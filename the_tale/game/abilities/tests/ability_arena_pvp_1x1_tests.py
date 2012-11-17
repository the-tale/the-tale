# coding: utf-8

from django.test import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user
from game.logic_storage import LogicStorage


from game.logic import create_test_map
from game.abilities.deck.arena_pvp_1x1 import ArenaPvP1x1
from game.pvp.models import Battle1x1

class ArenaPvP1x1AbilityTest(TestCase):

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()


        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.ability_1 = ArenaPvP1x1.get_by_hero_id(self.hero_1.id)
        self.ability_2 = ArenaPvP1x1.get_by_hero_id(self.hero_2.id)


    def test_use(self):
        self.assertEqual(Battle1x1.objects.all().count(), 0)

        self.assertTrue(self.ability_1.use(self.storage, self.hero_1, None))

        self.assertEqual(Battle1x1.objects.all().count(), 1)

        battle = Battle1x1.objects.all()[0]
        self.assertEqual(battle.account.id, self.account_1.id)
        self.assertEqual(battle.enemy, None)


    def test_use_for_fast_account(self):
        self.assertEqual(Battle1x1.objects.all().count(), 0)

        self.assertFalse(self.ability_2.use(self.storage, self.hero_2, None))

        self.assertEqual(Battle1x1.objects.all().count(), 0)
