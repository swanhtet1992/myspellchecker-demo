"""Simple in-memory sliding window rate limiter."""

from __future__ import annotations

import time
from collections import defaultdict, deque

_requests: dict[int, deque[float]] = defaultdict(deque)
MAX_PER_MINUTE = 20


def check_rate_limit(user_id: int) -> bool:
    """Return True if the user is within rate limits, False otherwise."""
    now = time.time()
    q = _requests[user_id]
    while q and q[0] < now - 60:
        q.popleft()
    if len(q) >= MAX_PER_MINUTE:
        return False
    q.append(now)
    return True
