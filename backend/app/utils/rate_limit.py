"""Small in-memory protection for expensive API endpoints.

The limiter is deliberately process-local. Multi-worker production deployments
should also use an edge or shared-store limiter.
"""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class CostEndpointRateLimiter:
    def __init__(self, config):
        self.enabled = config.RATE_LIMIT_ENABLED
        self.window_seconds = config.RATE_LIMIT_WINDOW_SECONDS
        self.limits = {
            'search': config.RATE_LIMIT_SEARCH,
            'case': config.RATE_LIMIT_CASE,
            'simulation': config.RATE_LIMIT_SIMULATION,
            'documents': config.RATE_LIMIT_DOCUMENTS,
        }
        self._requests = defaultdict(deque)
        self._lock = Lock()

    @staticmethod
    def bucket_for_path(path: str):
        if path in {'/api/search', '/api/search/tasks'}:
            return 'search'
        if path in {'/api/case', '/api/case/tasks', '/api/novacourt/analyze'}:
            return 'case'
        if path.startswith('/api/simulation'):
            return 'simulation'
        if path.startswith('/api/cases/') and '/documents' in path:
            return 'documents'
        return None

    def check(self, client_ip: str, path: str):
        """Return (allowed, retry_after_seconds) for a request."""
        bucket = self.bucket_for_path(path)
        if not self.enabled or not bucket:
            return True, 0

        now = monotonic()
        key = (client_ip or 'unknown', bucket)
        with self._lock:
            timestamps = self._requests[key]
            cutoff = now - self.window_seconds
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            limit = self.limits[bucket]
            if len(timestamps) >= limit:
                retry_after = max(1, int(self.window_seconds - (now - timestamps[0])))
                return False, retry_after

            timestamps.append(now)
            return True, 0
