# coding: utf-8
import mock
import datetime

from django.test import client
from django.core.urlresolvers import reverse

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import PostponedTask, PostponedTaskPrototype, FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.logic import register_user, login_page_url
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map

from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.mobs import relations as mobs_relations

from the_tale.game.map.places.models import Place

from the_tale.game.logic_storage import LogicStorage

from the_tale.game import relations as game_relations

from the_tale.game.persons.models import Person
from the_tale.game.persons.relations import PERSON_STATE
from the_tale.game.persons.storage import persons_storage

from the_tale.game.heroes import relations
from the_tale.game.heroes.postponed_tasks import ChoosePreferencesTask, CHOOSE_PREFERENCES_TASK_STATE
from the_tale.game.heroes.preferences import HeroPreferences

from .. import logic
from .. import models


class PreferencesTestMixin(object):

    def test_reset_change_time(self):
        value = self.hero.preferences._get(self.PREFERENCE_TYPE)
        self.hero.preferences._set(self.PREFERENCE_TYPE, value)
        self.assertFalse(self.hero.preferences.can_update(self.PREFERENCE_TYPE, datetime.datetime.now()))
        self.hero.preferences.updated = False
        self.hero.preferences.reset_change_time(self.PREFERENCE_TYPE)
        self.assertTrue(self.hero.preferences.can_update(self.PREFERENCE_TYPE, datetime.datetime.now()))
        self.assertTrue(self.hero.preferences.updated)

    def test_reset_change_time__not_registered(self):
        self.hero.preferences.data = {}
        self.hero.preferences.reset_change_time(self.PREFERENCE_TYPE)
        self.assertFalse(self.hero.preferences.updated)
        self.assertTrue(self.hero.preferences.can_update(self.PREFERENCE_TYPE, datetime.datetime.now()))
        self.assertFalse(self.hero.preferences.updated)


