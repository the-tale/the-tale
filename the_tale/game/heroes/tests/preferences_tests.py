# coding: utf-8
import mock

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from game.balance import constants as c

from accounts.logic import register_user

from game.logic import create_test_bundle, create_test_map
from game.bundles import BundlePrototype

from game.mobs.storage import MobsDatabase

from game.map.places.models import Place

from game.persons.models import Person, PERSON_STATE
from game.persons.storage import persons_storage

from game.heroes.preferences import ChoosePreferencesTaskPrototype
from game.heroes.models import ChoosePreferencesTask, CHOOSE_PREFERENCES_STATE, PREFERENCE_TYPE
from game.heroes.exceptions import HeroException
from game.heroes.bag import SLOTS

class HeroPreferencesCommonTests(TestCase):

    def setUp(self):
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.hero = self.bundle.tests_get_hero()


    def test_reset_friend_on_highlevel_update(self):
        friend = self.place_1.persons[0]

        self.hero.preferences.friend_id = friend.id
        self.hero.save()

        friend.move_out_game()
        friend.save()

        self.bundle.on_highlevel_data_updated()

        self.assertEqual(self.hero.preferences.friend_id, None)

    def test_reset_enemy_on_highlevel_update(self):
        enemy = self.place_1.persons[0]

        self.hero.preferences.enemy_id = enemy.id
        self.hero.save()

        enemy.move_out_game()
        enemy.save()

        self.bundle.on_highlevel_data_updated()

        self.assertEqual(self.hero.preferences.enemy_id, None)



