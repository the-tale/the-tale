
import os

from tt_web import log
from tt_web import utils
from tt_web.tests import helpers as web_helpers

from .. import service
from .. import operations


TEST_LOGGER = log.ContextLogger()


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config())

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
