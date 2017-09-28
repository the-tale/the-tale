import os
import time
import uuid
import random

import asyncio

from aiohttp import test_utils

from tt_protocol.protocol import base_pb2
from tt_protocol.protocol import diary_pb2

from tt_web import utils
from tt_web import postgresql
from tt_web.tests import helpers as web_helpers

from tt_diary import objects
from tt_diary import service
from tt_diary import operations


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config(), loop=self.loop)

    async def clean_environment(self, app=None):
        operations.TIMESTAMPS_CACHE.clear()
        await operations.clean_diaries()


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


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
