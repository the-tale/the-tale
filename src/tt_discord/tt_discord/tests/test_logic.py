
import unittest

from aiohttp import test_utils

from .. import logic
from .. import objects
from .. import operations

from . import helpers


class NormalizeNicknameTests(unittest.TestCase):

    def test(self):
        self.assertEqual(logic.normalize_nickname(''), 'unknown player')

        self.assertEqual(logic.normalize_nickname('   my nick\tis   Tiendil\r'), 'my nick is Tiendil')

        self.assertEqual(logic.normalize_nickname('discordtag'), 'unknown player')
        self.assertEqual(logic.normalize_nickname('everyone'), 'unknown player')
        self.assertEqual(logic.normalize_nickname('here'), 'unknown player')

        self.assertEqual(logic.normalize_nickname('xxx@xxx#xxx:xxx``xxx```xxx'), 'xxx?xxx?xxx?xxx``xxx???xxx')
        self.assertEqual(logic.normalize_nickname('veryveryveryveryveryveryveryveryveryveryveryverylongnickname'),
                         'veryveryveryveryveryveryveryvery')


class RemoveAccountData(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_data(self):
        await helpers.create_accounts(game_ids=(666, 777, 888))

        unexisted_info = objects.AccountInfo(id=None,
                                             game_id=999,
                                             discord_id=None)

        await logic.remove_account_data(unexisted_info)

    @test_utils.unittest_run_loop
    async def test_has_data(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await helpers.force_bind(accounts_infos[1].id, discord_id=100500)
        await helpers.force_bind(accounts_infos[2].id, discord_id=100501)

        info = await operations.get_account_info_by_id(accounts_infos[1].id)

        with self.check_event_setupped(True):
            await logic.remove_account_data(info)

        new_info = await operations.get_account_info_by_id(accounts_infos[1].id)

        self.assertEqual(new_info, objects.AccountInfo(id=info.id,
                                                       game_id=None,
                                                       discord_id=100500))

        accounts_to_remove = await operations.get_orphan_discord_accounts()

        self.assertEqual(accounts_to_remove, [new_info])
