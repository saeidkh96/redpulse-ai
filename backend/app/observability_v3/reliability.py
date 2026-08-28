from __future__ import annotations
import time

class CircuitBreaker:
    def __init__(self, threshold: int = 3, reset_after: float = 30.0) -> None:
        self.threshold = threshold
        self.reset_after = reset_after
        self.failures = 0
        self.opened_at: float | None = None

    def allow(self) -> bool:
        if self.opened_at is None:
            return True
        if time.time() - self.opened_at >= self.reset_after:
            self.failures = 0
            self.opened_at = None
            return True
        return False

    def success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = time.time()
