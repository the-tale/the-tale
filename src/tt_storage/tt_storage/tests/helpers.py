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

from .. import objects
from .. import service
from .. import operations


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config(), loop=self.loop)

    async def clean_environment(self, app=None):
        await operations.clean_database()


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)
