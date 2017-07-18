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

from .. import objects
from .. import service
from .. import operations


class BaseTests(test_utils.AioHTTPTestCase):

    def setUp(self):
        super().setUp()
        asyncio.set_event_loop(self.loop)


    def get_app(self, loop):
        application = service.create_application(get_config(), loop=loop)

        application.on_startup.append(clean)
        application.on_cleanup.insert(0, clean)

        return application


    async def check_answer(self, request, Data=None, api_status=base_pb2.ApiResponse.SUCCESS):
        self.assertEqual(request.status, 200)
        content = await request.content.read()
        response = base_pb2.ApiResponse.FromString(content)
        self.assertEqual(response.status, api_status)

        if Data is None:
            return None

        response_data = Data()
        response.data.Unpack(response_data)

        await request.release()

        return response_data


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


async def initialize_services():
    config = get_config()
    await postgresql.initialize(config['database'])


async def deinitialize_services():
    await postgresql.deinitialize()


async def clean(app=None):
    await operations.clean_database()
