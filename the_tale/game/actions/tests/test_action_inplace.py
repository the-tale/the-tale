# coding: utf-8
import contextlib

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.relations import EQUIPMENT_SLOT
from the_tale.game.logic import create_test_map

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic
from the_tale.game.companions import relations as companions_relations

from the_tale.game.actions import prototypes
from the_tale.game.actions.tests.helpers import ActionEventsTestsMixin

from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts.relations import RARITY

from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.places.modifiers.prototypes import HolyCity, Resort

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f
from the_tale.game.balance import enums as e
from the_tale.game.balance.power import Power


class InPlaceActionTest(testcase.TestCase, ActionEventsTestsMixin):

    def setUp(self):
        super(InPlaceActionTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.action_idl = self.hero.actions.current_action

        self.hero._model.pos_previous_place_id = None # test setting prevouse place in action constructor

        self.action_inplace = prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.action_event = self.action_inplace

    def test_create(self):
        self.assertEqual(self.hero.position.previous_place, self.hero.position.place)

        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_inplace.leader, True)
        self.assertEqual(self.action_inplace.bundle_id, self.action_idl.bundle_id)

        self.storage._test_save()

    def test_instant_heal_in_resort(self):
        self.hero.health = 1
        self.hero.position.place.modifier = Resort(self.hero.position.place)
        old_messages_len = len (self.hero.messages.messages)
        prototypes.ActionInPlacePrototype.create(hero=self.hero)
        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(len(self.hero.messages.messages), old_messages_len + 1)
        self.storage._test_save()

    def test_no_instant_heal_in_resort(self):
        self.hero.health = self.hero.max_health
        self.hero.position.place.modifier = Resort(self.hero.position.place)
        old_messages_len = len (self.hero.messages.messages)
        prototypes.ActionInPlacePrototype.create(hero=self.hero)
        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(len(self.hero.messages.messages), old_messages_len)
        self.storage._test_save()


    def test_companion_heal_in_resort__no_companion(self):
        self.assertEqual(self.hero.companion, None)

        self.hero.position.place.modifier = Resort(self.hero.position.place)

        prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertEqual(self.hero.messages.messages[-1].key, None)
        self.storage._test_save()

    def test_companion_heal_in_resort__healed_companion(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.hero.companion.health, self.hero.companion.max_health)

        self.hero.position.place.modifier = Resort(self.hero.position.place)

        prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertFalse(self.hero.messages.messages[-1].key.is_ACTION_INPLACE_COMPANION_HEAL)

        self.storage._test_save()


    def test_companion_heal_in_resort__damaged_companion(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.hero.companion.health = 1

        self.hero.position.place.modifier = Resort(self.hero.position.place)

        with self.check_increased(lambda: self.hero.companion.health):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertTrue(self.hero.messages.messages[-1].key.is_ACTION_INPLACE_COMPANION_HEAL)

        self.storage._test_save()


    def test_instant_energy_regen_in_holy_city(self):
        self.hero._model.energy = 0
        self.hero._model.pos_previous_place_id = None

        self.hero.position.place.modifier = HolyCity(self.hero.position.place)


        self.assertNotEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_delta(lambda: len(self.hero.messages.messages), 1):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertEqual(self.hero.energy, c.ANGEL_ENERGY_INSTANT_REGENERATION_IN_PLACE)

        self.storage._test_save()

    def test_instant_energy_regen_in_holy_city__maximum_energy(self):
        self.hero._model.energy = self.hero.energy_maximum
        self.hero._model.pos_previous_place_id = None

        self.hero.position.place.modifier = HolyCity(self.hero.position.place)

        self.assertNotEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_not_changed(lambda: len(self.hero.messages.messages)):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertEqual(self.hero.energy, self.hero.energy_maximum)

        self.storage._test_save()

    def test_instant_energy_regen_in_holy_city__no_regen(self):
        self.hero._model.energy = 0
        self.hero._model.pos_previous_place_id = None

        self.hero.position.place.modifier = None

        self.assertNotEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_not_changed(lambda: len(self.hero.messages.messages)):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertEqual(self.hero.energy, 0)

        self.storage._test_save()

    def test_instant_energy_regen_in_holy_city__place_not_changed(self):
        self.hero._model.energy = 0
        self.hero.position.place.modifier = HolyCity(self.hero.position.place)
        self.hero.position.visit_current_place()

        self.assertEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_not_changed(lambda: len(self.hero.messages.messages)):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertEqual(self.hero.energy, 0)

        self.storage._test_save()

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.tax', 0.2)
    def test_tax(self):
        self.hero._model.money = 100
        self.hero._model.pos_previous_place_id = None

        self.assertNotEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_delta(lambda: len(self.hero.messages.messages), 1):
            with self.check_delta(lambda: self.hero.statistics.money_spend, 20):
                with self.check_delta(lambda: self.hero.statistics.money_spend_for_tax, 20):
                    prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertEqual(self.hero.money, 80)

        self.storage._test_save()

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.tax', 0.2)
    def test_tax__no_money(self):
        self.hero._model.money = 0
        self.hero._model.pos_previous_place_id = None

        self.assertNotEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_delta(lambda: len(self.hero.messages.messages), 1):
            with self.check_delta(lambda: self.hero.statistics.money_spend, 0):
                with self.check_delta(lambda: self.hero.statistics.money_spend_for_tax, 0):
                    prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertEqual(self.hero.money, 0)

        self.storage._test_save()

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.tax', 0.0)
    def test_tax__no_tax(self):
        self.hero._model.money = 100
        self.hero._model.pos_previous_place_id = None

        self.assertNotEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_delta(lambda: len(self.hero.messages.messages), 0):
            with self.check_delta(lambda: self.hero.statistics.money_spend, 0):
                with self.check_delta(lambda: self.hero.statistics.money_spend_for_tax, 0):
                    prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertEqual(self.hero.money, 100)

        self.storage._test_save()

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.tax', 0.2)
    def test_tax__place_not_changed(self):
        self.hero._model.money = 100

        self.hero.position.visit_current_place()
        self.assertEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_delta(lambda: len(self.hero.messages.messages), 0):
            with self.check_delta(lambda: self.hero.statistics.money_spend, 0):
                with self.check_delta(lambda: self.hero.statistics.money_spend_for_tax, 0):
                    prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.assertEqual(self.hero.money, 100)

        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.PLACE_HABITS_EVENT_PROBABILITY', 1.0)
    def test_habit_event(self):
        from the_tale.game.relations import HABIT_HONOR_INTERVAL, HABIT_PEACEFULNESS_INTERVAL

        for honor in HABIT_HONOR_INTERVAL.records:
            for peacefulness in HABIT_PEACEFULNESS_INTERVAL.records:

                self.hero.diary.clear()

                self.hero._model.pos_previous_place_id = None
                self.assertNotEqual(self.hero.position.place, self.hero.position.previous_place)

                with mock.patch('the_tale.game.map.places.habits.Honor.interval', honor):
                    with mock.patch('the_tale.game.map.places.habits.Peacefulness.interval', peacefulness):
                        with self.check_delta(self.hero.diary.messages_number, 1):
                            prototypes.ActionInPlacePrototype.create(hero=self.hero)


        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.PLACE_HABITS_EVENT_PROBABILITY', 0.0)
    def test_habit_event__no_event(self):
        self.hero._model.pos_previous_place_id = None

        self.assertNotEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_not_changed(lambda: len(self.hero.diary.messages)):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.PLACE_HABITS_EVENT_PROBABILITY', 1.0)
    def test_habit_event__not_visit(self):
        self.assertEqual(self.hero.position.place, self.hero.position.previous_place)

        with self.check_not_changed(lambda: len(self.hero.diary.messages)):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.storage._test_save()

    def test_processed(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()

    def test_regenerate_energy_action_create(self):
        self.hero.preferences.set_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY)
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 3)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRegenerateEnergyPrototype.TYPE)
        self.storage._test_save()

    def test_regenerate_energy_action_not_create_for_sacrifice(self):
        self.hero.preferences.set_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE)
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()

    def test_heal_action_create(self):
        self.hero.health = 1
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 3)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRestPrototype.TYPE)
        self.storage._test_save()

    @mock.patch('the_tale.game.companions.objects.Companion.need_heal_in_settlement', True)
    def test_heal_companion_action_create(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 3)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionHealCompanionPrototype.TYPE)
        self.assertEqual(self.action_inplace.state, prototypes.ActionInPlacePrototype.STATE.HEALING_COMPANION)
        self.storage._test_save()

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)
        self.storage._test_save()

    @mock.patch('the_tale.game.companions.objects.Companion.need_heal_in_settlement', True)
    def test_heal_companion_action_create__no_companion(self):
        self.assertEqual(self.hero.companion, None)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionIdlenessPrototype.TYPE)
        self.storage._test_save()

    def test_trade_action_create(self):

        for i in xrange(int(c.MAX_BAG_SIZE * c.BAG_SIZE_TO_SELL_LOOT_FRACTION) + 1):
            artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.loot, 1, rarity=RARITY.NORMAL)
            self.hero.bag.put_artifact(artifact)

        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 3)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionTradingPrototype.TYPE)

        self.storage._test_save()

    def test_equip_action_create(self):
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, 1, rarity=RARITY.NORMAL)
        artifact.power = Power(666, 666)
        self.hero.bag.put_artifact(artifact)

        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 3)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionEquippingPrototype.TYPE)

        self.storage._test_save()

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()


