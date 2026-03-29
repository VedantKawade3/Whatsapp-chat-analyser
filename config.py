from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

STOPWORDS_CANDIDATES = [
    BASE_DIR / "stop_hinglish.txt",
    BASE_DIR / "data" / "stop_hinglish.txt",
]

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_SAMPLE_MESSAGES = int(os.getenv("MAX_SAMPLE_MESSAGES", "120"))
MAX_SAMPLE_CHARS = int(os.getenv("MAX_SAMPLE_CHARS", "12000"))

def load_stop_words() -> set[str]:
    for path in STOPWORDS_CANDIDATES:
        if path.exists():
            try:
                return set(path.read_text(encoding="utf-8").split())
            except Exception:
                pass
    return set()