import os

from tt_web import utils
from tt_web.tests import helpers as web_helpers

from .. import logic
from .. import service
from .. import operations


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config())

    async def clean_environment(self, app=None):
        await operations.clean_database()
        await logic.clear_plugins()


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


def report_livetime():
    return get_config()['custom']['report_livetime']
