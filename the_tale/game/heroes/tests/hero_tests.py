# coding: utf-8

from django.test import TestCase

from accounts.logic import register_user

from game.logic import create_test_map
from game.artifacts.storage import ArtifactsDatabase
from game.artifacts.conf import EQUIP_TYPE
from game.prototypes import TimePrototype


from game.balance import formulas as f, constants as c
from game.logic_storage import LogicStorage
from game.heroes.bag import ARTIFACT_TYPES_TO_SLOTS, SLOTS
from game.quests.quests_builders import SearchSmith

from game.heroes.prototypes import HeroPrototype

class HeroTest(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

    def tearDown(self):
        pass


    def test_create(self):
        self.assertTrue(self.hero.is_alive)
        self.assertEqual(self.hero.created_at_turn, TimePrototype.get_current_time().turn_number)

    def test_create_time(self):
        time = TimePrototype.get_current_time()
        time.increment_turn()
        time.increment_turn()
        time.increment_turn()
        time.save()

        result, account_id, bundle_id = register_user('test_user_2')

        hero = HeroPrototype.get_by_account_id(account_id)

        self.assertEqual(hero.created_at_turn, TimePrototype.get_current_time().turn_number)

        self.assertTrue(hero.created_at_turn != self.hero.created_at_turn)


    def test_equipping_process(self):
        self.assertEqual(self.hero.get_equip_canditates(), (None, None, None))

        #equip artefact in empty slot
        artifact = ArtifactsDatabase.storage().generate_artifact_from_list(ArtifactsDatabase.storage().artifacts_ids, self.hero.level)

        equip_slot = ARTIFACT_TYPES_TO_SLOTS[artifact.equip_type][0]
        self.hero.equipment.unequip(equip_slot)

        self.hero.bag.put_artifact(artifact)

        slot, unequipped, equipped = self.hero.get_equip_canditates()
        self.assertTrue(slot)
        self.assertTrue(unequipped is None)
        self.assertEqual(equipped, artifact)

        self.hero.change_equipment(slot, unequipped, equipped)
        self.assertTrue(not self.hero.bag.items())
        self.assertEqual(self.hero.equipment.get(slot), artifact)

        # change artifact
        new_artifact = ArtifactsDatabase.storage().generate_artifact_from_list([artifact.id], self.hero.level)
        new_artifact.power = artifact.power + 1
        self.hero.bag.put_artifact(new_artifact)

        slot, unequipped, equipped = self.hero.get_equip_canditates()
        self.assertTrue(slot)
        self.assertEqual(unequipped, artifact)
        self.assertEqual(equipped, new_artifact)

        self.hero.change_equipment(slot, unequipped, equipped)
        self.assertEqual(self.hero.bag.items()[0][1], artifact)
        self.assertEqual(len(self.hero.bag.items()), 1)
        self.assertEqual(self.hero.equipment.get(slot), new_artifact)

        self.storage._test_save()


    def test_lvl_up(self):
        self.assertEqual(self.hero.level, 1)
        self.assertEqual(self.hero.experience_modifier, 1)

        self.hero.add_experience(f.exp_on_lvl(1)/2)
        self.assertEqual(self.hero.level, 1)

        self.hero.add_experience(f.exp_on_lvl(1))
        self.assertEqual(self.hero.level, 2)
        self.assertEqual(self.hero.experience, f.exp_on_lvl(1)/2)

        self.hero.add_experience(f.exp_on_lvl(2))
        self.assertEqual(self.hero.level, 3)

        self.hero.add_experience(f.exp_on_lvl(3))
        self.assertEqual(self.hero.level, 4)
        self.assertEqual(self.hero.destiny_points, 1)

        self.hero.add_experience(f.exp_on_lvl(4))
        self.assertEqual(self.hero.level, 5)
        self.assertEqual(self.hero.destiny_points, 2)

    def test_set_active_inactive_state(self):
        self.assertEqual(self.hero.experience_modifier, 1)

        time = TimePrototype.get_current_time()
        time.turn_number += 2 * c.EXP_ACTIVE_STATE_LENGTH
        time.save()

        self.assertTrue(self.hero.experience_modifier < 1)

        self.hero.mark_as_active()
        self.hero.save()

        self.assertEqual(self.hero.experience_modifier, 1)


class HeroGetSpecialQuestsTest(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)


    def test_special_quests_searchsmith_without_preferences(self):
        self.assertFalse(SearchSmith.type() in self.hero.get_special_quests())

    def test_special_quests_searchsmith_with_preferences_without_artifact(self):
        self.hero.equipment.test_remove_all()
        self.hero.preferences.equipment_slot = SLOTS.PLATE
        self.hero.save()

        self.assertTrue(SearchSmith.type() in self.hero.get_special_quests())

    def test_special_quests_searchsmith_with_preferences_with_artifact(self):
        self.hero.preferences.equipment_slot = SLOTS.PLATE
        self.hero.save()

        self.assertTrue(self.hero.equipment.get(SLOTS.PLATE) is not None)
        self.assertTrue(SearchSmith.type() in self.hero.get_special_quests())


class HeroEquipmentTests(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.hero.model.level = c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED
        self.hero.model.save()

    def test_sharp_artifact(self):
        old_power = self.hero.power
        artifact = self.hero.sharp_artifact()
        self.assertEqual(self.hero.power, old_power+1)
        self.assertEqual(artifact.power, 1)
        self.assertTrue(self.hero.equipment.updated)


    def test_sharp_artifact_when_all_artifacts_has_max_power(self):
        min_power, max_power = f.power_to_artifact_interval(self.hero.level)

        for artifact in self.hero.equipment.equipment.values():
            artifact.power = max_power

        old_power = self.hero.power
        artifact = self.hero.sharp_artifact()
        self.assertEqual(self.hero.power, old_power+1)
        self.assertEqual(artifact.power, max_power + 1)
        self.assertTrue(self.hero.equipment.updated)

    def test_sharp_preferences(self):
        self.hero.preferences.equipment_slot = SLOTS.HAND_PRIMARY

        artifact = self.hero.sharp_artifact()
        self.assertEqual(artifact.equip_type, EQUIP_TYPE.WEAPON)


    def test_sharp_preferences_with_max_power(self):
        min_power, max_power = f.power_to_artifact_interval(self.hero.level)

        self.hero.preferences.equipment_slot = SLOTS.HAND_PRIMARY

        artifact = self.hero.equipment.get(SLOTS.HAND_PRIMARY)
        artifact.power = max_power

        artifact = self.hero.sharp_artifact()
        self.assertNotEqual(artifact.equip_type, EQUIP_TYPE.WEAPON)
