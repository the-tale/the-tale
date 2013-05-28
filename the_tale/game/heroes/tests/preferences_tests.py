# coding: utf-8
import mock
import datetime

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase
from common.postponed_tasks import PostponedTask, PostponedTaskPrototype, FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from accounts.logic import register_user, login_url

from game.logic import create_test_map

from game.mobs.storage import mobs_storage
from game.mobs.models import MOB_RECORD_STATE

from game.map.places.models import Place

from game.logic_storage import LogicStorage

from game.balance import constants as c, enums as e

from game.persons.models import Person, PERSON_STATE
from game.persons.storage import persons_storage

from game.heroes.prototypes import HeroPrototype
from game.heroes.models import PREFERENCE_TYPE
from game.heroes.exceptions import HeroException
from game.heroes.bag import SLOTS
from game.heroes.postponed_tasks import ChoosePreferencesTask, CHOOSE_PREFERENCES_TASK_STATE
from game.heroes.preferences import HeroPreferences



class HeroPreferencesEnergyRegenerationTypeTest(TestCase):

    def setUp(self):
        super(HeroPreferencesEnergyRegenerationTypeTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.hero._model.level = c.CHARACTER_PREFERENCES_ENERGY_REGENERATION_TYPE_LEVEL_REQUIRED
        self.hero._model.pref_energy_regeneration_type = e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE
        self.hero._model.save()

    def tearDown(self):
        pass

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.place_id, None)

    def test_serialization(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(task.serialize(), ChoosePreferencesTask.deserialize(task.serialize()).serialize())

    # can not test wrong level, since energy regeneration choice available on 1 level
    def test_wrong_level(self):
        self.assertEqual(c.CHARACTER_PREFERENCES_ENERGY_REGENERATION_TYPE_LEVEL_REQUIRED, 1)

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
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.hero._model.level = c.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED
        self.hero._model.save()

        self.mob_uuid = mobs_storage.get_available_mobs_list(level=self.hero.level)[0].uuid
        self.mob_2_uuid = mobs_storage.get_available_mobs_list(level=self.hero.level)[1].uuid

    def tearDown(self):
        pass

    def test_reset_mob_when_it_disabled(self):
        mob_record = mobs_storage.all()[0]
        self.hero.preferences.mob = mob_record

        self.assertEqual(self.hero.preferences.mob, mob_record)

        mob_record.state = MOB_RECORD_STATE.DISABLED
        mob_record.save()

        self.assertEqual(self.hero.preferences.mob, None)
        self.assertEqual(self.hero.preferences.mob_changed_at, datetime.datetime(2000, 1, 1))


    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, 'wrong_mob_uuid')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.mob, None)

    def test_wrong_level(self):
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, self.mob_uuid)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def test_wrong_mob(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, 'wrong_mob_uuid')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_MOB)

    def test_wrong_preference(self):
        task = ChoosePreferencesTask(self.hero.id, 666, self.mob_uuid)
        self.assertRaises(HeroException, task.process, FakePostpondTaskPrototype(), self.storage)

    def test_wrong_mob_level(self):
        mobs_storage.all()[1].level = self.hero.level + 1

        wrong_mob_uuid = None
        for mob_record in mobs_storage.all():
            if mob_record.state.is_enabled and mob_record.level > self.hero.level:
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
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.MOB, self.mob_uuid)
        self.assertEqual(self.hero.preferences.mob, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.mob.uuid, self.mob_uuid)
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
        else:
            self.assertEqual(self.hero.preferences.mob.uuid, expected_mob_uuid)


    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_mob(self):
        self.check_change_mob(self.mob_2_uuid, self.mob_2_uuid, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_mob_cooldown(self):
        self.check_change_mob(self.mob_2_uuid, self.mob_uuid, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_mob(self):
        self.check_change_mob(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_mob_cooldown(self):
        self.check_change_mob(None, self.mob_uuid, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)


class HeroPreferencesPlaceTest(TestCase):

    def setUp(self):
        super(HeroPreferencesPlaceTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.hero._model.level = c.CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED
        self.hero.save()

        self.place = place_1
        self.place_2 = place_2

    def tearDown(self):
        pass

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.place_id, None)

    def test_wrong_level(self):
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, self.place.id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def test_wrong_place(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PLACE)

    def test_set_place(self):
        self.assertEqual(HeroPreferences.get_citizens_of(self.place), [])
        changed_at = self.hero.preferences.place_changed_at
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, self.place.id)
        self.assertEqual(self.hero.preferences.place_id, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.place_id, self.place.id)
        self.assertTrue(changed_at < self.hero.preferences.place_changed_at)

        self.assertEqual([hero.id for hero in HeroPreferences.get_citizens_of(self.place)], [])

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        self.hero.save()

        self.assertEqual([hero.id for hero in HeroPreferences.get_citizens_of(self.place)], [self.hero.id])

    def check_change_place(self, new_place_id, expected_place_id, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, self.place.id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.PLACE, new_place_id)
        self.assertEqual(self.hero.preferences.place_id, self.place.id)

        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.place_id, expected_place_id)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_place(self):
        self.check_change_place(self.place_2.id, self.place_2.id, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_place_cooldown(self):
        self.check_change_place(self.place_2.id, self.place.id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
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

        hero_1.preferences.place_id = self.place.id
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.save()

        hero_2.preferences.place_id = self.place.id
        hero_2.save()

        hero_3.preferences.place_id = self.place.id
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_3.save()

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = HeroPrototype.get_by_account_id(account_id)
        hero_4.preferences.place_id = self.place.id
        hero_4.save()

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        hero_5 = HeroPrototype.get_by_account_id(account_id)
        hero_5.preferences.place_id = self.place.id
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
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.hero._model.level = c.CHARACTER_PREFERENCES_FRIEND_LEVEL_REQUIRED
        self.hero._model.save()

        self.friend_id = Person.objects.all()[0].id
        self.friend_2_id = Person.objects.all()[1].id
        self.enemy_id = Person.objects.all()[2].id

    def tearDown(self):
        pass

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.friend_id, None)

    def test_wrong_level(self):
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def test_wrong_friend(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, 666)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_PERSON)

    def test_set_enemy_as_friend(self):
        self.hero.preferences.enemy_id = self.enemy_id
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
        self.assertEqual(self.hero.preferences.friend_id, None)


    def test_set_friend(self):
        self.assertEqual(HeroPreferences.get_friends_of(persons_storage[self.friend_id]), [])
        changed_at = self.hero.preferences.friend_changed_at
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(self.hero.preferences.friend_id, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.friend_id, self.friend_id)
        self.assertTrue(changed_at < self.hero.preferences.friend_changed_at)

        self.assertEqual([hero.id for hero in HeroPreferences.get_friends_of(persons_storage[self.friend_id])], [])

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        self.hero.save()

        self.assertEqual([hero.id for hero in HeroPreferences.get_friends_of(persons_storage[self.friend_id])], [self.hero.id])

    def check_change_friend(self, new_friend_id, expected_friend_id, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.FRIEND, new_friend_id)
        self.assertEqual(self.hero.preferences.friend_id, self.friend_id)
        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.friend_id, expected_friend_id)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_friend(self):
        self.check_change_friend(self.friend_2_id, self.friend_2_id, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_friend_cooldownd(self):
        self.check_change_friend(self.friend_2_id, self.friend_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
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

        hero_1.preferences.friend_id = person_1.id
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.save()

        hero_2.preferences.friend_id = person_1.id
        hero_2.save()

        hero_3.preferences.friend_id = person_1.id
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_3.save()

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = HeroPrototype.get_by_account_id(account_id)
        hero_4.preferences.friend_id = person_1.id
        hero_4.save()

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        hero_5 = HeroPrototype.get_by_account_id(account_id)
        hero_5.preferences.friend_id = person_1.id
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_5.save()

        self.assertEqual(HeroPreferences.count_friends_of(person_1), 2)
        self.assertEqual(HeroPreferences.count_friends_of(person_2), 0)

        self.assertEqual(set([h.id for h in HeroPreferences.get_friends_of(person_1)]), set([hero_1.id, hero_3.id]))

    def test_reset_friend_on_highlevel_update(self):
        friend = self.place_1.persons[0]

        self.hero.preferences.friend_id = friend.id
        self.hero.save()

        friend.move_out_game()
        friend.save()

        self.storage.on_highlevel_data_updated()

        self.assertEqual(self.hero.preferences.friend_id, None)



class HeroPreferencesEnemyTest(TestCase):

    def setUp(self):
        super(HeroPreferencesEnemyTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.hero._model.level = c.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED
        self.hero._model.save()

        self.enemy_id = Person.objects.all()[0].id
        self.enemy_2_id = Person.objects.all()[1].id
        self.friend_id = Person.objects.all()[2].id

    def tearDown(self):
        pass

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, 666)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.enemy_id, None)

    def test_wrong_level(self):
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

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
        self.assertEqual(self.hero.preferences.enemy_id, None)

    def test_set_enemy(self):
        self.assertEqual(HeroPreferences.get_enemies_of(persons_storage[self.enemy_id]), [])
        changed_at = self.hero.preferences.enemy_changed_at
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(self.hero.preferences.enemy_id, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.enemy_id, self.enemy_id)
        self.assertTrue(changed_at < self.hero.preferences.enemy_changed_at)

        self.assertEqual([hero.id for hero in HeroPreferences.get_enemies_of(persons_storage[self.enemy_id])], [])

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=1)
        self.hero.save()

        self.assertEqual([hero.id for hero in HeroPreferences.get_enemies_of(persons_storage[self.enemy_id])], [self.hero.id])

    def test_set_friend_as_enemy(self):
        self.hero.preferences.friend_id = self.friend_id
        self.hero.save()

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, self.friend_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.ENEMY_AND_FRIEND)

    def check_change_enemy(self, new_enemy_id, expected_enemy_id, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.ENEMY, new_enemy_id)
        self.assertEqual(self.hero.preferences.enemy_id, self.enemy_id)
        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.enemy_id, expected_enemy_id)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_enemy(self):
        self.check_change_enemy(self.enemy_2_id, self.enemy_2_id, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_enemy_cooldown(self):
        self.check_change_enemy(self.enemy_2_id, self.enemy_id, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
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

        hero_1.preferences.enemy_id = person_1.id
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.save()

        hero_2.preferences.enemy_id = person_1.id
        hero_2.save()

        hero_3.preferences.enemy_id = person_1.id
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_3.save()

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = HeroPrototype.get_by_account_id(account_id)
        hero_4.preferences.enemy_id = person_1.id
        hero_4.save()

        result, account_id, bundle_id = register_user('test_user_5', 'test_user_5@test.com', '111111')
        hero_5 = HeroPrototype.get_by_account_id(account_id)
        hero_5.preferences.enemy_id = person_1.id
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

        self.assertEqual(self.hero.preferences.enemy_id, None)



class HeroPreferencesEquipmentSlotTest(TestCase):

    def setUp(self):
        super(HeroPreferencesEquipmentSlotTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.hero._model.level = c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED
        self.hero._model.save()

        self.slot_1 = SLOTS.HAND_PRIMARY
        self.slot_2 = SLOTS.PLATE

    def tearDown(self):
        pass

    def test_create(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, 'wrong_equip_slot')
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.equipment_slot, None)

    def test_wrong_level(self):
        self.hero._model.level = 1
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.LOW_LEVEL)

    def test_wrong_slot(self):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, 'wrong_equip_slot')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.UNKNOWN_EQUIPMENT_SLOT)

    def test_wrong_preference(self):
        task = ChoosePreferencesTask(self.hero.id, '666', self.slot_1)
        self.assertRaises(HeroException, task.process, FakePostpondTaskPrototype(), self.storage)

    def test_set_equipment_slot(self):
        changed_at = self.hero.preferences.equipment_slot_changed_at
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1)
        self.assertEqual(self.hero.preferences.equipment_slot, None)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.equipment_slot, self.slot_1)
        self.assertTrue(changed_at < self.hero.preferences.equipment_slot_changed_at)

    def check_change_equipment_slot(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1)
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        task = ChoosePreferencesTask(self.hero.id, PREFERENCE_TYPE.EQUIPMENT_SLOT, new_slot)
        self.assertEqual(self.hero.preferences.equipment_slot, self.slot_1)
        task_result = task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(expected_state == CHOOSE_PREFERENCES_TASK_STATE.PROCESSED,  task_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.equipment_slot, expected_slot)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_equipment_slot(self):
        self.check_change_equipment_slot(self.slot_2, self.slot_2, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_change_equipment_slot_cooldown(self):
        self.check_change_equipment_slot(self.slot_2, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_equipment_slot(self):
        self.check_change_equipment_slot(None, None, CHOOSE_PREFERENCES_TASK_STATE.PROCESSED)

    def test_remove_equipment_slot_cooldown(self):
        self.check_change_equipment_slot(None, self.slot_1, CHOOSE_PREFERENCES_TASK_STATE.COOLDOWN)



class HeroPreferencesRequestsTest(TestCase):

    def setUp(self):
        super(HeroPreferencesRequestsTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.hero._model.level = c.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED # maximum blocking level
        self.hero._model.save()

        register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.client = client.Client()

        self.mob_uuid = mobs_storage.all()[0].uuid
        self.mob_2_uuid = mobs_storage.all()[1].uuid

        self.place = place_1
        self.place_2 = place_2


    def tearDown(self):
        pass

    def test_preferences_dialog_mob(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.MOB))

        texts = []

        for mob_record in mobs_storage.all():
            if mob_record.level <= self.hero.level:
                texts.append(('"%s"' % mob_record.uuid, 1))
            else:
                texts.append(('"%s"' % mob_record.uuid, 0))

        self.check_html_ok(response, texts=texts)


    def test_preferences_dialog_place(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.PLACE))

        texts = []

        for place in Place.objects.all():
            texts.append(('"%d"' % place.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_friend(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.FRIEND))

        texts = []

        for person in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            texts.append(('data-preference-id="%d"' % person.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_enemy(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.ENEMY))

        texts = []

        for person in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            texts.append(('data-preference-id="%d"' % person.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_unlogined(self):
        request_url = reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.ENEMY)
        self.check_redirect(request_url, login_url(request_url))

    def test_preferences_dialog_wrong_user(self):
        self.request_login('test_user_2@test.com')
        response = self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.ENEMY))
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
