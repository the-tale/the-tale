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


        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', 1)

        self.account = AccountPrototype.get_by_id(account_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.heroes.values()[0]

        self.ability = ArenaPvP1x1.get_by_hero_id(self.hero.id)


    def test_(self):
        self.assertEqual(Battle1x1.objects.all().count(), 0)

        self.ability.use(self.storage, self.hero, None)

        self.assertEqual(Battle1x1.objects.all().count(), 1)

        battle = Battle1x1.objects.all()[0]
        self.assertEqual(battle.account.id, self.account.id)
        self.assertEqual(battle.enemy, None)
