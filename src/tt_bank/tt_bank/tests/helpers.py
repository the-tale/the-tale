
import os
import getpass

from tt_web import log
from tt_web import utils
from tt_web import postgresql as db
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

    service_user = getpass.getuser()

    config['database']['name'] = service_user
    config['database']['user'] = service_user
    config['database']['password'] = service_user

    return config


async def call_change_balance(account_id,
                              currency,
                              amount,
                              restrictions=objects.Restrictions()):

    await operations._change_balance(db.sql,
                                     account_id=account_id,
                                     currency=currency,
                                     amount=amount,
                                     restrictions=restrictions,
                                     logger=TEST_LOGGER)