class InPlaceActionSpendMoneyTest(testcase.TestCase):

    def setUp(self):
        super(InPlaceActionSpendMoneyTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.action_inplace = prototypes.ActionInPlacePrototype.create(hero=self.hero)


    def test_no_money(self):

        self.hero._model.money = 1
        self.storage.process_turn()
        self.assertEqual(self.hero.money, 1)
        self.assertEqual(self.hero.statistics.money_spend, 0)
        self.storage._test_save()


    @mock.patch('the_tale.game.balance.constants.PRICE_DELTA', 0.0)
    def test_instant_heal(self):
        while not self.hero.next_spending.is_INSTANT_HEAL:
            self.hero.switch_spending()

        money = self.hero.spend_amount

        self.hero._model.money = money + 666
        self.hero.health = 1
        self.storage.process_turn()
        self.assertEqual(self.hero.money, 666)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.assertEqual(self.hero.statistics.money_spend, money)
        self.assertEqual(self.hero.statistics.money_spend_for_heal, money)
        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.PRICE_DELTA', 0.0)
    def test_instant_heal__too_much_health(self):
        while not self.hero.next_spending.is_INSTANT_HEAL:
            self.hero.switch_spending()

        money = self.hero.spend_amount
        health = (self.hero.max_health * c.SPEND_MONEY_FOR_HEAL_HEALTH_FRACTION) + 1

        self.hero._model.money = money + 666
        self.hero.health = health
        self.storage.process_turn()
        self.assertTrue(self.hero.money, money + 666)
        self.assertEqual(self.hero.health, health)

        self.assertEqual(self.hero.statistics.money_spend, 0)
        self.assertEqual(self.hero.statistics.money_spend_for_heal, 0)
        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.PRICE_DELTA', 0.0)
    def test_instant_heal__low_health(self):
        while not self.hero.next_spending.is_INSTANT_HEAL:
            self.hero.switch_spending()

        money = self.hero.spend_amount
        health = (self.hero.max_health * c.SPEND_MONEY_FOR_HEAL_HEALTH_FRACTION) - 1

        self.hero._model.money = money
        self.hero.health = health
        self.storage.process_turn()
        self.assertEqual(self.hero.money, 0)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.assertEqual(self.hero.statistics.money_spend, money)
        self.assertEqual(self.hero.statistics.money_spend_for_heal, money)
        self.storage._test_save()


    def test_bying_artifact_with_hero_preferences(self):
        while not self.hero.next_spending.is_BUYING_ARTIFACT:
            self.hero.switch_spending()

        money = self.hero.spend_amount

        self.assertEqual(self.hero.statistics.money_spend, 0)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

        #unequip all arefact
        self.hero.equipment._remove_all()
        # self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)
        self.hero.save()

        #buy artifact
        self.hero._model.money = money
        self.storage.process_turn()
        self.assertTrue(self.hero.money < money * c.PRICE_DELTA + 1)
        self.assertEqual(len(self.hero.bag.items()), 0)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, money - self.hero.money)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

        # # hero must not buy artifact in preferences slot, he has special quest for this
        # self.assertEqual(self.hero.equipment.get(EQUIPMENT_SLOT.PLATE), None)
        # self.storage._test_save()


    def test_bying_artifact_without_change(self):
        while not self.hero.next_spending.is_BUYING_ARTIFACT:
            self.hero.switch_spending()

        money = self.hero.spend_amount

        self.assertEqual(self.hero.statistics.money_spend, 0)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

        #unequip all arefact
        self.hero.equipment._remove_all()
        self.hero.save()

        #buy artifact
        self.hero._model.money = money

        self.storage.process_turn()
        self.assertTrue(self.hero.money < money * c.PRICE_DELTA + 1)
        self.assertEqual(len(self.hero.bag.items()), 0)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, money - self.hero.money)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)
        self.storage._test_save()

    def test_bying_artifact_with_change(self):
        while not self.hero.next_spending.is_BUYING_ARTIFACT:
            self.hero.switch_spending()

        # fill all slots with artifacts
        self.hero.equipment.test_equip_in_all_slots(artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level, rarity=RARITY.NORMAL))

        money = self.hero.spend_amount

        #buy artifact
        self.hero._model.money = money

        self.assertEqual(self.hero.statistics.money_spend, 0)
        self.assertEqual(self.hero.statistics.money_spend_for_artifacts, 0)
        self.assertEqual(self.hero.statistics.money_earned_from_artifacts, 0)

        self.storage.process_turn()
        self.assertTrue(self.hero.money > 0)
        self.assertEqual(len(self.hero.bag.items()), 0)

        self.assertTrue(self.hero.statistics.money_spend > money - self.hero.money)
        self.assertTrue(self.hero.statistics.money_spend_for_artifacts > money - self.hero.money)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)
        self.assertTrue(self.hero.statistics.money_earned_from_artifacts > 0)
        self.storage._test_save()

    def test_sharpening_artifact(self):
        while not self.hero.next_spending.is_SHARPENING_ARTIFACT:
            self.hero.switch_spending()

        money = self.hero.spend_amount

        old_power = self.hero.power.clone()

        self.hero._model.money = money
        self.storage.process_turn()
        self.assertTrue(self.hero.money < money * c.PRICE_DELTA + 1)
        self.assertEqual(old_power.total() + 1, self.hero.power.total())

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_sharpening, money - self.hero.money)
        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_upgrade_prefered_slot', True)
    def test_sharpening_artifact_with_hero_preferences(self):
        while not self.hero.next_spending.is_SHARPENING_ARTIFACT:
            self.hero.switch_spending()

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)
        self.hero.save()

        money = self.hero.spend_amount

        old_power = self.hero.power.clone()
        old_plate_power = self.hero.equipment.get(EQUIPMENT_SLOT.PLATE).power.clone()

        self.hero._model.money = money
        self.storage.process_turn()
        self.assertTrue(self.hero.money < money * c.PRICE_DELTA + 1)
        self.assertEqual(old_power.total() + 1, self.hero.power.total())
        self.assertEqual(old_plate_power.total() + 1, self.hero.equipment.get(EQUIPMENT_SLOT.PLATE).power.total())

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_sharpening, money - self.hero.money)
        self.storage._test_save()


    def test_repair_artifact(self):
        for artifact in self.hero.equipment.values():
            artifact.integrity = artifact.max_integrity

        test_artifact = artifact
        test_artifact.integrity = 0

        while not self.hero.next_spending.is_REPAIRING_ARTIFACT:
            self.hero.switch_spending()

        money = self.hero.spend_amount

        self.hero._model.money = money
        self.storage.process_turn()
        self.assertTrue(self.hero.money < money * c.PRICE_DELTA + 1)

        self.assertEqual(test_artifact.integrity, test_artifact.max_integrity)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_repairing, money - self.hero.money)
        self.storage._test_save()

    def test_useless(self):
        while not self.hero.next_spending.is_USELESS:
            self.hero.switch_spending()

        money = self.hero.spend_amount
        self.hero._model.money = money
        self.storage.process_turn()
        self.assertTrue(self.hero.money < money * c.PRICE_DELTA + 1)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_useless, money - self.hero.money)
        self.storage._test_save()


    def test_impact(self):
        while not self.hero.next_spending.is_IMPACT:
            self.hero.switch_spending()

        money = self.hero.spend_amount
        self.hero._model.money = money

        with mock.patch('the_tale.game.persons.prototypes.PersonPrototype.cmd_change_power') as cmd_change_power:
            self.storage.process_turn()

        self.assertEqual(cmd_change_power.call_count, 0)

        self.assertTrue(self.hero.money < money * c.PRICE_DELTA + 1)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_impact, money - self.hero.money)
        self.storage._test_save()

    def test_impact__can_change_power(self):
        while not self.hero.next_spending.is_IMPACT:
            self.hero.switch_spending()

        money = self.hero.spend_amount
        self.hero._model.money = money

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_change_person_power', lambda self, person: True):
            with mock.patch('the_tale.game.persons.prototypes.PersonPrototype.cmd_change_power') as cmd_change_power:
                self.storage.process_turn()

        self.assertEqual(cmd_change_power.call_count, 1)

        self.assertTrue(self.hero.money < money * c.PRICE_DELTA + 1)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_impact, money - self.hero.money)
        self.storage._test_save()

    def test_experience(self):
        while not self.hero.next_spending.is_EXPERIENCE:
            self.hero.switch_spending()

        money = self.hero.spend_amount
        self.hero._model.money = money
        self.storage.process_turn()
        self.assertTrue(self.hero.money < money * c.PRICE_DELTA + 1)

        self.assertEqual(self.hero.statistics.money_spend, money - self.hero.money)
        self.assertEqual(self.hero.statistics.money_spend_for_experience, money - self.hero.money)
        self.storage._test_save()



