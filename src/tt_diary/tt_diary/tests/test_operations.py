
import time
import asyncio

from aiohttp import test_utils

from tt_web import utils

from tt_diary import objects
from tt_diary import operations

from . import helpers


class OperationsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_load_diary__not_exists(self):
        diaries_count = await operations.count_diaries()
        self.assertEqual(diaries_count, 0)

        diary = await operations.load_diary(1)
        self.assertEqual(diary, None)

        diaries_count = await operations.count_diaries()
        self.assertEqual(diaries_count, 0)


    @test_utils.unittest_run_loop
    async def test_load_diary__exists(self):
        saved_diary = objects.Diary()
        saved_diary.push_message(helpers.create_message('message 1'))
        saved_diary.push_message(helpers.create_message('message 2'))

        await operations.save_diary(1, saved_diary)

        diaries_count = await operations.count_diaries()
        self.assertEqual(diaries_count, 1)

        loaded_diary = await operations.load_diary(1)

        self.assertEqual(saved_diary, loaded_diary)


    @test_utils.unittest_run_loop
    async def test_save_diary__overwrite(self):
        saved_diary = objects.Diary()
        saved_diary.push_message(helpers.create_message('message 1'))
        saved_diary.push_message(helpers.create_message('message 2'))

        await operations.save_diary(1, saved_diary)

        saved_diary.push_message(helpers.create_message('message 3'))

        loaded_diary_1 = await operations.load_diary(1)

        await operations.save_diary(1, saved_diary)

        diaries_count = await operations.count_diaries()

        self.assertEqual(diaries_count, 1)

        loaded_diary_2 = await operations.load_diary(1)

        self.assertNotEqual(saved_diary, loaded_diary_1)
        self.assertEqual(saved_diary, loaded_diary_2)

        self.assertEqual(loaded_diary_1.version + 1, loaded_diary_2.version)



    @test_utils.unittest_run_loop
    async def test_push_message(self):
        saved_diary = objects.Diary()
        saved_diary.push_message(helpers.create_message(turn_number=1, message='message 1'))
        saved_diary.push_message(helpers.create_message(turn_number=2, message='message 2'))

        await operations.save_diary(1, saved_diary)

        await operations.push_message(1, helpers.create_message(turn_number=3, message='message 3'), diary_size=100)

        loaded_diary = await operations.load_diary(1)

        self.assertEqual(loaded_diary.version, 3)
        self.assertEqual(list(loaded_diary.messages())[-1].message, 'message 3')


    @test_utils.unittest_run_loop
    async def test_push_message__diary_sieze(self):

        for i in range(11):
            await operations.push_message(1, helpers.create_message(turn_number=i, message='message {}'.format(i)), diary_size=5)

        loaded_diary = await operations.load_diary(1)

        self.assertEqual(loaded_diary.version, 11)
        self.assertEqual(set(message.message for message in loaded_diary.messages()),
                         {'message 6', 'message 7', 'message 8', 'message 9', 'message 10'})



    @test_utils.unittest_run_loop
    async def test_timestamps_cache__filled_and_initialized(self):
        await operations.save_diary(3, objects.Diary())
        await operations.save_diary(1, objects.Diary())
        await operations.save_diary(2, objects.Diary())

        cache = operations.TIMESTAMPS_CACHE

        self.assertEqual(cache, {1: 0, 2: 0, 3: 0})

        cache.clear()

        self.assertEqual(cache, {})

        await operations.push_message(3, helpers.create_message(turn_number=3, message='message 3'), diary_size=100)
        await operations.push_message(1, helpers.create_message(turn_number=4, message='message 4'), diary_size=100)
        await operations.push_message(3, helpers.create_message(turn_number=5, message='message 5'), diary_size=100)

        self.assertEqual(cache, {1: 1, 3: 2})

        await operations.initialize_timestamps_cache()

        self.assertEqual(cache, {1: 1, 2: 0, 3: 2})