class HeroPreferencesEnergyRegenerationTypeTest(TestCase):

    def setUp(self):
        place_1, place_2, place_3 = create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.model.level = c.CHARACTER_PREFERENCES_ENERGY_REGENERATION_TYPE_LEVEL_REQUIRED
        self.hero.model.pref_energy_regeneration_type = c.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE
        self.hero.model.save()

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.WAITING)
        self.assertEqual(self.hero.preferences.place_id, None)

    def test_reset_all(self):
        ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 1)
        ChoosePreferencesTaskPrototype.reset_all()
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 0)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.RESET).count(), 1)

    # can not test wrong level, since energy regeneration choice available on 1 level
    def test_wrong_level(self):
        self.assertEqual(c.CHARACTER_PREFERENCES_ENERGY_REGENERATION_TYPE_LEVEL_REQUIRED, 1)

    def test_wrong_energy_regeneration_type(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, 666)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    # can not test set energy regeneration type, since it must be always selected
    def test_set_energy_regeneration_typ(self):
        self.assertNotEqual(self.hero.preferences.energy_regeneration_type, None)

    def check_change_energy_regeneration_type(self, new_energy_regeneration_type, expected_energy_regeneration_type, expected_state):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, new_energy_regeneration_type)
        self.assertNotEqual(self.hero.preferences.energy_regeneration_type, new_energy_regeneration_type)

        task.process(self.bundle)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.energy_regeneration_type, expected_energy_regeneration_type)

    def test_change_energy_regeneration_type(self):
        self.check_change_energy_regeneration_type(c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY, c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_change_energy_regeneration_type_cooldown(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, c.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS)
        task.process(self.bundle)

        self.check_change_energy_regeneration_type(c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY, c.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS, CHOOSE_PREFERENCES_STATE.COOLDOWN)

    def test_remove_energy_regeneration_type(self):
        self.check_change_energy_regeneration_type(None, c.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE, CHOOSE_PREFERENCES_STATE.UNSPECIFIED_PREFERENCE)

    def test_remove_energy_regeneration_type_cooldown(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, c.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS)
        task.process(self.bundle)
        self.check_change_energy_regeneration_type(None, c.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS, CHOOSE_PREFERENCES_STATE.COOLDOWN)


class HeroPreferencesMobTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.model.level = c.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED
        self.hero.model.save()

        self.mob_id = MobsDatabase.storage().get_available_mobs_list(level=self.hero.level)[0].id
        self.mob_2_id = MobsDatabase.storage().get_available_mobs_list(level=self.hero.level)[1].id

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, 'wrong_mob_id')
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.WAITING)
        self.assertEqual(self.hero.preferences.mob_id, None)

    def test_reset_all(self):
        ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, 'wrong_mob_id')
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 1)
        ChoosePreferencesTaskPrototype.reset_all()
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 0)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.RESET).count(), 1)

    def test_wrong_level(self):
        self.hero.model.level = 1
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, self.mob_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_mob(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, 'wrong_mob_id')
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_preference(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, 666, self.mob_id)
        self.assertRaises(HeroException, task.process, self.bundle)

    def test_wrong_mob_level(self):
        wrong_mob_id = None
        for mob_id, mob_record in MobsDatabase.storage().data.items():
            if mob_record.level > self.hero.level:
                wrong_mob_id = mob_id
                break

        self.assertTrue(wrong_mob_id)

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, wrong_mob_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)
        self.assertEqual(self.hero.preferences.mob_id, None)


    def test_set_mob(self):
        changed_at = self.hero.preferences.mob_changed_at
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, self.mob_id)
        self.assertEqual(self.hero.preferences.mob_id, None)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.mob_id, self.mob_id)
        self.assertTrue(changed_at < self.hero.preferences.mob_changed_at)

    def check_change_mob(self, new_mob_id, expected_mob_id, expected_state):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, self.mob_id)
        task.process(self.bundle)

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, new_mob_id)
        self.assertEqual(self.hero.preferences.mob_id, self.mob_id)
        task.process(self.bundle)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.mob_id, expected_mob_id)

        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 2)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_mob(self):
        self.check_change_mob(self.mob_2_id, self.mob_2_id, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_change_mob_cooldown(self):
        self.check_change_mob(self.mob_2_id, self.mob_id, CHOOSE_PREFERENCES_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_mob(self):
        self.check_change_mob(None, None, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_remove_mob_cooldown(self):
        self.check_change_mob(None, self.mob_id, CHOOSE_PREFERENCES_STATE.COOLDOWN)


class HeroPreferencesPlaceTest(TestCase):

    def setUp(self):
        place_1, place_2, place_3 = create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.model.level = c.CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED
        self.hero.model.save()

        self.place = place_1
        self.place_2 = place_2

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.PLACE, 666)
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.WAITING)
        self.assertEqual(self.hero.preferences.place_id, None)

    def test_reset_all(self):
        ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.PLACE, 666)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 1)
        ChoosePreferencesTaskPrototype.reset_all()
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 0)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.RESET).count(), 1)

    def test_wrong_level(self):
        self.hero.model.level = 1
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.PLACE, self.place.id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_place(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, 666)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_set_place(self):
        changed_at = self.hero.preferences.place_changed_at
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.PLACE, self.place.id)
        self.assertEqual(self.hero.preferences.place_id, None)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.place_id, self.place.id)
        self.assertTrue(changed_at < self.hero.preferences.place_changed_at)


    def check_change_place(self, new_place_id, expected_place_id, expected_state):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.PLACE, self.place.id)
        task.process(self.bundle)

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.PLACE, new_place_id)
        self.assertEqual(self.hero.preferences.place_id, self.place.id)
        task.process(self.bundle)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.place_id, expected_place_id)

        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 2)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_place(self):
        self.check_change_place(self.place_2.id, self.place_2.id, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_change_place_cooldown(self):
        self.check_change_place(self.place_2.id, self.place.id, CHOOSE_PREFERENCES_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_place(self):
        self.check_change_place(None, None, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_remove_place_cooldown(self):
        self.check_change_place(None, self.place.id, CHOOSE_PREFERENCES_STATE.COOLDOWN)


class HeroPreferencesFriendTest(TestCase):

    def setUp(self):
        place_1, place_2, place_3 = create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.model.level = c.CHARACTER_PREFERENCES_FRIEND_LEVEL_REQUIRED
        self.hero.model.save()

        self.friend_id = Person.objects.all()[0].id
        self.friend_2_id = Person.objects.all()[1].id
        self.enemy_id = Person.objects.all()[2].id

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.FRIEND, 666)
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.WAITING)
        self.assertEqual(self.hero.preferences.friend_id, None)

    def test_reset_all(self):
        ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.FRIEND, 666)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 1)
        ChoosePreferencesTaskPrototype.reset_all()
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 0)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.RESET).count(), 1)

    def test_wrong_level(self):
        self.hero.model.level = 1
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.FRIEND, self.friend_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_friend(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, 666)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_set_enemy_as_friend(self):
        self.hero.preferences.enemy_id = self.enemy_id
        self.hero.save()

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.FRIEND, self.enemy_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.UNAVAILABLE_PERSON)

    def test_set_outgame_friend(self):
        friend = persons_storage[self.friend_id]
        friend.move_out_game()
        friend.save()

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.FRIEND, self.friend_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.OUTGAME_PERSON)
        self.assertEqual(self.hero.preferences.friend_id, None)


    def test_set_friend(self):
        changed_at = self.hero.preferences.friend_changed_at
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.FRIEND, self.friend_id)
        self.assertEqual(self.hero.preferences.friend_id, None)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.friend_id, self.friend_id)
        self.assertTrue(changed_at < self.hero.preferences.friend_changed_at)

    def check_change_friend(self, new_friend_id, expected_friend_id, expected_state):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.FRIEND, self.friend_id)
        task.process(self.bundle)

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.FRIEND, new_friend_id)
        self.assertEqual(self.hero.preferences.friend_id, self.friend_id)
        task.process(self.bundle)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.friend_id, expected_friend_id)

        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 2)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_friend(self):
        self.check_change_friend(self.friend_2_id, self.friend_2_id, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_change_friend_cooldownd(self):
        self.check_change_friend(self.friend_2_id, self.friend_id, CHOOSE_PREFERENCES_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_friend(self):
        self.check_change_friend(None, None, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_remove_friend_cooldown(self):
        self.check_change_friend(None, self.friend_id, CHOOSE_PREFERENCES_STATE.COOLDOWN)


class HeroPreferencesEnemyTest(TestCase):

    def setUp(self):
        place_1, place_2, place_3 = create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.model.level = c.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED
        self.hero.model.save()

        self.enemy_id = Person.objects.all()[0].id
        self.enemy_2_id = Person.objects.all()[1].id
        self.friend_id = Person.objects.all()[2].id

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENEMY, 666)
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.WAITING)
        self.assertEqual(self.hero.preferences.enemy_id, None)

    def test_reset_all(self):
        ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENEMY, 666)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 1)
        ChoosePreferencesTaskPrototype.reset_all()
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 0)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.RESET).count(), 1)

    def test_wrong_level(self):
        self.hero.model.level = 1
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_enemy(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, 666)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_set_outgame_enemy(self):
        enemy = persons_storage[self.enemy_id]
        enemy.move_out_game()
        enemy.save()

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.OUTGAME_PERSON)
        self.assertEqual(self.hero.preferences.enemy_id, None)

    def test_set_enemy(self):
        changed_at = self.hero.preferences.enemy_changed_at
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        self.assertEqual(self.hero.preferences.enemy_id, None)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.enemy_id, self.enemy_id)
        self.assertTrue(changed_at < self.hero.preferences.enemy_changed_at)

    def test_set_friend_as_enemy(self):
        self.hero.preferences.friend_id = self.friend_id
        self.hero.save()

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENEMY, self.friend_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.UNAVAILABLE_PERSON)

    def check_change_enemy(self, new_enemy_id, expected_enemy_id, expected_state):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENEMY, self.enemy_id)
        task.process(self.bundle)

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.ENEMY, new_enemy_id)
        self.assertEqual(self.hero.preferences.enemy_id, self.enemy_id)
        task.process(self.bundle)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.enemy_id, expected_enemy_id)

        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 2)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_enemy(self):
        self.check_change_enemy(self.enemy_2_id, self.enemy_2_id, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_change_enemy_cooldown(self):
        self.check_change_enemy(self.enemy_2_id, self.enemy_id, CHOOSE_PREFERENCES_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_enemy(self):
        self.check_change_enemy(None, None, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_remove_enemy_cooldown(self):
        self.check_change_enemy(None, self.enemy_id, CHOOSE_PREFERENCES_STATE.COOLDOWN)


class HeroPreferencesEquipmentSlotTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.model.level = c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED
        self.hero.model.save()

        self.slot_1 = SLOTS.HAND_PRIMARY
        self.slot_2 = SLOTS.PLATE

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.EQUIPMENT_SLOT, 'wrong_equip_slot')
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.WAITING)
        self.assertEqual(self.hero.preferences.mob_id, None)

    def test_reset_all(self):
        ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.EQUIPMENT_SLOT, 'wrong_equip_slot')
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 1)
        ChoosePreferencesTaskPrototype.reset_all()
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 0)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.RESET).count(), 1)

    def test_wrong_level(self):
        self.hero.model.level = 1
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_slot(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.EQUIPMENT_SLOT, 'wrong_equip_slot')
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_preference(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, '666', self.slot_1)
        self.assertRaises(HeroException, task.process, self.bundle)

    def test_set_equipment_slot(self):
        changed_at = self.hero.preferences.equipment_slot_changed_at
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1)
        self.assertEqual(self.hero.preferences.equipment_slot, None)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.equipment_slot, self.slot_1)
        self.assertTrue(changed_at < self.hero.preferences.equipment_slot_changed_at)

    def check_change_equipment_slot(self, new_slot, expected_slot, expected_state):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1)
        task.process(self.bundle)

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.EQUIPMENT_SLOT, new_slot)
        self.assertEqual(self.hero.preferences.equipment_slot, self.slot_1)
        task.process(self.bundle)
        self.assertEqual(task.state, expected_state)
        self.assertEqual(self.hero.preferences.equipment_slot, expected_slot)

        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 2)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_change_equipment_slot(self):
        self.check_change_equipment_slot(self.slot_2, self.slot_2, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_change_equipment_slot_cooldown(self):
        self.check_change_equipment_slot(self.slot_2, self.slot_1, CHOOSE_PREFERENCES_STATE.COOLDOWN)

    @mock.patch('game.balance.constants.CHARACTER_PREFERENCES_CHANGE_DELAY', 0)
    def test_remove_equipment_slot(self):
        self.check_change_equipment_slot(None, None, CHOOSE_PREFERENCES_STATE.PROCESSED)

    def test_remove_equipment_slot_cooldown(self):
        self.check_change_equipment_slot(None, self.slot_1, CHOOSE_PREFERENCES_STATE.COOLDOWN)



class HeroPreferencesRequestsTest(TestCase):

    def setUp(self):
        place_1, place_2, place_3 = create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.bundle = BundlePrototype.get_by_id(bundle_id)
        self.hero = self.bundle.tests_get_hero()

        self.hero.model.level = c.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED # maximum blocking level
        self.hero.model.save()

        register_user('test_user_2', 'test_user_2@test.com', '222222')

        self.client = client.Client()

        self.mob_id = MobsDatabase.storage().data.keys()[0]
        self.mob_2_id = MobsDatabase.storage().data.keys()[1]

        self.place = place_1
        self.place_2 = place_2


    def tearDown(self):
        pass

    def test_preferences_dialog_mob(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.MOB))

        texts = []

        for mob_id, mob_record in MobsDatabase.storage().data.items():
            if mob_record.level <= self.hero.level:
                texts.append(('"%s"' % mob_id, 1))
            else:
                texts.append(('"%s"' % mob_id, 0))

        self.check_html_ok(response, texts=texts)


    def test_preferences_dialog_place(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.PLACE))

        texts = []

        for place in Place.objects.all():
            texts.append(('"%d"' % place.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_friend(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.FRIEND))

        texts = []

        for person in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            texts.append(('data-preference-id="%d"' % person.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_preferences_dialog_enemy(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.ENEMY))

        texts = []

        for person in Person.objects.filter(state=PERSON_STATE.IN_GAME):
            texts.append(('data-preference-id="%d"' % person.id, 1))

        self.check_html_ok(response, texts=texts)

    def test_choose_preferences_unlogined(self):
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})
        self.check_ajax_error(response, 'heroes.can_no_see_this_account')

    def test_choose_preferences_success(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})

        task = ChoosePreferencesTask.objects.all()[0]
        self.check_ajax_processing(response, reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % task.id))

        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)

    def test_choose_preferences_remove_success(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB})

        task = ChoosePreferencesTask.objects.all()[0]
        self.assertEqual(task.preference_id, None)

        self.check_ajax_processing(response, reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % task.id))

        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)

    def test_choose_preferences_status_unlogined(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})
        response = self.client.post(reverse('accounts:logout'))

        task = ChoosePreferencesTask.objects.all()[0]
        response = self.client.post(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.check_ajax_error(response, 'heroes.can_no_see_this_account')

    def test_choose_preferences_status_foreign_task(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})
        response = self.client.post(reverse('accounts:logout'))

        response = self.client.post(reverse('accounts:login'), {'email': 'test_user_2@test.com', 'password': '222222'})

        task = ChoosePreferencesTask.objects.all()[0]
        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)), HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.check_ajax_error(response, 'heroes.can_no_see_this_account')

    def test_choose_preferences_status_error(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})

        task = ChoosePreferencesTask.objects.all()[0]
        task.state = CHOOSE_PREFERENCES_STATE.ERROR
        task.save()

        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.check_ajax_error(response, 'heroes.choose_preferences_status.error')

    def test_choose_preferences_status_success(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})

        task = ChoosePreferencesTask.objects.all()[0]
        task.state = CHOOSE_PREFERENCES_STATE.PROCESSED
        task.save()

        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.check_ajax_ok(response)

    def test_choose_preferences_status_cooldown(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})

        task = ChoosePreferencesTask.objects.all()[0]
        task.state = CHOOSE_PREFERENCES_STATE.COOLDOWN
        task.save()

        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.check_ajax_error(response, 'heroes.choose_preferences_status.cooldown')


    def test_choose_preferences_status_unavailable_person(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})

        task = ChoosePreferencesTask.objects.all()[0]
        task.state = CHOOSE_PREFERENCES_STATE.UNAVAILABLE_PERSON
        task.save()

        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.check_ajax_error(response, 'heroes.choose_preferences_status.unavailable_person')


    def test_choose_preferences_status_outgame_person(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})

        task = ChoosePreferencesTask.objects.all()[0]
        task.state = CHOOSE_PREFERENCES_STATE.OUTGAME_PERSON
        task.save()

        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.check_ajax_error(response, 'heroes.choose_preferences_status.outgame_person')


    def test_choose_preferences_unspecified_preference(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})

        task = ChoosePreferencesTask.objects.all()[0]
        task.state = CHOOSE_PREFERENCES_STATE.UNSPECIFIED_PREFERENCE
        task.save()

        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.check_ajax_error(response, 'heroes.choose_preferences_status.unspecified_preference')
