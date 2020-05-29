import os

from tt_web import utils
from tt_web.tests import helpers as web_helpers

from .. import service
from .. import objects
from .. import operations
from .. import relations


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config())

    async def clean_environment(self, app=None):
        await operations.clean_database()


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


def property(object_id, type, value, mode=relations.MODE.REPLACE):
    return objects.Property(object_id=object_id,
                            type=type,
                            value=value,
                            mode=mode)
