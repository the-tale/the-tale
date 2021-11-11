
import asyncio

from .. import exceptions


class Lock:
    __slots__ = ('_point', 'key', '_lock', 'timeout')

    def __init__(self, point, key, lock, timeout=None):
        self._point = point
        self._lock = lock

        self.key = key
        self.timeout = timeout

    async def acquire(self):
        try:
            await asyncio.wait_for(self._lock.acquire(), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise exceptions.SyncPointTimeoutError(key=self.key, timeout=self.timeout)

    def release(self):
        if not self._lock._waiters:
            del self._point._locks[self.key]

        self._lock.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.release()


class SyncPoint:
    __slots__ = ('_locks',)

    def __init__(self):
        self._locks = {}

    def lock(self, key, timeout=None):
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()

        return Lock(point=self, key=key, lock=self._locks[key], timeout=timeout)
