# `media_fetcher` — récupération de médias (yt-dlp), headless

Récupère des médias depuis un site de streaming via **yt-dlp**, **sans IHM**. Version
« classe » d'un script Zenity, pensée pour une application web Forge : headless
(aucune boîte de dialogue), utilisable depuis un worker de job (`forge-mvc-jobs`) ou
une commande, et branchable sur des étapes d'ingestion (`ingest_video` /
`ingest_audio`).

> Service **applicatif**, pas du framework : `yt-dlp` et `ffmpeg` sont des dépendances
> de l'application (yt-dlp résolu depuis le `PATH` par défaut).

## API publique

| Symbole | Type | Rôle |
|---|---|---|
| `MediaFetcher` | classe | Orchestrateur : liste les qualités, télécharge audio/vidéo. |
| `MediaFetcherConfig` | dataclass | Configuration (dossier de sortie, hôtes autorisés, limites). |
| `VideoQuality` | dataclass | Une qualité vidéo disponible (`height`, `label`). |
| `MediaFetchError` | exception | Erreur de récupération (hôte refusé, échec yt-dlp, dépassement de taille…). |

### `MediaFetcherConfig`

| Champ | Type | Rôle |
|---|---|---|
| `download_dir` | `Path` | dossier de destination |
| `allowed_hosts` | `frozenset[str]` | **liste blanche** d'hôtes autorisés (sécurité) |
| `ytdlp_path` | `str` | chemin de `yt-dlp` (résolu du `PATH` par défaut) |
| `max_bytes` | `int` | taille maximale (défaut 500 Mio) |
| `timeout_s` | `int` | délai maximal (défaut 600 s) |

### `MediaFetcher`

| Méthode | Signature | Rôle |
|---|---|---|
| `is_allowed` | `(url: str) -> bool` | l'URL est-elle sous un hôte autorisé ? |
| `list_video_qualities` | `(url: str) -> list[VideoQuality]` | qualités vidéo disponibles |
| `fetch_audio` | `(url: str) -> Path` | télécharge la piste audio, renvoie le fichier |
| `fetch_video` | `(url: str, max_height: int) -> Path` | télécharge la vidéo (≤ `max_height`), renvoie le fichier |

## Usage

```python
from pathlib import Path
from mvc.services.media_fetcher import MediaFetcher, MediaFetcherConfig

fetcher = MediaFetcher(MediaFetcherConfig(
    download_dir=Path("var/media"),
    allowed_hosts=frozenset({"www.youtube.com", "youtu.be"}),
))
if fetcher.is_allowed(url):
    fichier = fetcher.fetch_audio(url)
```

**Sécurité** : toujours restreindre `allowed_hosts` (liste blanche) et conserver les
limites `max_bytes` / `timeout_s`. Le service ne rend aucune IHM : appelez-le depuis
un job ou une commande.

## Références

Candidat aux outils du **bac à sable pédagogique** (ticket 22) ; dépendances
applicatives : `yt-dlp`, `ffmpeg`.
