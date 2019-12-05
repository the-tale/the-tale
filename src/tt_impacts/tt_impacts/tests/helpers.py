
import os
import uuid
import random
import datetime

from tt_web import utils
from tt_web.tests import helpers as web_helpers

from .. import objects
from .. import service
from .. import operations


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config())

    async def clean_environment(self, app=None):
        await operations.clean_database()


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


def test_impact(transaction=None, actor_type=None, actor_id=None, target_type=None, target_id=None, amount=None, turn=None):
    return objects.Impact(transaction=transaction if transaction is not None else uuid.uuid4(),
                          actor=objects.Object(actor_type if actor_type is not None else random.randint(0, 100),
                                               actor_id if actor_id is not None else random.randint(0, 10000)),
                          target=objects.Object(target_type if target_type is not None else random.randint(0, 100),
                                                target_id if target_id is not None else random.randint(0, 10000)),
                          amount=amount if amount is not None else random.randint(-100000000, 100000000),
                          turn=turn if turn is not None else random.randint(0, 10000),
                          time=datetime.datetime.now())