class HeroPreferencesEnergyRegenerationTypeTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE

    def setUp(self):
        super(HeroPreferencesEnergyRegenerationTypeTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE.level_required
        self.hero.preferences.set_energy_regeneration_type(relations.ENERGY_REGENERATION.SACRIFICE, change_time=datetime.datetime.fromtimestamp(0))
        logic.save_hero(self.hero)

    def test_preferences_serialization(self):
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_energy_regeneration_type(relations.ENERGY_REGENERATION.PRAY)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.energy_regeneration_type, relations.ENERGY_REGENERATION.PRAY)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.place, None)

    def test_serialization(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(task.serialize(), ChoosePreferencesTask.deserialize(task.serialize()).serialize())

    # can not test wrong level, since energy regeneration choice available on 1 level
    def test_wrong_level(self):
        self.assertEqual(relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE.level_required, 1)

    # can not test purchased state, since energy regeneration choice available on 1 level
    def test_purchased(self):
        self.assertEqual(relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE.level_required, 1)

    def test_wrong_format_of_energy_regeneration_type(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ENERGY_REGENERATION_TYPE)

    def test_wrong_energy_regeneration_type(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ENERGY_REGENERATION_TYPE)

    # can not test set energy regeneration type, since it must be always selected
    def test_set_energy_regeneration_typ(self):
        self.assertNotEqual(self.hero.preferences.energy_regeneration_type, None)

    def check_change_energy_regeneration_type(self, new_energy_regeneration_type, expected_energy_regeneration_type, expected_state):
        task = ChoosePreferencesTask(self.hero.id,
                                     relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE,
                                     new_energy_regeneration_type.value if new_energy_regeneration_type is not None else None)
        self.assertNotEqual(self.hero.preferences.energy_regeneration_type, new_energy_regeneration_type)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            process_result = task.process(FakePostpondTaskPrototype(), self.storage)

        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED, process_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.energy_regeneration_type, expected_energy_regeneration_type)
        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).energy_regeneration_type, expected_energy_regeneration_type)

    def test_change_energy_regeneration_type(self):
        self.check_change_energy_regeneration_type(relations.ENERGY_REGENERATION.PRAY, relations.ENERGY_REGENERATION.PRAY, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_energy_regeneration_type_cooldown(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, relations.ENERGY_REGENERATION.SYMBOLS.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.check_change_energy_regeneration_type(relations.ENERGY_REGENERATION.PRAY, relations.ENERGY_REGENERATION.SYMBOLS, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    def test_remove_energy_regeneration_type(self):
        self.check_change_energy_regeneration_type(None, relations.ENERGY_REGENERATION.SACRIFICE, CHOOSE_PREFERENCES_TASK_STATE.UNSPECIFIED_PREFERENCE)

    def test_remove_energy_regeneration_type_cooldown(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, relations.ENERGY_REGENERATION.SYMBOLS.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.check_change_energy_regeneration_type(None, relations.ENERGY_REGENERATION.SYMBOLS, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesMobTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.MOB

    def setUp(self):
        super(HeroPreferencesMobTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.MOB.level_required
        logic.save_hero(self.hero)

        self.mob_uuid = mobs_storage.get_available_mobs_list(level=self.hero.level)[0].uuid
        self.mob_2_uuid = mobs_storage.get_available_mobs_list(level=self.hero.level)[1].uuid

    def test_preferences_serialization(self):
        self.hero.preferences.set_mob(mobs_storage.all()[0])
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        mob = mobs_storage.all()[0]
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_mob(mob)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.mob.id, mob.id)

    def test_reset_mob_when_it_disabled(self):
        mob_record = mobs_storage.all()[0]
        self.hero.preferences.set_mob(mob_record)

        self.assertEqual(self.hero.preferences.mob, mob_record)

        mob_record.state = mobs_relations.MOB_RECORD_STATE.DISABLED
        mob_record.save()

        self.assertEqual(self.hero.preferences.mob, None)
        self.assertEqual(self.hero.preferences.mob_changed_at, datetime.datetime.fromtimestamp(0))


    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.MOB, 'wrong_mob_uuid')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.mob, None)

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.MOB.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.MOB, self.mob_uuid)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_mob(self, mob_uuid):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.MOB, mob_uuid)

        self.assertEqual(self.hero.preferences.mob, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.mob.uuid, mob_uuid)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.MOB.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.MOB.purchase_type)
        self.account.save()

        self.check_set_mob(self.mob_uuid)


    def test_wrong_mob(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.MOB, 'wrong_mob_uuid')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_MOB)

    def test_wrong_mob_level(self):
        mobs_storage.all()[1].level = self.hero.level + 1

        wrong_mob_uuid = None
        for mob_record in mobs_storage.all():
            if mob_record.state.is_ENABLED and mob_record.level > self.hero.level:
                wrong_mob_uuid = mob_record.uuid
                break

        self.assertTrue(wrong_mob_uuid)

        self.assertEqual(mobs_storage.all()[1].uuid, wrong_mob_uuid)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.MOB, wrong_mob_uuid)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LARGE_MOB_LEVEL)
        self.assertEqual(self.hero.preferences.mob, None)

    def test_mob_not_in_game(self):
        mob_record = mobs_storage.all()[1]
        mob_record.state = mobs_relations.MOB_RECORD_STATE.DISABLED
        mob_record.save()

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.MOB, mob_record.uuid)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.MOB_NOT_IN_GAME)
        self.assertEqual(self.hero.preferences.mob, None)


    def test_set_mob(self):
        changed_at = self.hero.preferences.mob_changed_at
        self.check_set_mob(self.mob_uuid)
        self.assertTrue(changed_at < self.hero.preferences.mob_changed_at)

    def check_change_mob(self, new_mob_uuid, expected_mob_uuid, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.MOB, self.mob_uuid)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.MOB, new_mob_uuid)
        self.assertEqual(self.hero.preferences.mob.uuid, self.mob_uuid)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED, task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(task.state, expected_state)
        if self.hero.preferences.mob is None:
            self.assertEqual(expected_mob_uuid, None)
            self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).mob_id, None)
        else:
            self.assertEqual(self.hero.preferences.mob.uuid, expected_mob_uuid)
            self.assertEqual(mobs_storage[models.HeroPreferences.objects.get(hero_id=self.hero.id).mob_id].uuid, expected_mob_uuid)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)


    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_mob(self):
        self.check_change_mob(self.mob_2_uuid, self.mob_2_uuid, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_mob_cooldown(self):
        self.check_change_mob(self.mob_2_uuid, self.mob_uuid, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_mob(self):
        self.check_change_mob(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_mob_cooldown(self):
        self.check_change_mob(None, self.mob_uuid, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesPlaceTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.PLACE

    def setUp(self):
        super(HeroPreferencesPlaceTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.PLACE.level_required
        logic.save_hero(self.hero)

        self.place = place_1
        self.place_2 = place_2
        self.place_3 = place_3

    def test_preferences_serialization(self):
        self.hero.preferences.set_place(self.place)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_place(self.place)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.place.id, self.place.id)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.PLACE, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.place, None)

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.PLACE.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.PLACE, self.place.id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_place(self, place):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.PLACE, place.id)
        self.assertEqual(self.hero.preferences.place, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.place.id, place.id)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.PLACE.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.PLACE.purchase_type)
        self.account.save()

        self.check_set_place(self.place)

    def test_wrong_place(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.PLACE, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PLACE)

    def test_wrong_format_of_place(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.PLACE, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PLACE)

    def test_set_place(self):
        self.assertEqual(HeroPreferences.get_citizens_of(self.place, all=False), [])
        self.assertEqual(HeroPreferences.get_citizens_of(self.place, all=True), [])

        changed_at = self.hero.preferences.place_changed_at

        self.check_set_place(self.place)

        self.assertTrue(changed_at < self.hero.preferences.place_changed_at)

        self.assertEqual([hero.id for hero in HeroPreferences.get_citizens_of(self.place, all=False)], [])
        self.assertEqual([hero.id for hero in HeroPreferences.get_citizens_of(self.place, all=True)], [self.hero.id])

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        logic.save_hero(self.hero)

        self.assertEqual([hero.id for hero in HeroPreferences.get_citizens_of(self.place, all=False)], [self.hero.id])
        self.assertEqual([hero.id for hero in HeroPreferences.get_citizens_of(self.place, all=True)], [self.hero.id])

    def check_change_place(self, new_place_id, expected_place_id, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.PLACE, self.place.id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.PLACE, new_place_id)
        self.assertEqual(self.hero.preferences.place.id, self.place.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(task.state, expected_state)

        if expected_place_id is None:
            self.assertEqual(self.hero.preferences.place, None)
        else:
            self.assertEqual(self.hero.preferences.place.id, expected_place_id)
        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).place_id, expected_place_id)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_place(self):
        self.check_change_place(self.place_2.id, self.place_2.id, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_place_cooldown(self):
        self.check_change_place(self.place_2.id, self.place.id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_place(self):
        self.check_change_place(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_place_cooldown(self):
        self.check_change_place(None, self.place.id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    def test_get_citizens_number(self):
        hero_1 = self.hero
        hero_1.preferences.set_place(self.place)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_1)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = logic.load_hero(account_id=account_id)
        hero_2.preferences.set_place(self.place)
        logic.save_hero(hero_2)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = logic.load_hero(account_id=account_id)
        hero_3.preferences.set_place(self.place)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_3)

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = logic.load_hero(account_id=account_id)
        hero_4.preferences.set_place(self.place)
        logic.save_hero(hero_4)

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        hero_5 = logic.load_hero(account_id=account_id)
        hero_5.preferences.set_place(self.place)
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_5)

        result, account_id, bundle_id = register_user('test_user_6', 'test_user_6@test.com', '111111')
        hero_6 = logic.load_hero(account_id=account_id)
        hero_6.preferences.set_place(self.place_2)
        hero_6.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_6)

        result, account_id, bundle_id = register_user('test_user_7', 'test_user_7@test.com', '111111')
        hero_7 = logic.load_hero(account_id=account_id)
        hero_7.preferences.set_place(self.place)
        hero_7.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        logic.save_hero(hero_7)

        self.assertEqual(HeroPreferences.count_citizens_of(self.place, all=False), 2)
        self.assertEqual(HeroPreferences.count_citizens_of(self.place_2, all=False), 1)
        self.assertEqual(HeroPreferences.count_citizens_of(self.place_3, all=False), 0)

        self.assertEqual(HeroPreferences.count_citizens_of(self.place, all=True), 3)

        self.assertEqual(set([h.id for h in HeroPreferences.get_citizens_of(self.place, all=False)]), set([hero_1.id, hero_3.id]))
        self.assertEqual(set([h.id for h in HeroPreferences.get_citizens_of(self.place, all=True)]), set([hero_1.id, hero_2.id, hero_3.id]))


    def test_count_habit_values(self):
        hero_1 = self.hero
        hero_1.preferences.set_place(self.place)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.habit_honor.change(-1)
        hero_1.habit_peacefulness.change(1)
        logic.save_hero(hero_1)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = logic.load_hero(account_id=account_id)
        hero_2.preferences.set_place(self.place)
        hero_2.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_2.habit_honor.change(2)
        hero_2.habit_peacefulness.change(-2)
        logic.save_hero(hero_2)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = logic.load_hero(account_id=account_id)
        hero_3.preferences.set_place(self.place_2)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_3.habit_honor.change(-4)
        hero_3.habit_peacefulness.change(4)
        logic.save_hero(hero_3)

        result, account_id, bundle_id = register_user('test_user_4', 'test_user_4@test.com', '111111')
        hero_4 = logic.load_hero(account_id=account_id)
        hero_4.preferences.set_place(self.place)
        hero_4.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_4.habit_honor.change(8)
        hero_4.habit_peacefulness.change(-8)
        logic.save_hero(hero_4)

        self.assertEqual(HeroPreferences.count_habit_values(self.place, all=False), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=False), ((0, -4), (4, 0)))

        self.assertEqual(HeroPreferences.count_habit_values(self.place, all=True), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=True), ((0, -4), (4, 0)))



class HeroPreferencesFriendTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.FRIEND

    def setUp(self):
        super(HeroPreferencesFriendTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.FRIEND.level_required
        logic.save_hero(self.hero)

        self.friend = self.place_1.persons[0]
        self.friend_2 = self.place_2.persons[0]
        self.enemy = self.place_3.persons[0]

        self.friend_id = self.friend.id
        self.friend_2_id = self.friend_2.id
        self.enemy_id = self.enemy.id

    def test_preferences_serialization(self):
        self.hero.preferences.set_friend(persons_storage[self.friend_id])
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        friend = persons_storage[self.friend_id]

        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_friend(friend)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.friend.id, friend.id)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FRIEND, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.friend, None)

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.FRIEND.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_friend(self, friend_id):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FRIEND, friend_id)
        self.assertEqual(self.hero.preferences.friend, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.friend.id, friend_id)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.FRIEND.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.FRIEND.purchase_type)
        self.account.save()

        self.check_set_friend(self.friend_id)

    def test_wrong_friend(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FRIEND, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON)

    def test_wrong_format(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FRIEND, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON)

    def test_set_enemy_as_friend(self):
        self.hero.preferences.set_enemy(persons_storage[self.enemy_id])
        logic.save_hero(self.hero)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FRIEND, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.ENEMY_AND_FRIEND)

    def test_set_outgame_friend(self):
        friend = persons_storage[self.friend_id]
        friend.move_out_game()
        friend.save()

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.OUTGAME_PERSON)
        self.assertEqual(self.hero.preferences.friend, None)


    def test_set_friend(self):
        self.assertEqual(HeroPreferences.get_friends_of(persons_storage[self.friend_id], all=False), [])
        self.assertEqual(HeroPreferences.get_friends_of(persons_storage[self.friend_id], all=True), [])

        changed_at = self.hero.preferences.friend_changed_at
        self.check_set_friend(self.friend_id)

        self.assertTrue(changed_at < self.hero.preferences.friend_changed_at)

        self.assertEqual([hero.id for hero in HeroPreferences.get_friends_of(persons_storage[self.friend_id], all=False)], [])
        self.assertEqual([hero.id for hero in HeroPreferences.get_friends_of(persons_storage[self.friend_id], all=True)], [self.hero.id])

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        logic.save_hero(self.hero)

        self.assertEqual([hero.id for hero in HeroPreferences.get_friends_of(persons_storage[self.friend_id], all=False)], [self.hero.id])
        self.assertEqual([hero.id for hero in HeroPreferences.get_friends_of(persons_storage[self.friend_id], all=True)], [self.hero.id])

    def check_change_friend(self, new_friend_id, expected_friend_id, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FRIEND, new_friend_id)
        self.assertEqual(self.hero.preferences.friend.id, self.friend_id)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        if expected_friend_id is None:
            self.assertEqual(self.hero.preferences.friend, None)
        else:
            self.assertEqual(self.hero.preferences.friend.id, expected_friend_id)
        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).friend_id, expected_friend_id)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_friend(self):
        self.check_change_friend(self.friend_2_id, self.friend_2_id, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_friend_cooldownd(self):
        self.check_change_friend(self.friend_2_id, self.friend_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_friend(self):
        self.check_change_friend(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_friend_cooldown(self):
        self.check_change_friend(None, self.friend_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    def test_get_friends_number(self):
        hero_1 = self.hero

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = logic.load_hero(account_id=account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = logic.load_hero(account_id=account_id)

        person_1 = self.place_1.persons[0]
        person_2 = self.place_1.persons[-1]

        hero_1.preferences.set_friend(person_1)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_1)

        hero_2.preferences.set_friend(person_1)
        logic.save_hero(hero_2)

        hero_3.preferences.set_friend(person_1)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_3)

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = logic.load_hero(account_id=account_id)
        hero_4.preferences.set_friend(person_1)
        logic.save_hero(hero_4)

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        hero_5 = logic.load_hero(account_id=account_id)
        hero_5.preferences.set_friend(person_1)
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_5)

        result, account_id, bundle_id = register_user('test_user_6', 'test_user_6@test.com', '111111')
        hero_6 = logic.load_hero(account_id=account_id)
        hero_6.preferences.set_friend(person_1)
        hero_6.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        logic.save_hero(hero_6)

        self.assertEqual(HeroPreferences.count_friends_of(person_1, all=False), 2)
        self.assertEqual(HeroPreferences.count_friends_of(person_2, all=False), 0)

        self.assertEqual(HeroPreferences.count_friends_of(person_1, all=True), 3)

        self.assertEqual(set([h.id for h in HeroPreferences.get_friends_of(person_1, all=False)]), set([hero_1.id, hero_3.id]))
        self.assertEqual(set([h.id for h in HeroPreferences.get_friends_of(person_1, all=True)]), set([hero_1.id, hero_2.id, hero_3.id]))

    def test_reset_friend_on_highlevel_update(self):
        friend = self.place_1.persons[0]

        self.hero.preferences.set_friend(friend)
        logic.save_hero(self.hero)

        friend.move_out_game()
        friend.save()

        self.storage.on_highlevel_data_updated()

        self.assertEqual(self.hero.preferences.friend, None)


    def test_count_habit_values(self):
        hero_1 = self.hero
        hero_1.preferences.set_friend(self.friend)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.habit_honor.change(-1)
        hero_1.habit_peacefulness.change(1)
        logic.save_hero(hero_1)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = logic.load_hero(account_id=account_id)
        hero_2.preferences.set_friend(self.friend)
        hero_2.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_2.habit_honor.change(2)
        hero_2.habit_peacefulness.change(-2)
        logic.save_hero(hero_2)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = logic.load_hero(account_id=account_id)
        hero_3.preferences.set_friend(self.friend_2)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_3.habit_honor.change(-4)
        hero_3.habit_peacefulness.change(4)
        logic.save_hero(hero_3)

        result, account_id, bundle_id = register_user('test_user_4', 'test_user_4@test.com', '111111')
        hero_4 = logic.load_hero(account_id=account_id)
        hero_4.preferences.set_friend(self.friend)
        hero_4.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_4.habit_honor.change(8)
        hero_4.habit_peacefulness.change(-8)
        logic.save_hero(hero_4)

        self.assertEqual(HeroPreferences.count_habit_values(self.place_1, all=False), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=False), ((0, -4), (4, 0)))

        self.assertEqual(HeroPreferences.count_habit_values(self.place_1, all=True), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=True), ((0, -4), (4, 0)))




class HeroPreferencesEnemyTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.ENEMY

    def setUp(self):
        super(HeroPreferencesEnemyTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.ENEMY.level_required
        logic.save_hero(self.hero)

        self.enemy = self.place_1.persons[0]
        self.enemy_2 = self.place_2.persons[0]
        self.friend = self.place_3.persons[0]

        self.enemy_id = self.enemy.id
        self.enemy_2_id = self.enemy_2.id
        self.friend_id =  self.friend.id

    def test_preferences_serialization(self):
        self.hero.preferences.set_enemy(persons_storage[self.enemy_id])
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        enemy = persons_storage[self.enemy_id]

        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_enemy(enemy)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.enemy.id, enemy.id)


    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENEMY, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.enemy, None)

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.ENEMY.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_enemy(self, enemy_id):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENEMY, enemy_id)
        self.assertEqual(self.hero.preferences.enemy, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.enemy.id, enemy_id)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.ENEMY.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.ENEMY.purchase_type)
        self.account.save()

        self.check_set_enemy(self.enemy_id)

    def test_wrong_enemy(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENEMY, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON)

    def test_wrong_format_of_enemy(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENEMY, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON)

    def test_set_outgame_enemy(self):
        enemy = persons_storage[self.enemy_id]
        enemy.move_out_game()
        enemy.save()

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.OUTGAME_PERSON)
        self.assertEqual(self.hero.preferences.enemy, None)

    def test_set_enemy(self):
        self.assertEqual(HeroPreferences.get_enemies_of(persons_storage[self.enemy_id], all=False), [])
        self.assertEqual(HeroPreferences.get_enemies_of(persons_storage[self.enemy_id], all=True), [])

        changed_at = self.hero.preferences.enemy_changed_at
        self.check_set_enemy(self.enemy_id)
        self.assertTrue(changed_at < self.hero.preferences.enemy_changed_at)

        self.assertEqual([hero.id for hero in HeroPreferences.get_enemies_of(persons_storage[self.enemy_id], all=False)], [])
        self.assertEqual([hero.id for hero in HeroPreferences.get_enemies_of(persons_storage[self.enemy_id], all=True)], [self.hero.id])

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        logic.save_hero(self.hero)

        self.assertEqual([hero.id for hero in HeroPreferences.get_enemies_of(persons_storage[self.enemy_id], all=False)], [self.hero.id])
        self.assertEqual([hero.id for hero in HeroPreferences.get_enemies_of(persons_storage[self.enemy_id], all=True)], [self.hero.id])

    def test_set_friend_as_enemy(self):
        self.hero.preferences.set_friend(persons_storage[self.friend_id])
        logic.save_hero(self.hero)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENEMY, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.ENEMY_AND_FRIEND)

    def check_change_enemy(self, new_enemy_id, expected_enemy_id, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ENEMY, new_enemy_id)
        self.assertEqual(self.hero.preferences.enemy.id, self.enemy_id)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        if expected_enemy_id is None:
            self.assertEqual(self.hero.preferences.enemy, None)
        else:
            self.assertEqual(self.hero.preferences.enemy.id, expected_enemy_id)
        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).enemy_id, expected_enemy_id)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_enemy(self):
        self.check_change_enemy(self.enemy_2_id, self.enemy_2_id, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_enemy_cooldown(self):
        self.check_change_enemy(self.enemy_2_id, self.enemy_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_enemy(self):
        self.check_change_enemy(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_enemy_cooldown(self):
        self.check_change_enemy(None, self.enemy_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    def test_get_enemies_number(self):
        hero_1 = self.hero

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = logic.load_hero(account_id=account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = logic.load_hero(account_id=account_id)

        person_1 = self.place_1.persons[0]
        person_2 = self.place_1.persons[-1]

        hero_1.preferences.set_enemy(person_1)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_1)

        hero_2.preferences.set_enemy(person_1)
        logic.save_hero(hero_2)

        hero_3.preferences.set_enemy(person_1)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_3)

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = logic.load_hero(account_id=account_id)
        hero_4.preferences.set_enemy(person_1)
        logic.save_hero(hero_4)

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        hero_5 = logic.load_hero(account_id=account_id)
        hero_5.preferences.set_enemy(person_1)
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_5)

        result, account_id, bundle_id = register_user('test_user_6', 'test_user_6@test.com', '111111')
        hero_6 = logic.load_hero(account_id=account_id)
        hero_6.preferences.set_enemy(person_1)
        hero_6.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        logic.save_hero(hero_6)

        self.assertEqual(HeroPreferences.count_enemies_of(person_1, all=False), 2)
        self.assertEqual(HeroPreferences.count_enemies_of(person_2, all=False), 0)

        self.assertEqual(HeroPreferences.count_enemies_of(person_1, all=True), 3)

        self.assertEqual(set([h.id for h in HeroPreferences.get_enemies_of(person_1, all=False)]), set([hero_1.id, hero_3.id]))
        self.assertEqual(set([h.id for h in HeroPreferences.get_enemies_of(person_1, all=True)]), set([hero_1.id, hero_2.id, hero_3.id]))

    def test_reset_enemy_on_highlevel_update(self):
        enemy = self.place_1.persons[0]

        self.hero.preferences.set_enemy(enemy)
        logic.save_hero(self.hero)

        enemy.move_out_game()
        enemy.save()

        self.storage.on_highlevel_data_updated()

        self.assertEqual(self.hero.preferences.enemy, None)


    def test_count_habit_values(self):
        hero_1 = self.hero
        hero_1.preferences.set_enemy(self.enemy)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.habit_honor.change(-1)
        hero_1.habit_peacefulness.change(1)
        logic.save_hero(hero_1)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = logic.load_hero(account_id=account_id)
        hero_2.preferences.set_enemy(self.enemy)
        hero_2.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_2.habit_honor.change(2)
        hero_2.habit_peacefulness.change(-2)
        logic.save_hero(hero_2)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = logic.load_hero(account_id=account_id)
        hero_3.preferences.set_enemy(self.enemy_2)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_3.habit_honor.change(-4)
        hero_3.habit_peacefulness.change(4)
        logic.save_hero(hero_3)

        result, account_id, bundle_id = register_user('test_user_4', 'test_user_4@test.com', '111111')
        hero_4 = logic.load_hero(account_id=account_id)
        hero_4.preferences.set_enemy(self.enemy)
        hero_4.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_4.habit_honor.change(8)
        hero_4.habit_peacefulness.change(-8)
        logic.save_hero(hero_4)

        self.assertEqual(HeroPreferences.count_habit_values(self.place_1, all=False), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=False), ((0, -4), (4, 0)))

        self.assertEqual(HeroPreferences.count_habit_values(self.place_1, all=True), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=True), ((0, -4), (4, 0)))



class HeroPreferencesEquipmentSlotTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.EQUIPMENT_SLOT

    def setUp(self):
        super(HeroPreferencesEquipmentSlotTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required
        logic.save_hero(self.hero)

        self.slot_1 = relations.EQUIPMENT_SLOT.HAND_PRIMARY
        self.slot_2 = relations.EQUIPMENT_SLOT.PLATE

    def test_preferences_serialization(self):
        self.hero.preferences.set_equipment_slot(self.slot_1)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_equipment_slot(self.slot_1)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.equipment_slot, self.slot_1)


    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, 'wrong_equip_slot')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.equipment_slot, None)

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_equipment_slot(self, slot_1):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.EQUIPMENT_SLOT , slot_1.value)
        self.assertEqual(self.hero.preferences.equipment_slot, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.equipment_slot, slot_1)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.EQUIPMENT_SLOT.purchase_type)
        self.account.save()

        self.check_set_equipment_slot(self.slot_1)


    def test_wrong_slot(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT)

    def test_wrong_forma_of_slot(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT)

    def test_set_equipment_slot(self):
        changed_at = self.hero.preferences.equipment_slot_changed_at
        self.check_set_equipment_slot(self.slot_1)
        self.assertTrue(changed_at < self.hero.preferences.equipment_slot_changed_at)

    def check_change_equipment_slot(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, new_slot.value if new_slot is not None else None)
        self.assertEqual(self.hero.preferences.equipment_slot, self.slot_1)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.equipment_slot, expected_slot)

        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).equipment_slot, expected_slot)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_equipment_slot(self):
        self.check_change_equipment_slot(self.slot_2, self.slot_2, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_equipment_slot_cooldown(self):
        self.check_change_equipment_slot(self.slot_2, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_equipment_slot(self):
        self.check_change_equipment_slot(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_equipment_slot_cooldown(self):
        self.check_change_equipment_slot(None, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesFavoriteItemTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.FAVORITE_ITEM

    def setUp(self):
        super(HeroPreferencesFavoriteItemTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.FAVORITE_ITEM.level_required
        logic.save_hero(self.hero)

        self.slot_1 = relations.EQUIPMENT_SLOT.HAND_PRIMARY
        self.slot_2 = relations.EQUIPMENT_SLOT.PLATE

    def test_preferences_serialization(self):
        self.hero.preferences.set_favorite_item(self.slot_1)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_favorite_item(self.slot_1)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.favorite_item, self.slot_1)


    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FAVORITE_ITEM, 'wrong_equip_slot')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.favorite_item, None)

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.FAVORITE_ITEM.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FAVORITE_ITEM, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def test_empty_slot(self):
        self.hero.equipment._remove_all()
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FAVORITE_ITEM, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.EMPTY_EQUIPMENT_SLOT)

    def check_set_favorite_item(self, slot_1):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FAVORITE_ITEM , slot_1.value)
        self.assertEqual(self.hero.preferences.favorite_item, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.favorite_item, slot_1)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.FAVORITE_ITEM.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.FAVORITE_ITEM.purchase_type)
        self.account.save()

        self.check_set_favorite_item(self.slot_1)


    def test_wrong_slot(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FAVORITE_ITEM, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT)

    def test_wrong_format_of_slot(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FAVORITE_ITEM, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT)

    def test_set_favorite_item(self):
        changed_at = self.hero.preferences.favorite_item_changed_at
        self.check_set_favorite_item(self.slot_1)
        self.assertTrue(changed_at < self.hero.preferences.favorite_item_changed_at)

    def check_change_favorite_item(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FAVORITE_ITEM, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.FAVORITE_ITEM, new_slot.value if new_slot is not None else None)
        self.assertEqual(self.hero.preferences.favorite_item, self.slot_1)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.favorite_item, expected_slot)

        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).favorite_item, expected_slot)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_favorite_item(self):
        self.check_change_favorite_item(self.slot_2, self.slot_2, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_favorite_item_cooldown(self):
        self.check_change_favorite_item(self.slot_2, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_favorite_item(self):
        self.check_change_favorite_item(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_favorite_item_cooldown(self):
        self.check_change_favorite_item(None, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)



class HeroPreferencesRiskLevelTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.RISK_LEVEL

    def setUp(self):
        super(HeroPreferencesRiskLevelTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.RISK_LEVEL.level_required
        logic.save_hero(self.hero)

        self.risk_1 = relations.RISK_LEVEL.VERY_HIGH
        self.risk_2 = relations.RISK_LEVEL.VERY_LOW

    def test_preferences_serialization(self):
        self.hero.preferences.set_risk_level(self.risk_1)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_risk_level(self.risk_1)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.risk_level, self.risk_1)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.RISK_LEVEL, 'wrong_risk_level')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertTrue(self.hero.preferences.risk_level.is_NORMAL )

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.RISK_LEVEL.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.RISK_LEVEL, self.risk_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)
        self.assertTrue(self.hero.preferences.risk_level.is_NORMAL )

    def check_set_risk_level(self, risk_1):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.RISK_LEVEL , risk_1.value)
        self.assertTrue(self.hero.preferences.risk_level.is_NORMAL)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.risk_level, risk_1)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.RISK_LEVEL.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.RISK_LEVEL.purchase_type)
        self.account.save()

        self.check_set_risk_level(self.risk_1)

    def test_wrong_risk_level(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.RISK_LEVEL, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_RISK_LEVEL)
        self.assertTrue(self.hero.preferences.risk_level.is_NORMAL )

    def test_wrong_format_of_risk_level(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.RISK_LEVEL, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_RISK_LEVEL)
        self.assertTrue(self.hero.preferences.risk_level.is_NORMAL )

    def test_set_risk_level(self):
        changed_at = self.hero.preferences.risk_level_changed_at
        self.check_set_risk_level(self.risk_1)
        self.assertTrue(changed_at < self.hero.preferences.risk_level_changed_at)

    def check_change_risk_level(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.RISK_LEVEL, self.risk_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.RISK_LEVEL, new_slot.value if new_slot is not None else None)
        self.assertEqual(self.hero.preferences.risk_level, self.risk_1)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.risk_level, expected_slot)

        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).risk_level, expected_slot)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_risk_level(self):
        self.check_change_risk_level(self.risk_2, self.risk_2, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_risk_level_cooldown(self):
        self.check_change_risk_level(self.risk_2, self.risk_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesArchetypeTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.ARCHETYPE

    def setUp(self):
        super(HeroPreferencesArchetypeTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.ARCHETYPE.level_required
        logic.save_hero(self.hero)

        self.mage = game_relations.ARCHETYPE.MAGICAL
        self.warior = game_relations.ARCHETYPE.PHYSICAL

    def test_preferences_serialization(self):
        self.hero.preferences.set_archetype(self.mage)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_archetype(self.mage)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.archetype, self.mage)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ARCHETYPE, 'wrong_archetype')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertTrue(self.hero.preferences.archetype.is_NEUTRAL )

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.ARCHETYPE.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ARCHETYPE, self.mage.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)
        self.assertTrue(self.hero.preferences.archetype.is_NEUTRAL )

    def check_set_archetype(self, archetype):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ARCHETYPE , archetype.value)
        self.assertTrue(self.hero.preferences.archetype.is_NEUTRAL)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.archetype, archetype)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.ARCHETYPE.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.ARCHETYPE.purchase_type)
        self.account.save()

        self.check_set_archetype(self.mage)

    def test_wrong_archetype(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ARCHETYPE, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ARCHETYPE)
        self.assertTrue(self.hero.preferences.archetype.is_NEUTRAL )

    def test_wrong_format_of_archetype(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ARCHETYPE, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ARCHETYPE)
        self.assertTrue(self.hero.preferences.archetype.is_NEUTRAL )

    def test_set_archetype(self):
        changed_at = self.hero.preferences.archetype_changed_at
        self.check_set_archetype(self.mage)
        self.assertTrue(changed_at < self.hero.preferences.archetype_changed_at)

    def check_change_archetype(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ARCHETYPE, self.mage.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.ARCHETYPE, new_slot.value if new_slot is not None else None)
        self.assertEqual(self.hero.preferences.archetype, self.mage)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.archetype, expected_slot)

        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).archetype, expected_slot)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_archetype(self):
        self.check_change_archetype(self.warior, self.warior, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_archetype_cooldown(self):
        self.check_change_archetype(self.warior, self.mage, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesCompanionDedicationTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.COMPANION_DEDICATION

    def setUp(self):
        super(HeroPreferencesCompanionDedicationTest, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.COMPANION_DEDICATION.level_required
        logic.save_hero(self.hero)

        self.egoism = relations.COMPANION_DEDICATION.EGOISM
        self.altruism = relations.COMPANION_DEDICATION.ALTRUISM

    def test_initialization(self):
        self.assertTrue(self.hero.preferences.companion_dedication.is_NORMAL)

    def test_preferences_serialization(self):
        self.hero.preferences.set_companion_dedication(self.egoism)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_companion_dedication(self.egoism)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.companion_dedication, self.egoism)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_DEDICATION, 'wrong_companion_dedication')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertTrue(self.hero.preferences.companion_dedication.is_NORMAL )

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.COMPANION_DEDICATION.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_DEDICATION, self.egoism.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)
        self.assertTrue(self.hero.preferences.companion_dedication.is_NORMAL)

    def check_set_companion_dedication(self, companion_dedication):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_DEDICATION , companion_dedication.value)
        self.assertTrue(self.hero.preferences.companion_dedication.is_NORMAL)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.companion_dedication, companion_dedication)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.COMPANION_DEDICATION.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.COMPANION_DEDICATION.purchase_type)
        self.account.save()

        self.check_set_companion_dedication(self.egoism)

    def test_wrong_companion_dedication(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_DEDICATION, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_COMPANION_DEDICATION)
        self.assertTrue(self.hero.preferences.companion_dedication.is_NORMAL )

    def test_wrong_format_of_companion_dedication(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_DEDICATION, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_COMPANION_DEDICATION)
        self.assertTrue(self.hero.preferences.companion_dedication.is_NORMAL )

    def test_set_companion_dedication(self):
        changed_at = self.hero.preferences.companion_dedication_changed_at
        self.check_set_companion_dedication(self.egoism)
        self.assertTrue(changed_at < self.hero.preferences.companion_dedication_changed_at)

    def check_change_companion_dedication(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_DEDICATION, self.egoism.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_DEDICATION, new_slot.value if new_slot is not None else None)
        self.assertEqual(self.hero.preferences.companion_dedication, self.egoism)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.companion_dedication, expected_slot)

        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).companion_dedication, expected_slot)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_companion_dedication(self):
        self.check_change_companion_dedication(self.altruism, self.altruism, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_companion_dedication_cooldown(self):
        self.check_change_companion_dedication(self.altruism, self.egoism, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesCompanionEmpathyTest(PreferencesTestMixin, TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.COMPANION_EMPATHY

    def setUp(self):
        super(HeroPreferencesCompanionEmpathyTest, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.COMPANION_EMPATHY.level_required
        logic.save_hero(self.hero)

        self.empath = relations.COMPANION_EMPATHY.EMPATH
        self.egocentric = relations.COMPANION_EMPATHY.EGOCENTRIC

    def test_initialization(self):
        self.assertTrue(self.hero.preferences.companion_empathy.is_ORDINAL)

    def test_preferences_serialization(self):
        self.hero.preferences.set_companion_empathy(self.empath)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_companion_empathy(self.empath)
        self.assertTrue(self.hero.preferences.updated)
        logic.save_hero(self.hero)
        self.assertFalse(self.hero.preferences.updated)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.companion_empathy, self.empath)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_EMPATHY, 'wrong_companion_empathy')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertTrue(self.hero.preferences.companion_empathy.is_ORDINAL )

    def test_wrong_level(self):
        self.assertTrue(relations.PREFERENCE_TYPE.COMPANION_EMPATHY.level_required > 1)
        self.hero.level = 1
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_EMPATHY, self.empath.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)
        self.assertTrue(self.hero.preferences.companion_empathy.is_ORDINAL)

    def check_set_companion_empathy(self, companion_empathy):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_EMPATHY , companion_empathy.value)
        self.assertTrue(self.hero.preferences.companion_empathy.is_ORDINAL)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.companion_empathy, companion_empathy)

    def test_purchased(self):
        self.assertTrue(relations.PREFERENCE_TYPE.COMPANION_EMPATHY.level_required > 1)
        self.hero.level = 1
        self.account.permanent_purchases.insert(relations.PREFERENCE_TYPE.COMPANION_EMPATHY.purchase_type)
        self.account.save()

        self.check_set_companion_empathy(self.empath)

    def test_wrong_companion_empathy(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_EMPATHY, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_COMPANION_EMPATHY)
        self.assertTrue(self.hero.preferences.companion_empathy.is_ORDINAL )

    def test_wrong_format_of_companion_empathy(self):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_EMPATHY, '3.5')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_COMPANION_EMPATHY)
        self.assertTrue(self.hero.preferences.companion_empathy.is_ORDINAL )

    def test_set_companion_empathy(self):
        changed_at = self.hero.preferences.companion_empathy_changed_at
        self.check_set_companion_empathy(self.empath)
        self.assertTrue(changed_at < self.hero.preferences.companion_empathy_changed_at)

    def check_change_companion_empathy(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_EMPATHY, self.empath.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, relations.PREFERENCE_TYPE.COMPANION_EMPATHY, new_slot.value if new_slot is not None else None)
        self.assertEqual(self.hero.preferences.companion_empathy, self.empath)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.companion_empathy, expected_slot)

        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).companion_empathy, expected_slot)

        self.assertEqual(reset_accessors_cache.call_count, 1 if expected_state.is_PROCESSED else 0)

    @mock.patch('the_tale.game.balance.constants.PREFERENCES_CHANGE_DELAY', 0)
    def test_change_companion_empathy(self):
        self.check_change_companion_empathy(self.egocentric, self.egocentric, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_companion_empathy_cooldown(self):
        self.check_change_companion_empathy(self.egocentric, self.empath, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)



class HeroPreferencesRequestsTest(TestCase):

    def setUp(self):
        super(HeroPreferencesRequestsTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = max(r.level_required for r in relations.PREFERENCE_TYPE.records) # maximum blocking level
        logic.save_hero(self.hero)

        register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.client = client.Client()

        self.mob_uuid = mobs_storage.all()[0].uuid
        self.mob_2_uuid = mobs_storage.all()[1].uuid

        self.place = place_1
        self.place_2 = place_2


    def tearDown(self):
        pass

    def test_preferences_dialog_energy_regeneration(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE.value))
        self.check_html_ok(response, texts=[record.text.capitalize() for record in relations.ENERGY_REGENERATION.records])


    def test_preferences_dialog_mob(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.MOB.value))

        texts = []

        for mob_record in mobs_storage.all():
            if mob_record.level <= self.hero.level:
                texts.append(('"%s"' % mob_record.uuid, 1))
            else:
                texts.append(('"%s"' % mob_record.uuid, 0))

        self.check_html_ok(response, texts=texts)


    def test_preferences_dialog_place(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.PLACE.value))

        texts = []

        for place in Place.objects.all():
            texts.append(('"%d"' % place.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_friend(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.FRIEND.value))

        texts = []

        for person in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            texts.append(('data-preference-id="%d"' % person.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_enemy(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.ENEMY.value))

        texts = []

        for person in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            texts.append(('data-preference-id="%d"' % person.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_risk_level(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.RISK_LEVEL.value))
        self.check_html_ok(response, texts=[r.text for r in relations.RISK_LEVEL.records])

    def test_preferences_dialog_archetype(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.ARCHETYPE.value))
        self.check_html_ok(response, texts=[r.text for r in game_relations.ARCHETYPE.records])

    def test_preferences_dialog_companion_dedication(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.COMPANION_DEDICATION.value))
        self.check_html_ok(response, texts=[r.text for r in relations.COMPANION_DEDICATION.records])

    def test_preferences_dialog_companion_empathy(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.COMPANION_EMPATHY.value))
        self.check_html_ok(response, texts=[r.text for r in relations.COMPANION_EMPATHY.records])


    def test_preferences_dialog_favorite_item(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.FAVORITE_ITEM.value))
        self.check_html_ok(response, texts=[self.hero.equipment.get(slot).name
                                            for slot in relations.EQUIPMENT_SLOT.records
                                            if self.hero.equipment.get(slot)])

    def test_preferences_dialog_unlogined(self):
        request_url = reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.ENEMY.value)
        self.check_redirect(request_url, login_page_url(request_url))

    def test_preferences_dialog_wrong_user(self):
        self.request_login('test_user_2@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % relations.PREFERENCE_TYPE.ENEMY.value))
        self.check_html_ok(response, texts=(('heroes.not_owner', 1),))

    def test_choose_preferences_unlogined(self):
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': relations.PREFERENCE_TYPE.MOB, 'preference_id': self.mob_uuid})
        self.check_ajax_error(response, 'common.login_required')

    def test_choose_preferences_wrong_user(self):
        self.request_login('test_user_2@test.com')
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': relations.PREFERENCE_TYPE.MOB, 'preference_id': self.mob_uuid})
        self.check_ajax_error(response, 'heroes.not_owner')

    def test_choose_preferences_success(self):
        self.assertEqual(PostponedTask.objects.all().count(), 0)
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': relations.PREFERENCE_TYPE.MOB, 'preference_id': self.mob_uuid})

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertEqual(PostponedTask.objects.all().count(), 1)

    def test_choose_preferences_remove_success(self):
        self.assertEqual(PostponedTask.objects.all().count(), 0)
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': relations.PREFERENCE_TYPE.MOB})

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertEqual(task.internal_logic.preference_id, None)

        self.assertEqual(PostponedTask.objects.all().count(), 1)
