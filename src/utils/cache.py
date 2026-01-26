import json
import time
from pathlib import Path
from typing import Any

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_path(key: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in key)
    return CACHE_DIR / f"{safe}.json"

def cache_get(key: str, ttl_seconds: int) -> Any | None:
    path = _cache_path(key)
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        ts = payload.get("ts")
        if ts is None:
            return None

        if (time.time() - ts) > ttl_seconds:
            return None

        return payload.get("data")
    except Exception:
        return None

def cache_set(key: str, data: Any) -> None:
    path = _cache_path(key)
    payload = {"ts": time.time(), "data": data}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
