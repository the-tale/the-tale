# coding: utf-8
import datetime
import random

import mock

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map
from game.artifacts.storage import artifacts_storage
from game.prototypes import TimePrototype


from game.balance import formulas as f, constants as c
from game.logic_storage import LogicStorage
from game.quests.quests_builders import SearchSmith

from game.heroes.bag import ARTIFACT_TYPE_TO_SLOT, SLOTS
from game.heroes.prototypes import HeroPrototype
from game.heroes.habilities import ABILITY_TYPE, ABILITIES
from game.heroes.habilities import battle
from game.heroes.conf import heroes_settings


class HeroTest(TestCase):

    def setUp(self):
        super(HeroTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

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

    def test_is_premium(self):
        self.assertFalse(self.hero.is_premium)
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.assertTrue(self.hero.is_premium)

    def test_is_banned(self):
        self.assertFalse(self.hero.is_banned)
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.assertTrue(self.hero.is_banned)

    def test_is_active(self):
        self.assertTrue(self.hero.is_active)
        self.hero.active_state_end_at = datetime.datetime.now()
        self.assertFalse(self.hero.is_active)

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


    def test_experience_modifier__active_inactive_state(self):
        self.assertEqual(self.hero.experience_modifier, 1)

        self.hero._model.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)

        self.assertTrue(self.hero.experience_modifier < 1)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now(),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() - datetime.timedelta(seconds=60))

        self.assertEqual(self.hero.experience_modifier, 1)

    def test_experience_modifier__with_premium(self):
        self.assertEqual(self.hero.experience_modifier, 1)

        self.hero._model.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        self.hero._model.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        self.assertEqual(self.hero.experience_modifier, 1)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now(),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() - datetime.timedelta(seconds=60))

        self.assertEqual(self.hero.experience_modifier, 1)

    def test_can_participate_in_pvp(self):
        self.assertFalse(self.hero.can_participate_in_pvp)

        self.hero.is_fast = False

        self.assertTrue(self.hero.can_participate_in_pvp)
        with mock.patch('game.heroes.prototypes.HeroPrototype.is_banned', True):
            self.assertFalse(self.hero.can_participate_in_pvp)

    def test_can_change_persons_power(self):
        self.assertFalse(self.hero.can_change_persons_power)
        self.hero._model.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertTrue(self.hero.can_change_persons_power)

        with mock.patch('game.heroes.prototypes.HeroPrototype.is_banned', True):
            self.assertFalse(self.hero.can_change_persons_power)

    def test_can_repair_building(self):
        self.assertFalse(self.hero.can_repair_building)
        self.hero._model.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertTrue(self.hero.can_repair_building)

        with mock.patch('game.heroes.prototypes.HeroPrototype.is_banned', True):
            self.assertFalse(self.hero.can_repair_building)

    def test_update_with_account_data(self):
        self.hero.is_fast = True
        self.hero.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=1)
        self.hero.change_person_power_allowed_end_at = datetime.datetime.now() - datetime.timedelta(seconds=1)
        self.hero.normal_experience_rate_end_at = datetime.datetime.now() - datetime.timedelta(seconds=1)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60))

        self.assertFalse(self.hero.is_fast)
        self.assertTrue(self.hero.active_state_end_at > datetime.datetime.now())
        self.assertTrue(self.hero.premium_state_end_at > datetime.datetime.now())
        self.assertTrue(self.hero.ban_state_end_at > datetime.datetime.now())


    def test_modify_person_power(self):
        friend = self.place_1.persons[0]
        enemy = self.place_2.persons[0]

        self.hero.preferences.place_id = self.place_1.id
        self.hero.preferences.friend_id = friend.id
        self.hero.preferences.enemy_id = enemy.id

        self.assertEqual(self.hero.modify_person_power(self.place_3.persons[0], 100), 100)
        self.assertTrue(self.hero.modify_person_power(enemy, 100) > 100)
        self.assertTrue(self.hero.modify_person_power(friend, 100) > self.hero.modify_person_power(enemy, 100))

    def test_is_ui_caching_required(self):
        self.assertTrue(self.hero.is_ui_caching_required) # new hero must be cached, since player, who created him, is in game
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=heroes_settings.UI_CACHING_TIME + 1)
        self.assertFalse(self.hero.is_ui_caching_required)

    def test_cached_ui_info_from_cache__from_cache_is_true__for_not_visited_heroes(self):
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=heroes_settings.UI_CACHING_TIME+1)
        self.hero.save()

        with mock.patch('game.workers.supervisor.Worker.cmd_start_hero_caching') as call_counter:
            with mock.patch('game.heroes.prototypes.HeroPrototype.ui_info') as ui_info:
                HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)
        self.assertEqual(call_counter.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(for_last_turn=False, quests_info=True))

    def test_cached_ui_info_from_cache__from_cache_is_true__for_visited_heroes(self):
        with mock.patch('game.workers.supervisor.Worker.cmd_start_hero_caching') as call_counter:
            with mock.patch('game.heroes.prototypes.HeroPrototype.ui_info') as ui_info:
                HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)
        self.assertEqual(call_counter.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(for_last_turn=False, quests_info=True))

    def test_cached_ui_info_from_cache__from_cache_is_false(self):
        with mock.patch('game.workers.supervisor.Worker.cmd_start_hero_caching') as call_counter:
            HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)
        self.assertEqual(call_counter.call_count, 0)

    def test_ui_caching_timeout_greate_then_turn_delta(self):
        self.assertTrue(heroes_settings.UI_CACHING_TIMEOUT > c.TURN_DELTA)


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
            self.hero._model.level = level
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
            self.hero._model.level = level
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
            self.hero._model.level = level
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

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))

        self.hero = self.storage.accounts_to_heroes[account_id]
        self.hero._model.level = c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED
        self.hero.save()

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
        self.assertTrue(artifact.type.is_main_hand)


    def test_sharp_preferences_with_max_power(self):
        min_power, max_power = f.power_to_artifact_interval(self.hero.level)

        self.hero.preferences.equipment_slot = SLOTS.HAND_PRIMARY

        artifact = self.hero.equipment.get(SLOTS.HAND_PRIMARY)
        artifact.power = max_power

        artifact = self.hero.sharp_artifact()
        self.assertFalse(artifact.type.is_main_hand)

    def test_buy_artifact_and_not_equip(self):
        old_equipment = self.hero.equipment.serialize()
        old_bag = self.hero.bag.serialize()
        self.hero.buy_artifact(equip=False)
        self.assertEqual(old_equipment, self.hero.equipment.serialize())
        self.assertNotEqual(old_bag, self.hero.bag.serialize())


    def test_equipping_process(self):
        self.assertEqual(self.hero.get_equip_canditates(), (None, None, None))

        #equip artefact in empty slot
        artifact = artifacts_storage.generate_artifact_from_list(artifacts_storage.artifacts, self.hero.level)

        equip_slot = ARTIFACT_TYPE_TO_SLOT[artifact.type.value]
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
        new_artifact = artifacts_storage.generate_artifact_from_list([artifact.record], self.hero.level)
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
