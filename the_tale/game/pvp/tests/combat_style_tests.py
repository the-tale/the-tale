# coding: utf-8
import random

from django.test import TestCase

from dext.settings import settings

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.pvp.combat_styles import COMBAT_STYLES
from game.pvp.exceptions import PvPException

class CombatStyleTests(TestCase):

    def setUp(self):
        settings.refresh()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.combat_style = random.choice(COMBAT_STYLES.values())

    def test_hero_has_resources_no_resources(self):
        self.assertFalse(self.combat_style.hero_has_resources(self.hero_1))

    def test_hero_has_resources(self):
        self.hero_1.pvp_rage = self.combat_style.cost_rage
        self.hero_1.pvp_initiative = self.combat_style.cost_initiative + 1
        self.hero_1.pvp_concentration = self.combat_style.cost_concentration + 2
        self.assertTrue(self.combat_style.hero_has_resources(self.hero_1))

    def test_apply_to_hero_exception(self):
        self.assertRaises(PvPException, self.combat_style.apply_to_hero, self.hero_1, self.hero_2)

    def test_apply_to_hero(self):
        self.assertEqual(self.hero_1.pvp_combat_style, None)

        self.hero_1.pvp_rage = self.combat_style.cost_rage
        self.hero_1.pvp_initiative = self.combat_style.cost_initiative + 1
        self.hero_1.pvp_concentration = self.combat_style.cost_concentration + 2

        self.combat_style.apply_to_hero(self.hero_1, self.hero_2)

        self.assertEqual(self.hero_1.pvp_rage, 0)
        self.assertEqual(self.hero_1.pvp_initiative, 1)
        self.assertEqual(self.hero_1.pvp_concentration, 2)

        self.assertEqual(self.hero_1.pvp_power, self.combat_style.power)
        self.assertEqual(self.hero_1.pvp_power_modified, self.combat_style.power)

        self.assertEqual(self.hero_1.pvp_combat_style, self.combat_style.type)
