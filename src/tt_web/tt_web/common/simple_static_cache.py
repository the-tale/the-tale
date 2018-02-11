
import time
import asyncio


class BaseCache:
    __slots__ = ('_reset_time', '_value', '_sync_future', 'initialized')

    def __init__(self):
        self._reset_time = 0
        self._value = None
        self._sync_future = None
        self.initialized = False

    def live_time(self):
        raise NotImplementedError()

    async def get_value(self):

        # first requests for get_value always wait for complete of load_value first call
        if self._sync_future:
            await self._sync_future
            return self._value

        if not self.initialized:
            self._sync_future = asyncio.Future()

            self._value = await self.load_value()
            self._reset_time = time.time() + self.live_time()

            self.initialized = True
            self._sync_future.set_result(None)
            self._sync_future = None

            return self._value

        if self._reset_time < time.time():
            # set before value update to ensure that we make only one external request for value
            # other calls to get_value will receive old data for a moment
            self._reset_time = time.time() + self.live_time()
            self._value = await self.load_value()

            return self._value

        return self._value

    async def load_value(self):
        raise NotImplementedError()
        await None

    def soft_reset(self):
        self._reset_time = 0

    def hard_reset(self):
        self._reset_time = 0
        self._value = None
        self._sync_future = None
        self.initialized = False
