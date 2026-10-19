"""
Centralna konfiguracja asystenta.

Wszystkie ustawienia zależne od komputera i dane dostępowe są czytane
ze zmiennych środowiskowych (plik .env). Wzór: .env.example
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
VOICES_DIR = BASE_DIR / "voices"


def _path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    return Path(value).expanduser() if value else default


# --- Rozpoznawanie mowy (Vosk) ---
VOSK_MODEL_PATH = _path("VOSK_MODEL_PATH", BASE_DIR / "models" / "vosk-model-small-pl-0.22")
WAKE_WORD = os.getenv("WAKE_WORD", "kaszel")
_mic = os.getenv("MIC_DEVICE_INDEX", "").strip()
MIC_DEVICE_INDEX = int(_mic) if _mic else None  # None = domyślny mikrofon systemu

# --- Model językowy (Ollama) ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "asystent")

# --- Synteza mowy (Coqui XTTS v2) ---
VOICE_FILE = os.getenv("VOICE_FILE", "default.wav")

# --- Spotify (opcjonalnie) ---
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
SPOTIFY_CACHE_PATH = BASE_DIR / ".spotify_cache"

# --- Foldery robocze ---
PROJECTS_DIR = _path("PROJECTS_DIR", Path.home() / "Projects")
NOTES_DIR = _path("NOTES_DIR", BASE_DIR / "notes")
SCREENSHOTS_DIR = _path("SCREENSHOTS_DIR", BASE_DIR / "screenshots")

# --- Pliki danych ---
COMMANDS_FILE = DATA_DIR / "commands.json"
APP_SETS_FILE = DATA_DIR / "app_sets.json"
GAMES_FILE = DATA_DIR / "games.json"
PROJECTS_DB = DATA_DIR / "projects.json"        # tworzony automatycznie
CHAT_HISTORY_FILE = DATA_DIR / "chat_history.json"  # tworzony automatycznie
