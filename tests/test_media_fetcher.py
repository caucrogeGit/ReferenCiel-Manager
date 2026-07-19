# pyright: strict
"""Tests du service media_fetcher (yt-dlp mocké : aucun réseau, aucun binaire).

`MediaFetcher._run` est remplacé par des doublures (sous-classes) : on vérifie la
garde de sécurité (allowlist anti-SSRF, schémas d'URL), l'analyse des qualités
(parsing du JSON yt-dlp, fusion par hauteur, libellés) et la sélection du fichier
produit, sans dépendre de yt-dlp — donc exécutable en CI (ADR-006).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from mvc.services.media_fetcher import (
    MediaFetcher,
    MediaFetcherConfig,
    MediaFetchError,
)

_URL = "https://youtube.com/watch?v=exemple"


def _config(tmp_path: Path, *, max_bytes: int = 500 * 1024 * 1024) -> MediaFetcherConfig:
    return MediaFetcherConfig(
        download_dir=tmp_path,
        allowed_hosts=frozenset({"youtube.com"}),
        max_bytes=max_bytes,
    )


class _FetcherAnalyse(MediaFetcher):
    """`_run` renvoie un JSON figé sur stdout (simulateur de --dump-single-json)."""

    def __init__(self, config: MediaFetcherConfig, stdout: str) -> None:
        super().__init__(config)
        self._stdout = stdout

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=self._stdout, stderr="")


class _FetcherTelechargement(MediaFetcher):
    """`_run` simule yt-dlp : dépose `fichiers` (nom -> taille) dans le dossier de sortie."""

    def __init__(self, config: MediaFetcherConfig, fichiers: dict[str, int]) -> None:
        super().__init__(config)
        self._fichiers = fichiers

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        sortie = Path(args[args.index("--output") + 1]).parent
        for nom, taille in self._fichiers.items():
            (sortie / nom).write_bytes(b"x" * taille)
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")


# ── Sécurité (allowlist, schémas) ───────────────────────────────────────────


def test_allowlist_vide_refusee(tmp_path: Path) -> None:
    config = MediaFetcherConfig(download_dir=tmp_path, allowed_hosts=frozenset())
    with pytest.raises(MediaFetchError, match="allowed_hosts"):
        MediaFetcher(config)


def test_is_allowed_hote_exact_et_sous_domaine(tmp_path: Path) -> None:
    fetcher = MediaFetcher(_config(tmp_path))
    assert fetcher.is_allowed("https://youtube.com/watch?v=x")
    assert fetcher.is_allowed("https://www.youtube.com/watch?v=x")
    assert not fetcher.is_allowed("https://autresite.fr/video")
    # Un hôte qui *contient* le domaine autorisé sans en être un sous-domaine.
    assert not fetcher.is_allowed("https://fauxyoutube.com/video")
    assert not fetcher.is_allowed("pas-une-url")


def test_guard_refuse_schema_non_http(tmp_path: Path) -> None:
    fetcher = MediaFetcher(_config(tmp_path))
    with pytest.raises(MediaFetchError, match="URL invalide"):
        fetcher.list_video_qualities("ftp://youtube.com/video")


def test_guard_refuse_domaine_hors_allowlist(tmp_path: Path) -> None:
    fetcher = MediaFetcher(_config(tmp_path))
    with pytest.raises(MediaFetchError, match="Domaine non autorisé"):
        fetcher.list_video_qualities("https://autresite.fr/video")


# ── Analyse des qualités ────────────────────────────────────────────────────


def test_qualites_triees_avec_libelles(tmp_path: Path) -> None:
    payload = {
        "formats": [
            {"vcodec": "avc1", "height": 720, "fps": 30, "filesize": 500 * 1024 * 1024},
            {"vcodec": "vp9", "height": 1080, "fps": 60, "filesize": 2 * 1024 ** 3},
            {"vcodec": "av01", "height": 480, "dynamic_range": "HDR10"},
        ]
    }
    fetcher = _FetcherAnalyse(_config(tmp_path), json.dumps(payload))
    qualites = fetcher.list_video_qualities(_URL)
    assert [q.height for q in qualites] == [1080, 720, 480]
    assert qualites[0].label == "1080p | 60 images/s | ~2.0 Gio"
    assert qualites[1].label == "720p | ~500 Mio"  # fps < 50 : pas affiché
    assert qualites[2].label == "480p | HDR"


def test_qualites_fusionnees_par_hauteur(tmp_path: Path) -> None:
    """Deux formats de même hauteur : fps max, taille max, HDR si l'un l'est."""
    payload = {
        "formats": [
            {"vcodec": "avc1", "height": 1080, "fps": 30, "filesize": 100 * 1024 * 1024},
            {"vcodec": "vp9", "height": 1080, "fps": 60,
             "filesize_approx": 200 * 1024 * 1024, "dynamic_range": "HDR10"},
        ]
    }
    fetcher = _FetcherAnalyse(_config(tmp_path), json.dumps(payload))
    qualites = fetcher.list_video_qualities(_URL)
    assert len(qualites) == 1
    assert qualites[0].label == "1080p | 60 images/s | HDR | ~200 Mio"


def test_formats_invalides_ignores(tmp_path: Path) -> None:
    """Audio seul, hauteurs absentes/booléennes/négatives/textuelles : tous écartés."""
    payload = {
        "formats": [
            {"vcodec": "none", "height": 720},          # audio seul
            {"acodec": "opus"},                          # pas de vcodec
            {"vcodec": "avc1", "height": True},          # booléen (piège int)
            {"vcodec": "avc1", "height": "720"},         # chaîne
            {"vcodec": "avc1", "height": -1},            # négatif
            "pas-un-objet",                              # entrée non structurée
        ]
    }
    fetcher = _FetcherAnalyse(_config(tmp_path), json.dumps(payload))
    assert fetcher.list_video_qualities(_URL) == []


def test_json_illisible_leve_une_erreur(tmp_path: Path) -> None:
    fetcher = _FetcherAnalyse(_config(tmp_path), "pas du json")
    with pytest.raises(MediaFetchError, match="Analyse impossible"):
        fetcher.list_video_qualities(_URL)


# ── Récupération (sélection du fichier produit) ─────────────────────────────


def test_download_choisit_le_plus_gros_et_ignore_les_temporaires(tmp_path: Path) -> None:
    fichiers = {"petit.mp3": 10, "final.mp3": 100, "reste.part": 1000}
    fetcher = _FetcherTelechargement(_config(tmp_path), fichiers)
    media = fetcher.fetch_audio(_URL)
    assert media.name == "final.mp3"
    assert media.stat().st_size == 100


def test_download_sans_fichier_produit_leve_une_erreur(tmp_path: Path) -> None:
    fetcher = _FetcherTelechargement(_config(tmp_path), {})
    with pytest.raises(MediaFetchError, match="Aucun fichier produit"):
        fetcher.fetch_audio(_URL)


def test_download_trop_volumineux_supprime_et_leve(tmp_path: Path) -> None:
    fetcher = _FetcherTelechargement(_config(tmp_path, max_bytes=50), {"gros.mp3": 100})
    with pytest.raises(MediaFetchError, match="trop volumineux"):
        fetcher.fetch_audio(_URL)
    assert not list(tmp_path.rglob("gros.mp3"))  # le fichier fautif est supprimé


def test_fetch_video_hauteur_invalide(tmp_path: Path) -> None:
    fetcher = _FetcherTelechargement(_config(tmp_path), {"video.mp4": 10})
    with pytest.raises(MediaFetchError, match="Résolution demandée invalide"):
        fetcher.fetch_video(_URL, max_height=0)


# ── Exécution de yt-dlp (erreurs process) ───────────────────────────────────


def test_ytdlp_introuvable(tmp_path: Path) -> None:
    config = MediaFetcherConfig(
        download_dir=tmp_path,
        allowed_hosts=frozenset({"youtube.com"}),
        ytdlp_path=str(tmp_path / "inexistant" / "yt-dlp"),
    )
    with pytest.raises(MediaFetchError, match="introuvable"):
        MediaFetcher(config).list_video_qualities(_URL)


def test_ytdlp_en_echec_remonte_la_fin_de_stderr(tmp_path: Path) -> None:
    faux = tmp_path / "faux-yt-dlp"
    faux.write_text("#!/bin/sh\necho 'ERROR: video indisponible' >&2\nexit 3\n")
    faux.chmod(0o755)
    config = MediaFetcherConfig(
        download_dir=tmp_path,
        allowed_hosts=frozenset({"youtube.com"}),
        ytdlp_path=str(faux),
    )
    with pytest.raises(MediaFetchError, match="video indisponible"):
        MediaFetcher(config).list_video_qualities(_URL)