class InPlaceActionCompanionBuyMealTests(testcase.TestCase):

    def setUp(self):
        super(InPlaceActionCompanionBuyMealTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action

        self.companion_record = companions_logic.create_random_companion_record('thief', state=companions_relations.STATE.ENABLED)
        self.hero.set_companion(companions_logic.create_companion(self.companion_record))

        self.hero._model.money = f.expected_gold_in_day(self.hero.level)

        self.hero.position.set_place(self.place_1)
        self.hero.position.visit_current_place()
        self.hero.position.set_place(self.place_2)


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_money_for_food_multiplier', 0.5)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_eat', lambda hero: True)
    def test_buy_meal(self):
        with contextlib.nested(
                self.check_decreased(lambda: self.hero.money),
                self.check_increased(lambda: self.hero.statistics.money_spend_for_companions),
                self.check_increased(lambda: len(self.hero.messages))
                ):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_money_for_food_multiplier', 0.5)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_eat', lambda hero: True)
    def check_not_used(self):
        with contextlib.nested(
                self.check_not_changed(lambda: self.hero.money),
                self.check_not_changed(lambda: self.hero.statistics.money_spend_for_companions),
                self.check_not_changed(lambda: len(self.hero.messages))
                ):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_money_for_food_multiplier', 0.5)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_eat', lambda hero: True)
    def test_no_previouse_place(self):
        self.hero._model.pos_previous_place = None
        self.check_not_used()

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_money_for_food_multiplier', 0.5)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_eat', lambda hero: True)
    def test_previouse_place_is_equal(self):
        self.hero.position.visit_current_place()
        self.check_not_used()

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_money_for_food_multiplier', 66666666)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_eat', lambda hero: True)
    def test_not_enough_money(self):
        with contextlib.nested(
                self.check_delta(lambda: self.hero.money, -self.hero.money),
                self.check_delta(lambda: self.hero.statistics.money_spend_for_companions, self.hero.money),
                self.check_increased(lambda: len(self.hero.messages))
                ):
            prototypes.ActionInPlacePrototype.create(hero=self.hero)


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_money_for_food_multiplier', 66666666)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_eat', lambda hero: True)
    def test_no_money(self):
        self.hero._model.money = 0
        self.check_not_used()


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.companion_money_for_food_multiplier', 0.5)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_eat', lambda hero: False)
    def test_companion_does_not_eat(self):
        self.hero.position.visit_current_place()
        self.check_not_used()



