
import time
import asyncio
import random

from aiohttp import test_utils

from tt_diary import utils
from tt_diary import exceptions
from tt_diary import service

from . import helpers


POINT = utils.SyncPoint()


class SyncPointTests(helpers.BaseTests):

    def test_empty(self):
        self.assertEqual(POINT._locks, {})


    @test_utils.unittest_run_loop
    async def test_sigle(self):

        async with POINT.lock('key_1') as locker:
            self.assertEqual(locker._point, POINT)
            self.assertNotEqual(locker._lock, None)
            self.assertEqual(locker.key, 'key_1')
            self.assertEqual(locker.timeout, None)
            self.assertEqual(locker.loop, None)

            self.assertEqual(set(POINT._locks), {'key_1',})

        self.test_empty()


    @test_utils.unittest_run_loop
    async def test_nested(self):

        async with POINT.lock('key_1') as locker_1:

            async with POINT.lock('key_2') as locker_2:

                self.assertEqual(locker_1.key, 'key_1')
                self.assertEqual(locker_2.key, 'key_2')

                self.assertEqual(set(POINT._locks), {'key_1', 'key_2'})
                self.assertTrue(locker_1._point is locker_2._point)

            self.assertEqual(locker_1.key, 'key_1')
            self.assertEqual(set(POINT._locks), {'key_1',})

        self.test_empty()


    @test_utils.unittest_run_loop
    async def test_dublicate(self):

        async def operation_1():

            async with POINT.lock('key_1') as locker:
                self.assertEqual(locker.key, 'key_1')
                self.assertEqual(set(POINT._locks), {'key_1',})

                await asyncio.sleep(0.25)

                self.assertEqual(set(POINT._locks), {'key_1',})

            self.assertEqual(set(POINT._locks), {'key_1',})


        async def operation_2():

            await asyncio.sleep(0.05) # ensuher that operation_1 take lock first

            async with POINT.lock('key_1') as locker:
                self.assertEqual(locker.key, 'key_1')
                self.assertEqual(set(POINT._locks), {'key_1',})

            self.test_empty()

        task_1 = operation_1()
        task_2 = operation_2()

        await asyncio.gather(task_1, task_2)

        self.test_empty()


    @test_utils.unittest_run_loop
    async def test_timeout(self):

        async def operation_1():

            async with POINT.lock('key_1') as locker:

                self.assertEqual(locker.key, 'key_1')
                self.assertEqual(set(POINT._locks), {'key_1',})

                await asyncio.sleep(0.3)

                self.assertEqual(set(POINT._locks), {'key_1',})


        async def operation_2():

            await asyncio.sleep(0.05) # ensuher that operation_1 take lock first

            async with POINT.lock('key_1', timeout=0.1) as locker:

                self.assertEqual(locker.key, 'key_1')
                self.assertEqual(set(POINT._locks), {'key_1',})

            self.test_empty()


        task_1 = asyncio.ensure_future(operation_1())
        task_2 = asyncio.ensure_future(operation_2())

        await asyncio.wait((task_1, task_2))

        self.assertEqual(task_1.exception(), None)
        self.assertTrue(isinstance(task_2.exception(), exceptions.SyncPointTimeoutError))

        self.test_empty()


    @test_utils.unittest_run_loop
    async def test_ordering(self):

        values = []

        async def call(value):
            async with POINT.lock('key'):
                values.append((value, 1))
                await asyncio.sleep(0.25)
                values.append((value, 2))

        tasks = [asyncio.ensure_future(call('a')),
                 asyncio.ensure_future(call('b')),
                 asyncio.ensure_future(call('c')),
                 asyncio.ensure_future(call('d'))]

        random.shuffle(tasks)

        await asyncio.wait(tasks)

        self.assertEqual(values,
                         [('a', 1), ('a', 2),
                          ('b', 1), ('b', 2),
                          ('c', 1), ('c', 2),
                          ('d', 1), ('d', 2)])
