# coding: utf-8
import mock
import datetime

from django.test import client
from django.core.urlresolvers import reverse

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import PostponedTask, PostponedTaskPrototype, FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.logic import register_user, login_url
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map

from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.mobs.models import MOB_RECORD_STATE

from the_tale.game.map.places.models import Place

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.balance import enums as e

from the_tale.game.persons.models import Person, PERSON_STATE
from the_tale.game.persons.storage import persons_storage

from the_tale.game.heroes.prototypes import HeroPrototype, HeroPreferencesPrototype
from the_tale.game.heroes.relations import PREFERENCE_TYPE, EQUIPMENT_SLOT, RISK_LEVEL
from the_tale.game.heroes.postponed_tasks import ChoosePreferencesTask, CHOOSE_PREFERENCES_TASK_STATE
from the_tale.game.heroes.preferences import HeroPreferences


class HeroPreferencesEnergyRegenerationTypeTest(TestCase):

    def setUp(self):
        super(HeroPreferencesEnergyRegenerationTypeTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE.level_required
        self.hero.preferences.set_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE, change_time=datetime.datetime.fromtimestamp(0))
        self.hero.save()

    def test_preferences_serialization(self):
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(self.hero.id, data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY)
        self.assertTrue(self.hero.preferences.updated)
        self.hero.save()
        self.assertFalse(self.hero.preferences.updated)
        self.hero.reload()
        self.assertEqual(self.hero.preferences.energy_regeneration_type, e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.place, None)

    def test_serialization(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(task.serialize(), ChoosePreferencesTask.deserialize(task.serialize()).serialize())

    # can not test wrong level, since energy regeneration choice available on 1 level
    def test_wrong_level(self):
        self.assertEqual(PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE.level_required, 1)

    # can not test purchased state, since energy regeneration choice available on 1 level
    def test_purchased(self):
        self.assertEqual(PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE.level_required, 1)

    def test_wrong_energy_regeneration_type(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_ENERGY_REGENERATION_TYPE)

    # can not test set energy regeneration type, since it must be always selected
    def test_set_energy_regeneration_typ(self):
        self.assertNotEqual(self.hero.preferences.energy_regeneration_type, None)

    def check_change_energy_regeneration_type(self, new_energy_regeneration_type, expected_energy_regeneration_type, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, new_energy_regeneration_type)
        self.assertNotEqual(self.hero.preferences.energy_regeneration_type, new_energy_regeneration_type)

        process_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED, process_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.energy_regeneration_type, expected_energy_regeneration_type)
        self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).energy_regeneration_type, expected_energy_regeneration_type)

    def test_change_energy_regeneration_type(self):
        self.check_change_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY, e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_energy_regeneration_type_cooldown(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, e.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.check_change_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY, e.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    def test_remove_energy_regeneration_type(self):
        self.check_change_energy_regeneration_type(None, e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE, CHOOSE_PREFERENCES_TASK_STATE.UNSPECIFIED_PREFERENCE)

    def test_remove_energy_regeneration_type_cooldown(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, e.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.check_change_energy_regeneration_type(None, e.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesMobTest(TestCase):

    def setUp(self):
        super(HeroPreferencesMobTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = PREFERENCE_TYPE.MOB.level_required
        self.hero._model.save()

        self.mob_uuid = mobs_storage.get_available_mobs_list(level=self.hero.level)[0].uuid
        self.mob_2_uuid = mobs_storage.get_available_mobs_list(level=self.hero.level)[1].uuid

    def test_preferences_serialization(self):
        self.hero.preferences.set_mob(mobs_storage.all()[0])
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(self.hero.id, data).serialize())

    def test_save(self):
        mob = mobs_storage.all()[0]
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_mob(mob)
        self.assertTrue(self.hero.preferences.updated)
        self.hero.save()
        self.assertFalse(self.hero.preferences.updated)
        self.hero.reload()
        self.assertEqual(self.hero.preferences.mob.id, mob.id)

    def test_reset_mob_when_it_disabled(self):
        mob_record = mobs_storage.all()[0]
        self.hero.preferences.set_mob(mob_record)

        self.assertEqual(self.hero.preferences.mob, mob_record)

        mob_record.state = MOB_RECORD_STATE.DISABLED
        mob_record.save()

        self.assertEqual(self.hero.preferences.mob, None)
        self.assertEqual(self.hero.preferences.mob_changed_at, datetime.datetime.fromtimestamp(0))


    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, 'wrong_mob_uuid')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.mob, None)

    def test_wrong_level(self):
        self.assertTrue(PREFERENCE_TYPE.MOB.level_required > 1)
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, self.mob_uuid)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_mob(self, mob_uuid):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, mob_uuid)

        self.assertEqual(self.hero.preferences.mob, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.mob.uuid, mob_uuid)

    def test_purchased(self):
        self.assertTrue(PREFERENCE_TYPE.MOB.level_required > 1)
        self.hero._model.level = 1
        self.account.permanent_purchases.insert(PREFERENCE_TYPE.MOB.purchase_type)
        self.account.save()

        self.check_set_mob(self.mob_uuid)


    def test_wrong_mob(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, 'wrong_mob_uuid')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_MOB)

    def test_wrong_mob_level(self):
        mobs_storage.all()[1].level = self.hero.level + 1

        wrong_mob_uuid = None
        for mob_record in mobs_storage.all():
            if mob_record.state._is_ENABLED and mob_record.level > self.hero.level:
                wrong_mob_uuid = mob_record.uuid
                break

        self.assertTrue(wrong_mob_uuid)

        self.assertEqual(mobs_storage.all()[1].uuid, wrong_mob_uuid)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, wrong_mob_uuid)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LARGE_MOB_LEVEL)
        self.assertEqual(self.hero.preferences.mob, None)

    def test_mob_not_in_game(self):
        mob_record = mobs_storage.all()[1]
        mob_record.state = MOB_RECORD_STATE.DISABLED
        mob_record.save()

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, mob_record.uuid)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.MOB_NOT_IN_GAME)
        self.assertEqual(self.hero.preferences.mob, None)


    def test_set_mob(self):
        changed_at = self.hero.preferences.mob_changed_at
        self.check_set_mob(self.mob_uuid)
        self.assertTrue(changed_at < self.hero.preferences.mob_changed_at)

    def check_change_mob(self, new_mob_uuid, expected_mob_uuid, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, self.mob_uuid)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, new_mob_uuid)
        self.assertEqual(self.hero.preferences.mob.uuid, self.mob_uuid)

        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED, task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(task.state, expected_state)
        if self.hero.preferences.mob is None:
            self.assertEqual(expected_mob_uuid, None)
            self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).mob_id, None)
        else:
            self.assertEqual(self.hero.preferences.mob.uuid, expected_mob_uuid)
            self.assertEqual(mobs_storage[HeroPreferencesPrototype.get_by_hero_id(self.hero.id).mob_id].uuid, expected_mob_uuid)


    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_mob(self):
        self.check_change_mob(self.mob_2_uuid, self.mob_2_uuid, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_mob_cooldown(self):
        self.check_change_mob(self.mob_2_uuid, self.mob_uuid, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_mob(self):
        self.check_change_mob(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_mob_cooldown(self):
        self.check_change_mob(None, self.mob_uuid, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesPlaceTest(TestCase):

    def setUp(self):
        super(HeroPreferencesPlaceTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = PREFERENCE_TYPE.PLACE.level_required
        self.hero.save()

        self.place = place_1
        self.place_2 = place_2

    def test_preferences_serialization(self):
        self.hero.preferences.set_place(self.place)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(self.hero.id, data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_place(self.place)
        self.assertTrue(self.hero.preferences.updated)
        self.hero.save()
        self.assertFalse(self.hero.preferences.updated)
        self.hero.reload()
        self.assertEqual(self.hero.preferences.place.id, self.place.id)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.place, None)

    def test_wrong_level(self):
        self.assertTrue(PREFERENCE_TYPE.PLACE.level_required > 1)
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, self.place.id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_place(self, place):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, place.id)
        self.assertEqual(self.hero.preferences.place, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.place.id, place.id)

    def test_purchased(self):
        self.assertTrue(PREFERENCE_TYPE.PLACE.level_required > 1)
        self.hero._model.level = 1
        self.account.permanent_purchases.insert(PREFERENCE_TYPE.PLACE.purchase_type)
        self.account.save()

        self.check_set_place(self.place)

    def test_wrong_place(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PLACE)

    def test_set_place(self):
        self.assertEqual(HeroPreferences.get_citizens_of(self.place), [])
        changed_at = self.hero.preferences.place_changed_at

        self.check_set_place(self.place)

        self.assertTrue(changed_at < self.hero.preferences.place_changed_at)

        self.assertEqual([hero.id for hero in HeroPreferences.get_citizens_of(self.place)], [])

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        self.hero.save()

        self.assertEqual([hero.id for hero in HeroPreferences.get_citizens_of(self.place)], [self.hero.id])

    def check_change_place(self, new_place_id, expected_place_id, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, self.place.id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, new_place_id)
        self.assertEqual(self.hero.preferences.place.id, self.place.id)

        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(task.state, expected_state)

        if expected_place_id is None:
            self.assertEqual(self.hero.preferences.place, None)
        else:
            self.assertEqual(self.hero.preferences.place.id, expected_place_id)
        self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).place_id, expected_place_id)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_place(self):
        self.check_change_place(self.place_2.id, self.place_2.id, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_place_cooldown(self):
        self.check_change_place(self.place_2.id, self.place.id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_place(self):
        self.check_change_place(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_place_cooldown(self):
        self.check_change_place(None, self.place.id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    def test_get_citizens_number(self):
        hero_1 = self.hero

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = HeroPrototype.get_by_account_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = HeroPrototype.get_by_account_id(account_id)

        hero_1.preferences.set_place(self.place)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.save()

        hero_2.preferences.set_place(self.place)
        hero_2.save()

        hero_3.preferences.set_place(self.place)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_3.save()

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = HeroPrototype.get_by_account_id(account_id)
        hero_4.preferences.set_place(self.place)
        hero_4.save()

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        hero_5 = HeroPrototype.get_by_account_id(account_id)
        hero_5.preferences.set_place(self.place)
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_5.save()

        self.assertEqual(HeroPreferences.count_citizens_of(self.place), 2)
        self.assertEqual(HeroPreferences.count_citizens_of(self.place_2), 0)

        self.assertEqual(set([h.id for h in HeroPreferences.get_citizens_of(self.place)]), set([hero_1.id, hero_3.id]))


class HeroPreferencesFriendTest(TestCase):

    def setUp(self):
        super(HeroPreferencesFriendTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = PREFERENCE_TYPE.FRIEND.level_required
        self.hero._model.save()

        self.friend_id = Person.objects.all()[0].id
        self.friend_2_id = Person.objects.all()[1].id
        self.enemy_id = Person.objects.all()[2].id

    def test_preferences_serialization(self):
        self.hero.preferences.set_friend(persons_storage[self.friend_id])
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(self.hero.id, data).serialize())

    def test_save(self):
        friend = persons_storage[self.friend_id]

        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_friend(friend)
        self.assertTrue(self.hero.preferences.updated)
        self.hero.save()
        self.assertFalse(self.hero.preferences.updated)
        self.hero.reload()
        self.assertEqual(self.hero.preferences.friend.id, friend.id)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.friend, None)

    def test_wrong_level(self):
        self.assertTrue(PREFERENCE_TYPE.FRIEND.level_required > 1)
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_friend(self, friend_id):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, friend_id)
        self.assertEqual(self.hero.preferences.friend, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.friend.id, friend_id)

    def test_purchased(self):
        self.assertTrue(PREFERENCE_TYPE.FRIEND.level_required > 1)
        self.hero._model.level = 1
        self.account.permanent_purchases.insert(PREFERENCE_TYPE.FRIEND.purchase_type)
        self.account.save()

        self.check_set_friend(self.friend_id)

    def test_wrong_friend(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON)

    def test_set_enemy_as_friend(self):
        self.hero.preferences.set_enemy(persons_storage[self.enemy_id])
        self.hero.save()

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.ENEMY_AND_FRIEND)

    def test_set_outgame_friend(self):
        friend = persons_storage[self.friend_id]
        friend.move_out_game()
        friend.save()

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.OUTGAME_PERSON)
        self.assertEqual(self.hero.preferences.friend, None)


    def test_set_friend(self):
        self.assertEqual(HeroPreferences.get_friends_of(persons_storage[self.friend_id]), [])
        changed_at = self.hero.preferences.friend_changed_at
        self.check_set_friend(self.friend_id)

        self.assertTrue(changed_at < self.hero.preferences.friend_changed_at)

        self.assertEqual([hero.id for hero in HeroPreferences.get_friends_of(persons_storage[self.friend_id])], [])

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        self.hero.save()

        self.assertEqual([hero.id for hero in HeroPreferences.get_friends_of(persons_storage[self.friend_id])], [self.hero.id])

    def check_change_friend(self, new_friend_id, expected_friend_id, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, new_friend_id)
        self.assertEqual(self.hero.preferences.friend.id, self.friend_id)
        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        if expected_friend_id is None:
            self.assertEqual(self.hero.preferences.friend, None)
        else:
            self.assertEqual(self.hero.preferences.friend.id, expected_friend_id)
        self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).friend_id, expected_friend_id)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_friend(self):
        self.check_change_friend(self.friend_2_id, self.friend_2_id, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_friend_cooldownd(self):
        self.check_change_friend(self.friend_2_id, self.friend_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_friend(self):
        self.check_change_friend(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_friend_cooldown(self):
        self.check_change_friend(None, self.friend_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    def test_get_friends_number(self):
        hero_1 = self.hero

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = HeroPrototype.get_by_account_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = HeroPrototype.get_by_account_id(account_id)

        person_1 = self.place_1.persons[0]
        person_2 = self.place_1.persons[-1]

        hero_1.preferences.set_friend(person_1)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.save()

        hero_2.preferences.set_friend(person_1)
        hero_2.save()

        hero_3.preferences.set_friend(person_1)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_3.save()

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = HeroPrototype.get_by_account_id(account_id)
        hero_4.preferences.set_friend(person_1)
        hero_4.save()

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        hero_5 = HeroPrototype.get_by_account_id(account_id)
        hero_5.preferences.set_friend(person_1)
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_5.save()

        self.assertEqual(HeroPreferences.count_friends_of(person_1), 2)
        self.assertEqual(HeroPreferences.count_friends_of(person_2), 0)

        self.assertEqual(set([h.id for h in HeroPreferences.get_friends_of(person_1)]), set([hero_1.id, hero_3.id]))

    def test_reset_friend_on_highlevel_update(self):
        friend = self.place_1.persons[0]

        self.hero.preferences.set_friend(friend)
        self.hero.save()

        friend.move_out_game()
        friend.save()

        self.storage.on_highlevel_data_updated()

        self.assertEqual(self.hero.preferences.friend, None)



class HeroPreferencesEnemyTest(TestCase):

    def setUp(self):
        super(HeroPreferencesEnemyTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = PREFERENCE_TYPE.ENEMY.level_required
        self.hero._model.save()

        self.enemy_id = Person.objects.all()[0].id
        self.enemy_2_id = Person.objects.all()[1].id
        self.friend_id = Person.objects.all()[2].id

    def test_preferences_serialization(self):
        self.hero.preferences.set_enemy(persons_storage[self.enemy_id])
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(self.hero.id, data).serialize())

    def test_save(self):
        enemy = persons_storage[self.enemy_id]

        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_enemy(enemy)
        self.assertTrue(self.hero.preferences.updated)
        self.hero.save()
        self.assertFalse(self.hero.preferences.updated)
        self.hero.reload()
        self.assertEqual(self.hero.preferences.enemy.id, enemy.id)


    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.enemy, None)

    def test_wrong_level(self):
        self.assertTrue(PREFERENCE_TYPE.ENEMY.level_required > 1)
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_enemy(self, enemy_id):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, enemy_id)
        self.assertEqual(self.hero.preferences.enemy, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.enemy.id, enemy_id)

    def test_purchased(self):
        self.assertTrue(PREFERENCE_TYPE.ENEMY.level_required > 1)
        self.hero._model.level = 1
        self.account.permanent_purchases.insert(PREFERENCE_TYPE.ENEMY.purchase_type)
        self.account.save()

        self.check_set_enemy(self.enemy_id)

    def test_wrong_enemy(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON)

    def test_set_outgame_enemy(self):
        enemy = persons_storage[self.enemy_id]
        enemy.move_out_game()
        enemy.save()

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.OUTGAME_PERSON)
        self.assertEqual(self.hero.preferences.enemy, None)

    def test_set_enemy(self):
        self.assertEqual(HeroPreferences.get_enemies_of(persons_storage[self.enemy_id]), [])
        changed_at = self.hero.preferences.enemy_changed_at
        self.check_set_enemy(self.enemy_id)
        self.assertTrue(changed_at < self.hero.preferences.enemy_changed_at)
        self.assertEqual([hero.id for hero in HeroPreferences.get_enemies_of(persons_storage[self.enemy_id])], [])

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        self.hero.save()

        self.assertEqual([hero.id for hero in HeroPreferences.get_enemies_of(persons_storage[self.enemy_id])], [self.hero.id])

    def test_set_friend_as_enemy(self):
        self.hero.preferences.set_friend(persons_storage[self.friend_id])
        self.hero.save()

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.ENEMY_AND_FRIEND)

    def check_change_enemy(self, new_enemy_id, expected_enemy_id, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, new_enemy_id)
        self.assertEqual(self.hero.preferences.enemy.id, self.enemy_id)
        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        if expected_enemy_id is None:
            self.assertEqual(self.hero.preferences.enemy, None)
        else:
            self.assertEqual(self.hero.preferences.enemy.id, expected_enemy_id)
        self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).enemy_id, expected_enemy_id)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_enemy(self):
        self.check_change_enemy(self.enemy_2_id, self.enemy_2_id, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_enemy_cooldown(self):
        self.check_change_enemy(self.enemy_2_id, self.enemy_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_enemy(self):
        self.check_change_enemy(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_enemy_cooldown(self):
        self.check_change_enemy(None, self.enemy_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    def test_get_enemies_number(self):
        hero_1 = self.hero

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = HeroPrototype.get_by_account_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = HeroPrototype.get_by_account_id(account_id)

        person_1 = self.place_1.persons[0]
        person_2 = self.place_1.persons[-1]

        hero_1.preferences.set_enemy(person_1)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.save()

        hero_2.preferences.set_enemy(person_1)
        hero_2.save()

        hero_3.preferences.set_enemy(person_1)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_3.save()

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = HeroPrototype.get_by_account_id(account_id)
        hero_4.preferences.set_enemy(person_1)
        hero_4.save()

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        hero_5 = HeroPrototype.get_by_account_id(account_id)
        hero_5.preferences.set_enemy(person_1)
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_5.save()

        self.assertEqual(HeroPreferences.count_enemies_of(person_1), 2)
        self.assertEqual(HeroPreferences.count_enemies_of(person_2), 0)

        self.assertEqual(set([h.id for h in HeroPreferences.get_enemies_of(person_1)]), set([hero_1.id, hero_3.id]))

    def test_reset_enemy_on_highlevel_update(self):
        enemy = self.place_1.persons[0]

        self.hero.preferences.enemy_id = enemy.id
        self.hero.save()

        enemy.move_out_game()
        enemy.save()

        self.storage.on_highlevel_data_updated()

        self.assertEqual(self.hero.preferences.enemy, None)



class HeroPreferencesEquipmentSlotTest(TestCase):

    def setUp(self):
        super(HeroPreferencesEquipmentSlotTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required
        self.hero._model.save()

        self.slot_1 = EQUIPMENT_SLOT.HAND_PRIMARY
        self.slot_2 = EQUIPMENT_SLOT.PLATE

    def test_preferences_serialization(self):
        self.hero.preferences.set_equipment_slot(self.slot_1)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(self.hero.id, data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_equipment_slot(self.slot_1)
        self.assertTrue(self.hero.preferences.updated)
        self.hero.save()
        self.assertFalse(self.hero.preferences.updated)
        self.hero.reload()
        self.assertEqual(self.hero.preferences.equipment_slot, self.slot_1)


    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, 'wrong_equip_slot')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.equipment_slot, None)

    def test_wrong_level(self):
        self.assertTrue(PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required > 1)
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def check_set_equipment_slot(self, slot_1):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT , slot_1.value)
        self.assertEqual(self.hero.preferences.equipment_slot, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.equipment_slot, slot_1)

    def test_purchased(self):
        self.assertTrue(PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required > 1)
        self.hero._model.level = 1
        self.account.permanent_purchases.insert(PREFERENCE_TYPE.EQUIPMENT_SLOT.purchase_type)
        self.account.save()

        self.check_set_equipment_slot(self.slot_1)


    def test_wrong_slot(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT)

    def test_set_equipment_slot(self):
        changed_at = self.hero.preferences.equipment_slot_changed_at
        self.check_set_equipment_slot(self.slot_1)
        self.assertTrue(changed_at < self.hero.preferences.equipment_slot_changed_at)

    def check_change_equipment_slot(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, new_slot.value if new_slot is not None else None)
        self.assertEqual(self.hero.preferences.equipment_slot, self.slot_1)
        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.equipment_slot, expected_slot)

        self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).equipment_slot, expected_slot)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_equipment_slot(self):
        self.check_change_equipment_slot(self.slot_2, self.slot_2, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_equipment_slot_cooldown(self):
        self.check_change_equipment_slot(self.slot_2, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_equipment_slot(self):
        self.check_change_equipment_slot(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_equipment_slot_cooldown(self):
        self.check_change_equipment_slot(None, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesFavoriteItemTest(TestCase):

    def setUp(self):
        super(HeroPreferencesFavoriteItemTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = PREFERENCE_TYPE.FAVORITE_ITEM.level_required
        self.hero._model.save()

        self.slot_1 = EQUIPMENT_SLOT.HAND_PRIMARY
        self.slot_2 = EQUIPMENT_SLOT.PLATE

    def test_preferences_serialization(self):
        self.hero.preferences.set_favorite_item(self.slot_1)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(self.hero.id, data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_favorite_item(self.slot_1)
        self.assertTrue(self.hero.preferences.updated)
        self.hero.save()
        self.assertFalse(self.hero.preferences.updated)
        self.hero.reload()
        self.assertEqual(self.hero.preferences.favorite_item, self.slot_1)


    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FAVORITE_ITEM, 'wrong_equip_slot')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.favorite_item, None)

    def test_wrong_level(self):
        self.assertTrue(PREFERENCE_TYPE.FAVORITE_ITEM.level_required > 1)
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FAVORITE_ITEM, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def test_empty_slot(self):
        self.hero.equipment._remove_all()
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FAVORITE_ITEM, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.EMPTY_EQUIPMENT_SLOT)

    def check_set_favorite_item(self, slot_1):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FAVORITE_ITEM , slot_1.value)
        self.assertEqual(self.hero.preferences.favorite_item, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.favorite_item, slot_1)

    def test_purchased(self):
        self.assertTrue(PREFERENCE_TYPE.FAVORITE_ITEM.level_required > 1)
        self.hero._model.level = 1
        self.account.permanent_purchases.insert(PREFERENCE_TYPE.FAVORITE_ITEM.purchase_type)
        self.account.save()

        self.check_set_favorite_item(self.slot_1)


    def test_wrong_slot(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FAVORITE_ITEM, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT)

    def test_set_favorite_item(self):
        changed_at = self.hero.preferences.favorite_item_changed_at
        self.check_set_favorite_item(self.slot_1)
        self.assertTrue(changed_at < self.hero.preferences.favorite_item_changed_at)

    def check_change_favorite_item(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FAVORITE_ITEM, self.slot_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FAVORITE_ITEM, new_slot.value if new_slot is not None else None)
        self.assertEqual(self.hero.preferences.favorite_item, self.slot_1)
        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.favorite_item, expected_slot)

        self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).favorite_item, expected_slot)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_favorite_item(self):
        self.check_change_favorite_item(self.slot_2, self.slot_2, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_favorite_item_cooldown(self):
        self.check_change_favorite_item(self.slot_2, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_favorite_item(self):
        self.check_change_favorite_item(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_favorite_item_cooldown(self):
        self.check_change_favorite_item(None, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)



class HeroPreferencesRiskLevelTest(TestCase):

    def setUp(self):
        super(HeroPreferencesRiskLevelTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = PREFERENCE_TYPE.RISK_LEVEL.level_required
        self.hero._model.save()

        self.risk_1 = RISK_LEVEL.VERY_HIGH
        self.risk_2 = RISK_LEVEL.VERY_LOW

    def test_preferences_serialization(self):
        self.hero.preferences.set_risk_level(self.risk_1)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(self.hero.id, data).serialize())

    def test_save(self):
        self.assertFalse(self.hero.preferences.updated)
        self.hero.preferences.set_risk_level(self.risk_1)
        self.assertTrue(self.hero.preferences.updated)
        self.hero.save()
        self.assertFalse(self.hero.preferences.updated)
        self.hero.reload()
        self.assertEqual(self.hero.preferences.risk_level, self.risk_1)

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.RISK_LEVEL, 'wrong_risk_level')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertTrue(self.hero.preferences.risk_level._is_NORMAL )

    def test_wrong_level(self):
        self.assertTrue(PREFERENCE_TYPE.RISK_LEVEL.level_required > 1)
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.RISK_LEVEL, self.risk_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)
        self.assertTrue(self.hero.preferences.risk_level._is_NORMAL )

    def check_set_risk_level(self, risk_1):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.RISK_LEVEL , risk_1.value)
        self.assertTrue(self.hero.preferences.risk_level._is_NORMAL)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.risk_level, risk_1)

    def test_purchased(self):
        self.assertTrue(PREFERENCE_TYPE.RISK_LEVEL.level_required > 1)
        self.hero._model.level = 1
        self.account.permanent_purchases.insert(PREFERENCE_TYPE.RISK_LEVEL.purchase_type)
        self.account.save()

        self.check_set_risk_level(self.risk_1)

    def test_wrong_risk_level(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.RISK_LEVEL, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_RISK_LEVEL)
        self.assertTrue(self.hero.preferences.risk_level._is_NORMAL )

    def test_set_risk_level(self):
        changed_at = self.hero.preferences.risk_level_changed_at
        self.check_set_risk_level(self.risk_1)
        self.assertTrue(changed_at < self.hero.preferences.risk_level_changed_at)

    def check_change_risk_level(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.RISK_LEVEL, self.risk_1.value)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.RISK_LEVEL, new_slot.value if new_slot is not None else None)
        self.assertEqual(self.hero.preferences.risk_level, self.risk_1)
        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.risk_level, expected_slot)

        self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).risk_level, expected_slot)

    @mock.patch('the_tale.game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_risk_level(self):
        self.check_change_risk_level(self.risk_2, self.risk_2, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_risk_level_cooldown(self):
        self.check_change_risk_level(self.risk_2, self.risk_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesRequestsTest(TestCase):

    def setUp(self):
        super(HeroPreferencesRequestsTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero._model.level = max(r.level_required for r in PREFERENCE_TYPE._records) # maximum blocking level
        self.hero._model.save()

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
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE.value))
        self.check_html_ok(response, texts=[text.capitalize() for text in e.ANGEL_ENERGY_REGENERATION_TYPES._ID_TO_TEXT.values()])


    def test_preferences_dialog_mob(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.MOB.value))

        texts = []

        for mob_record in mobs_storage.all():
            if mob_record.level <= self.hero.level:
                texts.append(('"%s"' % mob_record.uuid, 1))
            else:
                texts.append(('"%s"' % mob_record.uuid, 0))

        self.check_html_ok(response, texts=texts)


    def test_preferences_dialog_place(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.PLACE.value))

        texts = []

        for place in Place.objects.all():
            texts.append(('"%d"' % place.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_friend(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.FRIEND.value))

        texts = []

        for person in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            texts.append(('data-preference-id="%d"' % person.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_enemy(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.ENEMY.value))

        texts = []

        for person in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            texts.append(('data-preference-id="%d"' % person.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_risk_level(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.RISK_LEVEL.value))
        self.check_html_ok(response, texts=[r.text for r in RISK_LEVEL._records])

    def test_preferences_dialog_favorite_item(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.FAVORITE_ITEM.value))
        self.check_html_ok(response, texts=[self.hero.equipment.get(slot).name
                                            for slot in EQUIPMENT_SLOT._records
                                            if self.hero.equipment.get(slot)])

    def test_preferences_dialog_unlogined(self):
        request_url = reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.ENEMY.value)
        self.check_redirect(request_url, login_url(request_url))

    def test_preferences_dialog_wrong_user(self):
        self.request_login('test_user_2@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.ENEMY.value))
        self.check_html_ok(response, texts=(('heroes.not_owner', 1),))

    def test_choose_preferences_unlogined(self):
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_uuid})
        self.check_ajax_error(response, 'common.login_required')

    def test_choose_preferences_wrong_user(self):
        self.request_login('test_user_2@test.com')
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_uuid})
        self.check_ajax_error(response, 'heroes.not_owner')

    def test_choose_preferences_success(self):
        self.assertEqual(PostponedTask.objects.all().count(), 0)
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_uuid})

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertEqual(PostponedTask.objects.all().count(), 1)

    def test_choose_preferences_remove_success(self):
        self.assertEqual(PostponedTask.objects.all().count(), 0)
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB})

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertEqual(task.internal_logic.preference_id, None)

        self.assertEqual(PostponedTask.objects.all().count(), 1)
