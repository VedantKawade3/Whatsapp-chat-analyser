from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from config import CACHE_DIR

def make_cache_key(prefix: str, payload: str) -> str:
    raw = f"{prefix}::{payload}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"

def read_cache(key: str) -> Optional[dict[str, Any]]:
    path = cache_path(key)
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def write_cache(key: str, data: dict[str, Any]) -> None:
    path = cache_path(key)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")