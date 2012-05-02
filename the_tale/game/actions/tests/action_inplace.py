# coding: utf-8

from django.test import TestCase

from game.game_info import ITEMS_OF_EXPENDITURE
from game.heroes.bag import ARTIFACT_TYPES_TO_SLOTS
from game.logic import create_test_bundle, create_test_map
from game.actions.prototypes import ActionInPlacePrototype, ActionRestPrototype, ActionTradingPrototype, ActionEquippingPrototype
from game.artifacts.storage import ArtifactsDatabase
from game.artifacts.conf import ITEM_TYPE

from game.balance import constants as c, formulas as f

class InPlaceActionTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('InPlaceActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.bundle.add_action(ActionInPlacePrototype.create(self.action_idl))
        self.action_inplace = self.bundle.tests_get_last_action()
        self.hero = self.bundle.tests_get_hero()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_inplace.leader, True)


    def test_processed(self):
        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)


    def test_heal_action_create(self):
        self.hero.health = 1
        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 3)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionRestPrototype.TYPE)

    def test_trade_action_create(self):
        storage = ArtifactsDatabase.storage()

        for i in xrange(int(c.MAX_BAG_SIZE * c.BAG_SIZE_TO_SELL_LOOT_FRACTION) + 1):
            artifact = storage.generate_artifact_from_list(storage.loot_ids, 1)
            self.hero.bag.put_artifact(artifact)

        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 3)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionTradingPrototype.TYPE)

    def test_equip_action_create(self):
        storage = ArtifactsDatabase.storage()

        artifact = storage.generate_artifact_from_list(storage.artifacts_ids, 1)
        artifact.power = 666
        self.hero.bag.put_artifact(artifact)

        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 3)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionEquippingPrototype.TYPE)


class InPlaceActionSpendMoneyTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('InPlaceActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.bundle.add_action(ActionInPlacePrototype.create(self.action_idl))
        self.action_inplace = self.bundle.tests_get_last_action()
        self.hero = self.bundle.tests_get_hero()


    def tearDown(self):
        pass


    def test_no_money(self):

        self.hero.money = 1
        self.bundle.process_turn(1)
        self.assertEqual(self.hero.money, 1)
        self.assertEqual(self.hero.statistics.money_spend, 0)


    def test_instant_heal(self):
        while self.hero.next_spending != ITEMS_OF_EXPENDITURE.INSTANT_HEAL:
            self.hero.switch_spending()

        money = f.instant_heal_price(self.hero.level)

        self.hero.money = money
        self.hero.health = 1
        self.bundle.process_turn(1)
        self.assertTrue(self.hero.money < f.instant_heal_price(self.hero.level) * c.PRICE_DELTA + 1)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_heal, money - self.hero.money)

    def test_bying_artifact(self):
        while self.hero.next_spending != ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT:
            self.hero.switch_spending()

        money = f.buy_artifact_price(self.hero.level)

        self.hero.money = money
        self.bundle.process_turn(1)
        self.assertTrue(self.hero.money < f.buy_artifact_price(self.hero.level) * c.PRICE_DELTA + 1)
        self.assertEqual(len(self.hero.bag.items()), 1)
        artifact_id, artifact = self.hero.bag.items()[0]
        self.assertNotEqual(artifact.type, ITEM_TYPE.USELESS)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, money - self.hero.money)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

    def test_sharpening_artifact(self):
        while self.hero.next_spending != ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT:
            self.hero.switch_spending()

        money = f.sharpening_artifact_price(self.hero.level)

        self.hero.money = money
        artifact = ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level)
        artifact_power = artifact.power
        equip_slot = ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type][0]
        self.hero.equipment.unequip(equip_slot)
        self.hero.equipment.equip(equip_slot, artifact)
        self.bundle.process_turn(1)
        self.assertTrue(self.hero.money < f.sharpening_artifact_price(self.hero.level) * c.PRICE_DELTA + 1)
        self.assertEqual(artifact_power + 1, self.hero.equipment.get(equip_slot).power)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_sharpening, money - self.hero.money)

    def test_useless(self):
        while self.hero.next_spending != ITEMS_OF_EXPENDITURE.USELESS:
            self.hero.switch_spending()

        money = f.useless_price(self.hero.level)
        self.hero.money = money
        self.bundle.process_turn(1)
        self.assertTrue(self.hero.money < f.useless_price(self.hero.level) * c.PRICE_DELTA + 1)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_useless, money - self.hero.money)


    def test_impact(self):
        while self.hero.next_spending != ITEMS_OF_EXPENDITURE.IMPACT:
            self.hero.switch_spending()

        money = f.impact_price(self.hero.level)
        self.hero.money = money
        self.bundle.process_turn(1)
        self.assertTrue(self.hero.money < f.impact_price(self.hero.level) * c.PRICE_DELTA + 1)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_impact, money - self.hero.money)
