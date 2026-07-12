"""Récupération de médias depuis un site de streaming (yt-dlp), sans IHM.

Version « classe » du script Zenity, pensée pour une application web Forge :
headless (aucune boîte de dialogue), utilisable depuis un worker de job
(forge-mvc-jobs) ou une commande, et branchable sur ingest_video / ingest_audio.

À placer dans `mvc/services/` de VOTRE application (pas dans le squelette Forge) :
yt-dlp est une dépendance de l'application, pas du framework.

Dépendances applicatives : yt-dlp et ffmpeg installés (yt-dlp résolu depuis le
PATH par défaut).

Sécurité (à ne pas retirer) :
  - allowlist de domaines : seuls les hôtes déclarés sont acceptés (défense SSRF
    et clarté « sites pris en charge ») ;
  - URL passée en ARGUMENT à yt-dlp (jamais un shell) : pas d'injection ;
  - timeout et taille maximale bornés.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from shutil import which
from urllib.parse import urlparse


class MediaFetchError(Exception):
    """Récupération refusée ou échouée (URL non autorisée, yt-dlp en erreur…)."""


@dataclass(frozen=True)
class MediaFetcherConfig:
    """Configuration de la récupération. `allowed_hosts` est obligatoire."""

    download_dir: Path
    allowed_hosts: frozenset[str]
    ytdlp_path: str = field(default_factory=lambda: which("yt-dlp") or "yt-dlp")
    max_bytes: int = 500 * 1024 * 1024  # 500 Mio
    timeout_s: int = 600  # 10 minutes


@dataclass(frozen=True)
class VideoQuality:
    """Une résolution disponible (pour proposer un choix à l'utilisateur)."""

    height: int
    label: str


# Extensions produites qu'on ne considère PAS comme le média final.
_TEMP_SUFFIXES = {".part", ".ytdl", ".temp"}


class MediaFetcher:
    """Récupère l'audio (MP3) ou la vidéo (MP4) d'une URL de streaming autorisée."""

    def __init__(self, config: MediaFetcherConfig) -> None:
        if not config.allowed_hosts:
            raise MediaFetchError(
                "allowed_hosts est vide : refuser tout par défaut (anti-SSRF)."
            )
        self._config = config
        config.download_dir.mkdir(parents=True, exist_ok=True)

    # ── Sécurité ────────────────────────────────────────────────────────────

    def is_allowed(self, url: str) -> bool:
        """Vrai si l'hôte de l'URL est dans l'allowlist (ou un sous-domaine)."""
        try:
            host = (urlparse(url).hostname or "").lower()
        except ValueError:
            return False
        if not host:
            return False
        return any(
            host == allowed or host.endswith("." + allowed)
            for allowed in self._config.allowed_hosts
        )

    def _guard(self, url: str) -> None:
        if not url or not url.lower().startswith(("http://", "https://")):
            raise MediaFetchError("URL invalide.")
        if not self.is_allowed(url):
            raise MediaFetchError(
                "Domaine non autorisé. Sites pris en charge : "
                + ", ".join(sorted(self._config.allowed_hosts))
            )

    # ── Analyse des qualités ────────────────────────────────────────────────

    def list_video_qualities(self, url: str) -> list[VideoQuality]:
        """Résolutions vidéo disponibles, de la plus haute à la plus basse."""
        self._guard(url)
        completed = self._run(["--no-playlist", "--dump-single-json", url])
        try:
            data = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise MediaFetchError(f"Analyse impossible : {exc}") from exc

        by_height: dict[int, dict[str, object]] = {}
        for fmt in data.get("formats", []):
            vcodec = fmt.get("vcodec")
            height = fmt.get("height")
            if not vcodec or vcodec == "none":
                continue
            if not isinstance(height, int) or height <= 0:
                continue
            info = by_height.setdefault(height, {"fps": 0.0, "hdr": False, "size": 0})
            fps = fmt.get("fps")
            if isinstance(fps, (int, float)):
                info["fps"] = max(float(info["fps"]), float(fps))  # type: ignore[arg-type]
            hdr = fmt.get("dynamic_range")
            if hdr and hdr != "SDR":
                info["hdr"] = True
            size = fmt.get("filesize") or fmt.get("filesize_approx")
            if isinstance(size, (int, float)) and size > 0:
                info["size"] = max(int(info["size"]), int(size))  # type: ignore[arg-type]

        qualities: list[VideoQuality] = []
        for height in sorted(by_height, reverse=True):
            info = by_height[height]
            label = f"{height}p"
            if float(info["fps"]) >= 50:  # type: ignore[arg-type]
                label += f" | {round(float(info['fps']))} images/s"  # type: ignore[arg-type]
            if info["hdr"]:
                label += " | HDR"
            if int(info["size"]):  # type: ignore[arg-type]
                label += f" | ~{self._human_size(int(info['size']))}"  # type: ignore[arg-type]
            qualities.append(VideoQuality(height=height, label=label))
        return qualities

    # ── Récupération ────────────────────────────────────────────────────────

    def fetch_audio(self, url: str) -> Path:
        """Télécharge le meilleur son, converti en MP3 (métadonnées + pochette)."""
        self._guard(url)
        return self._download([
            "--no-playlist",
            "--format", "bestaudio/best",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--embed-metadata",
            "--embed-thumbnail",
            "--convert-thumbnails", "jpg",
        ], url)

    def fetch_video(self, url: str, max_height: int) -> Path:
        """Télécharge la vidéo (avec son) jusqu'à `max_height`, remux MP4."""
        self._guard(url)
        if not isinstance(max_height, int) or max_height <= 0:
            raise MediaFetchError("Résolution demandée invalide.")
        selector = (
            f"bestvideo*[height<={max_height}]+bestaudio/best[height<={max_height}]"
        )
        return self._download([
            "--no-playlist",
            "--format", selector,
            "--merge-output-format", "mp4",
            "--remux-video", "mp4",
            "--embed-metadata",
            "--embed-thumbnail",
            "--convert-thumbnails", "jpg",
        ], url)

    # ── Interne ─────────────────────────────────────────────────────────────

    def _download(self, options: list[str], url: str) -> Path:
        """Télécharge dans un dossier temporaire dédié et renvoie le fichier produit."""
        workdir = Path(tempfile.mkdtemp(dir=self._config.download_dir))
        output = str(workdir / "%(title)s [%(id)s].%(ext)s")
        self._run(
            options
            + [
                "--windows-filenames",
                "--max-filesize", str(self._config.max_bytes),
                "--no-progress",
                "--output", output,
                url,
            ]
        )
        produced = [
            path
            for path in workdir.iterdir()
            if path.is_file() and path.suffix.lower() not in _TEMP_SUFFIXES
        ]
        if not produced:
            raise MediaFetchError("Aucun fichier produit (média vide ou trop volumineux).")
        media = max(produced, key=lambda p: p.stat().st_size)
        if media.stat().st_size > self._config.max_bytes:
            media.unlink(missing_ok=True)
            raise MediaFetchError("Fichier trop volumineux.")
        return media

    def _run(self, args: list[str]) -> "subprocess.CompletedProcess[str]":
        """Exécute yt-dlp SANS shell (URL en argument), avec timeout."""
        try:
            completed = subprocess.run(
                [self._config.ytdlp_path, *args],
                capture_output=True,
                text=True,
                timeout=self._config.timeout_s,
                check=False,
            )
        except FileNotFoundError as exc:
            raise MediaFetchError(f"yt-dlp introuvable : {self._config.ytdlp_path}") from exc
        except subprocess.TimeoutExpired as exc:
            raise MediaFetchError("Délai dépassé pendant la récupération.") from exc
        if completed.returncode != 0:
            tail = "\n".join(completed.stderr.strip().splitlines()[-15:])
            raise MediaFetchError(f"yt-dlp a échoué :\n{tail}")
        return completed

    @staticmethod
    def _human_size(nb_bytes: int) -> str:
        mio = nb_bytes / (1024 * 1024)
        return f"{mio / 1024:.1f} Gio" if mio >= 1024 else f"{mio:.0f} Mio"
