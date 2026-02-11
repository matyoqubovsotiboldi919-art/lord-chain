import time

# key -> list[timestamps]
_BUCKETS: dict[str, list[int]] = {}

def allow(key: str, limit: int, window_seconds: int) -> bool:
    """
    Sliding window:
    - limit: nechta ruxsat
    - window_seconds: nechchi sekund ichida
    """
    now = int(time.time())
    arr = _BUCKETS.get(key, [])
    arr = [t for t in arr if now - t < window_seconds]
    if len(arr) >= limit:
        _BUCKETS[key] = arr
        return False
    arr.append(now)
    _BUCKETS[key] = arr
    return True