class InPlaceActionCompanionStealingTest(testcase.TestCase):

    def setUp(self):
        super(InPlaceActionCompanionStealingTest, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action

        self.action_inplace = prototypes.ActionInPlacePrototype.create(hero=self.hero)

        self.action_inplace.state = self.action_inplace.STATE.PROCESSED

        self.companion_record = companions_logic.create_random_companion_record('thief', state=companions_relations.STATE.ENABLED)
        self.hero.set_companion(companions_logic.create_companion(self.companion_record))


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_money', lambda self: True)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_item', lambda self: True)
    def test_no_companion(self):
        self.hero.remove_companion()

        with contextlib.nested(
                self.check_not_changed(lambda: self.hero.bag.occupation),
                self.check_not_changed(lambda: self.hero.money),
                self.check_not_changed(lambda: self.hero.statistics.money_earned_from_companions),
                self.check_not_changed(lambda: self.hero.statistics.artifacts_had),
                self.check_not_changed(lambda: self.hero.statistics.loot_had),
                self.check_not_changed(lambda: len(self.hero.messages))
                ):
            self.storage.process_turn(continue_steps_if_needed=False)

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_money', lambda self: True)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_item', lambda self: False)
    def test_steal_money(self):
        with contextlib.nested(
                self.check_not_changed(lambda: self.hero.bag.occupation),
                self.check_increased(lambda: self.hero.money),
                self.check_increased(lambda: self.hero.statistics.money_earned_from_companions),
                self.check_not_changed(lambda: self.hero.statistics.artifacts_had),
                self.check_not_changed(lambda: self.hero.statistics.loot_had),
                self.check_increased(lambda: len(self.hero.messages))
                ):
            self.storage.process_turn(continue_steps_if_needed=False)


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_money', lambda self: False)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_item', lambda self: True)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.artifacts_probability', lambda self, mob: 0)
    def test_steal_item__loot(self):
        with contextlib.nested(
                self.check_increased(lambda: self.hero.bag.occupation),
                self.check_not_changed(lambda: self.hero.money),
                self.check_not_changed(lambda: self.hero.statistics.money_earned_from_companions),
                self.check_not_changed(lambda: self.hero.statistics.artifacts_had),
                self.check_delta(lambda: self.hero.statistics.loot_had, 1),
                self.check_increased(lambda: len(self.hero.messages))
                ):
            self.storage.process_turn(continue_steps_if_needed=False)


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_money', lambda self: False)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_item', lambda self: True)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.artifacts_probability', lambda self, mob: 1)
    def test_steal_item__artifact(self):
        with contextlib.nested(
                self.check_increased(lambda: self.hero.bag.occupation),
                self.check_not_changed(lambda: self.hero.money),
                self.check_not_changed(lambda: self.hero.statistics.money_earned_from_companions),
                self.check_delta(lambda: self.hero.statistics.artifacts_had, 1),
                self.check_not_changed(lambda: self.hero.statistics.loot_had),
                self.check_increased(lambda: len(self.hero.messages))
                ):
            self.storage.process_turn(continue_steps_if_needed=False)



    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_money', lambda self: False)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_item', lambda self: True)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.bag_is_full', True)
    def test_steal_item__bag_is_full(self):
        with contextlib.nested(
                self.check_not_changed(lambda: self.hero.bag.occupation),
                self.check_not_changed(lambda: self.hero.money),
                self.check_not_changed(lambda: self.hero.statistics.money_earned_from_companions),
                self.check_not_changed(lambda: self.hero.statistics.artifacts_had),
                self.check_not_changed(lambda: self.hero.statistics.loot_had),
                self.check_not_changed(lambda: len(self.hero.messages))
                ):
            self.storage.process_turn(continue_steps_if_needed=False)


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_money', lambda self: True)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.can_companion_steal_item', lambda self: True)
    def test_steal_all(self):
        with contextlib.nested(
                self.check_increased(lambda: self.hero.bag.occupation),
                self.check_increased(lambda: self.hero.money),
                self.check_increased(lambda: self.hero.statistics.money_earned_from_companions),
                self.check_delta(lambda: self.hero.statistics.artifacts_had + self.hero.statistics.loot_had, 1),
                self.check_increased(lambda: len(self.hero.messages))
                ):
            self.storage.process_turn(continue_steps_if_needed=False)
