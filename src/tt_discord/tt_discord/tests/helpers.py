import os
import contextlib

from tt_web import utils
from tt_web.common import event
from tt_web import postgresql as db
from tt_web.tests import helpers as web_helpers

from .. import conf
from .. import service
from .. import operations


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config())

    async def clean_environment(self, app=None):
        await operations.clean_database()

    @contextlib.contextmanager
    def check_event_setupped(self, setupped):
        event.get(conf.SYNC_EVENT_NAME).clear()
        yield
        self.assertEqual(event.get(conf.SYNC_EVENT_NAME).is_set(), setupped)


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


async def create_accounts(game_ids):
    accounts_infos = []

    for game_id in game_ids:
        account_info = await operations.create_account(game_id=game_id)
        accounts_infos.append(account_info)

    return accounts_infos


async def force_bind(account_id, discord_id):
    await db.sql('UPDATE accounts SET discord_id=%(discord_id)s WHERE id=%(account_id)s',
                 {'account_id': account_id,
                  'discord_id': discord_id})
