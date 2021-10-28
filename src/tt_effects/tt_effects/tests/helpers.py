
import os
import random

from tt_web import log
from tt_web import s11n
from tt_web import utils
from tt_web.tests import helpers as web_helpers

from .. import service
from .. import objects
from .. import operations


TEST_LOGGER = log.ContextLogger()


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config(), loop=self.loop)

    async def clean_environment(self, app=None):
        await operations.clean_database()


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    config = utils.load_config(config_path)

    service_name = os.environ['TT_SERVICE']

    config['database']['name'] = service_name
    config['database']['user'] = service_name
    config['database']['password'] = service_name

    return config


def create_effect(uid, id=None):
    return objects.Effect(id=id,
                          attribute=random.randint(1, 100),
                          entity=random.randint(1, 100),
                          value='some.value.{}'.format(uid),
                          caption='effect caption {}'.format(uid),
                          data=s11n.to_json({'expired_at': 666, 'uid': uid}))
