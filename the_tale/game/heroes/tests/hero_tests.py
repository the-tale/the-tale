# coding: utf-8
import random

import mock

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map
from game.artifacts.storage import ArtifactsDatabase
from game.artifacts.conf import EQUIP_TYPE
from game.prototypes import TimePrototype


from game.balance import formulas as f, constants as c
from game.logic_storage import LogicStorage
from game.quests.quests_builders import SearchSmith

from game.heroes.bag import ARTIFACT_TYPES_TO_SLOTS, SLOTS
from game.heroes.prototypes import HeroPrototype
from game.heroes.habilities import ABILITY_TYPE, ABILITIES
from game.heroes.habilities import battle


class HeroTest(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

    def tearDown(self):
        pass


    def test_create(self):
        self.assertTrue(self.hero.is_alive)
        self.assertEqual(self.hero.created_at_turn, TimePrototype.get_current_time().turn_number)
        self.assertEqual(self.hero.abilities.get('hit').level, 1)

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


    def test_set_active_inactive_state(self):
        self.assertEqual(self.hero.experience_modifier, 1)

        time = TimePrototype.get_current_time()
        time.turn_number += 2 * c.EXP_ACTIVE_STATE_LENGTH
        time.save()

        self.assertTrue(self.hero.experience_modifier < 1)

        self.hero.mark_as_active()
        self.hero.save()

        self.assertEqual(self.hero.experience_modifier, 1)


class HeroLevelUpTests(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

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

        self.hero.add_experience(f.exp_on_lvl(4))
        self.assertEqual(self.hero.level, 5)

    def test_max_ability_points_number(self):
        level_to_points_number = { 1: 2,
                                   2: 2,
                                   3: 3,
                                   4: 3,
                                   5: 4}

        for level, points_number in level_to_points_number.items():
            self.hero.model.level = level
            self.assertEqual(self.hero.max_ability_points_number, points_number)


    def test_can_choose_new_ability(self):
        self.assertTrue(self.hero.can_choose_new_ability)
        with mock.patch('game.heroes.prototypes.HeroPrototype.current_ability_points_number', 2):
            self.assertFalse(self.hero.can_choose_new_ability)

    def test_next_battle_ability_point_lvl(self):
        level_to_next_level = { 1: 3,
                                2: 3,
                                3: 7,
                                4: 7,
                                5: 7,
                                6: 7,
                                7: 9,
                                8: 9,
                                9: 13,
                                10: 13,
                                11: 13,
                                12: 13,
                                13: 15,
                                14: 15,
                                15: 19,
                                16: 19,
                                17: 19}

        for level, next_level in level_to_next_level.items():
            self.hero.model.level = level
            self.assertEqual(self.hero.next_battle_ability_point_lvl, next_level)

    def test_next_nonbattle_ability_point_lvl(self):
        level_to_next_level = { 1: 5,
                                2: 5,
                                3: 5,
                                4: 5,
                                5: 11,
                                6: 11,
                                7: 11,
                                8: 11,
                                9: 11,
                                10: 11,
                                11: 17,
                                12: 17,
                                13: 17,
                                14: 17,
                                15: 17,
                                16: 17,
                                17: 23}

        for level, next_level in level_to_next_level.items():
            self.hero.model.level = level
            self.assertEqual(self.hero.next_nonbattle_ability_point_lvl, next_level)

    def test_next_ability_type(self):
        ability_points_to_type = {1: ABILITY_TYPE.BATTLE,
                                  2: ABILITY_TYPE.BATTLE,
                                  3: ABILITY_TYPE.NONBATTLE,
                                  4: ABILITY_TYPE.BATTLE,
                                  5: ABILITY_TYPE.BATTLE,
                                  6: ABILITY_TYPE.NONBATTLE}

        for ability_points, next_type in ability_points_to_type.items():
            with mock.patch('game.heroes.prototypes.HeroPrototype.current_ability_points_number', ability_points):
                self.assertEqual(self.hero.next_ability_type, next_type)


    def test_get_abilities_for_choose_first_time(self):
        abilities = self.hero.get_abilities_for_choose()
        self.assertEqual(len(abilities), c.ABILITIES_FOR_CHOOSE_MAXIMUM)

    def test_get_abilities_for_choose_has_free_slots(self):
        for ability in self.hero.abilities.abilities.values():
            ability.level = ability.MAX_LEVEL
        abilities = self.hero.get_abilities_for_choose()
        self.assertEqual(len(abilities), 4)
        self.assertEqual(len(filter(lambda a: a.level==2 and a.get_id()=='hit', abilities)), 0)

    def test_get_abilities_for_choose_all_passive_slots_busy(self):
        passive_abilities = filter(lambda a: a.activation_type.is_passive, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(len(filter(lambda a: a.activation_type.is_passive, abilities)), 0)

    def test_get_abilities_for_choose_all_active_slots_busy(self):
        active_abilities = filter(lambda a: a.activation_type.is_active, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(len(filter(lambda a: a.activation_type.is_active, abilities)), 0)

    def test_get_abilities_for_choose_all_slots_busy(self):
        passive_abilities = filter(lambda a: a.activation_type.is_passive, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = filter(lambda a: a.activation_type.is_active, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(len(abilities), 0)

    @mock.patch('game.heroes.prototypes.HeroPrototype.next_ability_type', ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_slots_busy_but_one_not_max_level(self):
        passive_abilities = filter(lambda a: a.activation_type.is_passive, [a(level=a.MAX_LEVEL) for a in battle.ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = filter(lambda a: a.activation_type.is_active, [a(level=a.MAX_LEVEL) for a in battle.ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        ability = random.choice(self.hero.abilities.abilities.values())
        ability.level -= 1

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(abilities, [ability.__class__(level=ability.level+1)])

    def test_get_abilities_for_choose_all_slots_busy_and_all_not_max_level(self):
        passive_abilities = filter(lambda a: a.activation_type.is_passive, [a(level=1) for a in ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = filter(lambda a: a.activation_type.is_active, [a(level=1) for a in ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(len(abilities), c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM)



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

    def test_buy_artifact_and_not_equip(self):
        old_equipment = self.hero.equipment.serialize()
        old_bag = self.hero.bag.serialize()
        self.hero.buy_artifact(equip=False)
        self.assertEqual(old_equipment, self.hero.equipment.serialize())
        self.assertNotEqual(old_bag, self.hero.bag.serialize())
