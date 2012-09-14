# coding: utf-8

from django.test import TestCase

from dext.settings import settings

from game.heroes.bag import SLOTS
from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionInPlacePrototype, ActionRestPrototype, ActionTradingPrototype, ActionEquippingPrototype, ActionRegenerateEnergyPrototype
from game.artifacts.storage import ArtifactsDatabase
from game.prototypes import TimePrototype

from game.balance import constants as c, formulas as f

class InPlaceActionTest(TestCase):

    def setUp(self):
        settings.refresh()

        create_test_map()

        self.bundle = create_test_bundle('InPlaceActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.action_inplace = ActionInPlacePrototype.create(self.action_idl)
        self.hero = self.bundle.tests_get_hero()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_inplace.leader, True)
        test_bundle_save(self, self.bundle)


    def test_processed(self):
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)
        test_bundle_save(self, self.bundle)

    def test_regenerate_energy_action_create(self):
        self.hero.preferences.energy_regeneration_type = c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 3)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionRegenerateEnergyPrototype.TYPE)
        test_bundle_save(self, self.bundle)

    def test_regenerate_energy_action_not_create_for_sacrifice(self):
        self.hero.preferences.energy_regeneration_type = c.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)
        test_bundle_save(self, self.bundle)

    def test_heal_action_create(self):
        self.hero.health = 1
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 3)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionRestPrototype.TYPE)
        test_bundle_save(self, self.bundle)

    def test_trade_action_create(self):
        storage = ArtifactsDatabase.storage()

        for i in xrange(int(c.MAX_BAG_SIZE * c.BAG_SIZE_TO_SELL_LOOT_FRACTION) + 1):
            artifact = storage.generate_artifact_from_list(storage.loot_ids, 1)
            self.hero.bag.put_artifact(artifact)

        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 3)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionTradingPrototype.TYPE)

        test_bundle_save(self, self.bundle)

    def test_equip_action_create(self):
        storage = ArtifactsDatabase.storage()

        artifact = storage.generate_artifact_from_list(storage.artifacts_ids, 1)
        artifact.power = 666
        self.hero.bag.put_artifact(artifact)

        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 3)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionEquippingPrototype.TYPE)

        test_bundle_save(self, self.bundle)

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        while len(self.bundle.actions) != 1:
            self.bundle.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)

        test_bundle_save(self, self.bundle)


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

        self.hero.model.money = 1
        self.bundle.process_turn()
        self.assertEqual(self.hero.money, 1)
        self.assertEqual(self.hero.statistics.money_spend, 0)
        test_bundle_save(self, self.bundle)


    def test_instant_heal(self):
        while self.hero.next_spending != c.ITEMS_OF_EXPENDITURE.INSTANT_HEAL:
            self.hero.switch_spending()

        money = f.instant_heal_price(self.hero.level)

        self.hero.model.money = money
        self.hero.health = 1
        self.bundle.process_turn()
        self.assertTrue(self.hero.money < f.instant_heal_price(self.hero.level) * c.PRICE_DELTA + 1)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_heal, money - self.hero.money)
        test_bundle_save(self, self.bundle)

    def test_bying_artifact_with_hero_preferences(self):
        while self.hero.next_spending != c.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT:
            self.hero.switch_spending()

        money = f.buy_artifact_price(self.hero.level)

        self.assertEqual(self.hero.statistics.money_spend, 0)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

        #unequip all arefact
        self.hero.equipment.test_remove_all()
        self.hero.preferences.equipment_slot = SLOTS.PLATE
        self.hero.save()

        #buy artifact
        self.hero.model.money = money

        self.bundle.process_turn()
        self.assertTrue(self.hero.money < f.buy_artifact_price(self.hero.level) * c.PRICE_DELTA + 1)
        self.assertEqual(len(self.hero.bag.items()), 0)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, money - self.hero.money)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

        self.assertNotEqual(self.hero.equipment.get(SLOTS.PLATE), None)
        test_bundle_save(self, self.bundle)


    def test_bying_artifact_without_change(self):
        while self.hero.next_spending != c.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT:
            self.hero.switch_spending()

        money = f.buy_artifact_price(self.hero.level)

        self.assertEqual(self.hero.statistics.money_spend, 0)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

        #unequip all arefact
        self.hero.equipment.test_remove_all()
        self.hero.save()

        #buy artifact
        self.hero.model.money = money

        self.bundle.process_turn()
        self.assertTrue(self.hero.money < f.buy_artifact_price(self.hero.level) * c.PRICE_DELTA + 1)
        self.assertEqual(len(self.hero.bag.items()), 0)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, money - self.hero.money)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)
        test_bundle_save(self, self.bundle)

    def test_bying_artifact_with_change(self):
        while self.hero.next_spending != c.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT:
            self.hero.switch_spending()

        # fill all slots with artifacts
        self.hero.equipment.test_equip_in_all_slots(ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level))

        money = f.buy_artifact_price(self.hero.level)

        #buy artifact
        self.hero.model.money = money

        self.assertEqual(self.hero.statistics.money_spend, 0)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

        self.bundle.process_turn()
        self.assertTrue(self.hero.money > 0)
        self.assertEqual(len(self.hero.bag.items()), 0)

        self.assertTrue(self.hero.statistics.money_spend > money - self.hero.money)
        self.assertTrue(self.hero.statistics.money_spend_for_artifacts > money - self.hero.money)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)
        self.assertTrue(self.hero.statistics.money_earned_from_artifacts > 0)
        test_bundle_save(self, self.bundle)

    def test_sharpening_artifact(self):
        while self.hero.next_spending != c.ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT:
            self.hero.switch_spending()

        money = f.sharpening_artifact_price(self.hero.level)

        old_power = self.hero.power

        self.hero.model.money = money
        self.bundle.process_turn()
        self.assertTrue(self.hero.money < f.sharpening_artifact_price(self.hero.level) * c.PRICE_DELTA + 1)
        self.assertEqual(old_power + 1, self.hero.power)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_sharpening, money - self.hero.money)
        test_bundle_save(self, self.bundle)

    def test_sharpening_artifact_with_hero_preferences(self):
        while self.hero.next_spending != c.ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT:
            self.hero.switch_spending()

        self.hero.preferences.equipment_slot = SLOTS.PLATE
        self.hero.save()

        money = f.sharpening_artifact_price(self.hero.level)

        old_power = self.hero.power
        old_plate_power = self.hero.equipment.get(SLOTS.PLATE).power

        self.hero.model.money = money
        self.bundle.process_turn()
        self.assertTrue(self.hero.money < f.sharpening_artifact_price(self.hero.level) * c.PRICE_DELTA + 1)
        self.assertEqual(old_power + 1, self.hero.power)
        self.assertEqual(old_plate_power + 1, self.hero.equipment.get(SLOTS.PLATE).power)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_sharpening, money - self.hero.money)
        test_bundle_save(self, self.bundle)


    def test_useless(self):
        while self.hero.next_spending != c.ITEMS_OF_EXPENDITURE.USELESS:
            self.hero.switch_spending()

        money = f.useless_price(self.hero.level)
        self.hero.model.money = money
        self.bundle.process_turn()
        self.assertTrue(self.hero.money < f.useless_price(self.hero.level) * c.PRICE_DELTA + 1)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_useless, money - self.hero.money)
        test_bundle_save(self, self.bundle)


    def test_impact(self):
        while self.hero.next_spending != c.ITEMS_OF_EXPENDITURE.IMPACT:
            self.hero.switch_spending()

        money = f.impact_price(self.hero.level)
        self.hero.model.money = money
        self.bundle.process_turn()
        self.assertTrue(self.hero.money < f.impact_price(self.hero.level) * c.PRICE_DELTA + 1)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_impact, money - self.hero.money)
        test_bundle_save(self, self.bundle)
