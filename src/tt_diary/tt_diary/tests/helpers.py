import os
import time
import uuid
import random

import asyncio

from aiohttp import test_utils

from tt_protocol.protocol import base_pb2
from tt_protocol.protocol import diary_pb2

from tt_diary import utils
from tt_diary import objects
from tt_diary import service
from tt_diary import postgresql
from tt_diary import operations


class BaseTests(test_utils.AioHTTPTestCase):

    def setUp(self):
        super().setUp()
        asyncio.set_event_loop(self.loop)


    def get_app(self, loop):
        application = service.create_application(get_config(), loop=loop)

        application.on_startup.append(clean)
        application.on_cleanup.insert(0, clean)

        return application


    async def check_answer(self, request, Data=None):
        self.assertEqual(request.status, 200)
        content = await request.content.read()
        response = base_pb2.ApiResponse.FromString(content)
        self.assertEqual(response.status, base_pb2.ApiResponse.SUCCESS)

        if Data is None:
            return None

        response_data = Data()
        response.data.Unpack(response_data)

        await request.release()

        return response_data



def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper



def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


async def initialize_services():
    config = get_config()
    await postgresql.initialize(config['database'])


async def deinitialize_services():
    await postgresql.deinitialize()


async def clean(app=None):
    operations.TIMESTAMPS_CACHE.clear()
    await operations.clean_diaries()


def create_message(message=None, turn_number=None, timestamp=None):

    if turn_number is None:
        turn_number = random.randint(1, 1000)

    if timestamp is None:
        timestamp = time.time()

    return objects.Message(timestamp=timestamp,
                           turn_number=turn_number,
                           type=random.randint(1, 100),
                           game_time='game time {}'.format(turn_number),
                           game_date='game date {}'.format(turn_number),
                           position='position {}'.format(turn_number),
                           message=message if message else 'message {}'.format(uuid.uuid4().hex),
                           variables={'x': 'y', 'z': 1})
