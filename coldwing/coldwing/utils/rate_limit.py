from __future__ import annotations

import time


class RateLimiter:
    def __init__(self, per_second: float = 5.0) -> None:
        if per_second <= 0:
            raise ValueError("per_second must be > 0")
        self.per_second = per_second
        self._last = 0.0

    def wait(self) -> None:
        min_interval = 1.0 / self.per_second
        now = time.monotonic()
        delta = now - self._last
        if delta < min_interval:
            time.sleep(min_interval - delta)
        self._last = time.monotonic()
