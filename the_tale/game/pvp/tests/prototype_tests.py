# coding: utf-8

import mock

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from game.pvp.models import Battle1x1, BATTLE_1X1_STATE
from game.pvp.prototypes import Battle1x1Prototype



class PrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()

        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        result, account_3_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)
        self.account_3 = AccountPrototype.get_by_id(account_3_id)

    def test_remove_unprocessed_battles(self):
        Battle1x1Prototype.create(self.account_1)
        battle_2 = Battle1x1Prototype.create(self.account_2)
        battle_3 = Battle1x1Prototype.create(self.account_3)

        self.assertEqual(Battle1x1.objects.all().count(), 3)
        Battle1x1Prototype.remove_unprocessed_battles()
        self.assertEqual(Battle1x1.objects.all().count(), 3)

        battle_2.state = BATTLE_1X1_STATE.PROCESSED
        battle_2.save()

        battle_3.state = BATTLE_1X1_STATE.ENEMY_NOT_FOND
        battle_3.save()

        Battle1x1Prototype.remove_unprocessed_battles()
        self.assertEqual(Battle1x1.objects.all().count(), 3)

        with mock.patch('game.pvp.conf.pvp_settings.UNPROCESSED_LIVE_TIME', -1):
            Battle1x1Prototype.remove_unprocessed_battles()

        self.assertEqual(Battle1x1.objects.all().count(), 2)
