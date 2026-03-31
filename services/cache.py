import json
import os
from typing import Any

import redis

CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/2")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "120"))

_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis.from_url(CACHE_REDIS_URL, decode_responses=True)
    return _client


def get_json(key: str) -> Any | None:
    try:
        raw = _get_client().get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None


def set_json(key: str, value: Any, ttl_seconds: int = CACHE_TTL_SECONDS) -> None:
    try:
        _get_client().setex(key, ttl_seconds, json.dumps(value))
    except Exception:
        return


def delete_key(key: str) -> None:
    try:
        _get_client().delete(key)
    except Exception:
        return
