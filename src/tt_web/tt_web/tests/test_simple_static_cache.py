import time
import asyncio
import collections

from aiohttp import test_utils

from . import helpers

from ..common import simple_static_cache


LIVE_TIME = 1.0
DELAY_TIME = 0.5


class Cache(simple_static_cache.BaseCache):

    def __init__(self, values):
        self.values = list(values)
        super(Cache, self).__init__()

    def live_time(self):
        return LIVE_TIME

    async def load_value(self):
        await asyncio.sleep(DELAY_TIME)

        value = self.values.pop(0)
        self.values.append(value)

        return value


class CacheTests(helpers.BaseTests):

    def test_initialize(self):
        self.assertTrue(DELAY_TIME < LIVE_TIME)

        cache = Cache([1, 2, 3])

        self.assertEqual(cache._reset_time, 0)
        self.assertEqual(cache._value, None)
        self.assertEqual(cache._sync_future, None)
        self.assertFalse(cache.initialized)


    @test_utils.unittest_run_loop
    async def test_single_requester(self):
        cache = Cache([1, 2, 3])

        self.assertFalse(cache.initialized)

        value = await cache.get_value()
        self.assertEqual(value, 1)


        self.assertTrue(cache.initialized)

        self.assertTrue(time.time() < cache._reset_time)

        await asyncio.sleep(LIVE_TIME + 0.1)

        value = await cache.get_value()
        self.assertEqual(value, 2)


    @test_utils.unittest_run_loop
    async def test_multiple_requesters(self):
        cache = Cache([1, 2, 3])

        self.assertFalse(cache.initialized)

        results = await asyncio.gather(cache.get_value(), cache.get_value(), cache.get_value())
        self.assertEqual(collections.Counter(results), {1: 3})  # all requests wait for value
        self.assertTrue(time.time() < cache._reset_time)

        self.assertTrue(cache.initialized)

        await asyncio.sleep(LIVE_TIME)

        results = await asyncio.gather(cache.get_value(), cache.get_value(), cache.get_value())
        self.assertEqual(collections.Counter(results), {1: 2, 2: 1})
        self.assertTrue(time.time() < cache._reset_time)


    @test_utils.unittest_run_loop
    async def test_soft_reset(self):
        cache = Cache([1, 2, 3])

        value = await cache.get_value()
        self.assertEqual(value, 1)

        cache.soft_reset()

        self.assertEqual(cache._reset_time, 0)

        # without sleep

        value = await cache.get_value()
        self.assertEqual(value, 2)
