import os
import threading
import time
import uuid as _uuid


_last_timestamp_ms = 0
_lock = threading.Lock()


def uuid7():
    """Return a time-ordered UUIDv7 value."""
    global _last_timestamp_ms

    timestamp_ms = time.time_ns() // 1_000_000
    with _lock:
        if timestamp_ms <= _last_timestamp_ms:
            timestamp_ms = _last_timestamp_ms + 1
        _last_timestamp_ms = timestamp_ms

    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & ((1 << 62) - 1)

    value = (
        ((timestamp_ms & ((1 << 48) - 1)) << 80)
        | (7 << 76)
        | (rand_a << 64)
        | (0b10 << 62)
        | rand_b
    )
    return _uuid.UUID(int=value)
