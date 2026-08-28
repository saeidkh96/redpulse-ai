from __future__ import annotations
import time
from typing import Callable, TypeVar
T = TypeVar("T")

def retry(fn: Callable[[], T], attempts: int = 3, delay_seconds: float = 0.05) -> T:
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(delay_seconds)
    raise last
