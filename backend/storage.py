import time
from typing import Optional

_store: dict = {}
_TTL = 3600


def store_result(result_id: str, data: dict):
    _store[result_id] = {"data": data, "ts": time.time()}


def get_result(result_id: str) -> Optional[dict]:
    entry = _store.get(result_id)
    if not entry:
        return None
    if time.time() - entry["ts"] > _TTL:
        del _store[result_id]
        return None
    return entry["data"]
