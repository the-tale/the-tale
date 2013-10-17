# coding: utf-8
import datetime
import time
import random

import mock

from questgen.quests.search_smith import SearchSmith

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map
from game.prototypes import TimePrototype


from game.balance import formulas as f, constants as c
from game.logic_storage import LogicStorage

from game.map.places.storage import places_storage


from game.heroes.prototypes import HeroPrototype, HeroPreferencesPrototype
from game.heroes.habilities import ABILITY_TYPE, ABILITIES, battle
from game.heroes.conf import heroes_settings
from game.heroes.relations import EQUIPMENT_SLOT, RISK_LEVEL


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

        self.assertTrue(self.hero.preferences.risk_level._is_NORMAL)

        self.assertEqual(HeroPreferencesPrototype._db_count(), 1)
        self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).energy_regeneration_type, self.hero.preferences.energy_regeneration_type)
        self.assertEqual(HeroPreferencesPrototype.get_by_hero_id(self.hero.id).risk_level, self.hero.preferences.risk_level)


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
        game_time = TimePrototype.get_current_time()
        game_time.increment_turn()
        game_time.increment_turn()
        game_time.increment_turn()
        game_time.save()

        result, account_id, bundle_id = register_user('test_user_2')

        hero = HeroPrototype.get_by_account_id(account_id)

        self.assertEqual(hero.created_at_turn, TimePrototype.get_current_time().turn_number)

        self.assertTrue(hero.created_at_turn != self.hero.created_at_turn)

    def test_experience_modifier__banned(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertEqual(self.hero.experience_modifier, 0)

    def test_experience_modifier__active_inactive_state(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero._model.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)

        self.assertTrue(self.hero.experience_modifier < c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now(),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() - datetime.timedelta(seconds=60),
                                           might=0)

        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

    def test_experience_modifier__with_premium(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero._model.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        self.hero._model.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_PREMIUM_ACCOUNT)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now(),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() - datetime.timedelta(seconds=60),
                                           might=666)

        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

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
                                           ban_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           might=666)

        self.assertFalse(self.hero.is_fast)
        self.assertTrue(self.hero.active_state_end_at > datetime.datetime.now())
        self.assertTrue(self.hero.premium_state_end_at > datetime.datetime.now())
        self.assertTrue(self.hero.ban_state_end_at > datetime.datetime.now())
        self.assertEqual(self.hero.might, 666)


    def test_modify_person_power(self):
        friend = self.place_1.persons[0]
        enemy = self.place_2.persons[0]

        self.hero.preferences.set_place(self.place_1)
        self.hero.preferences.set_friend(friend)
        self.hero.preferences.set_enemy(enemy)

        self.assertEqual(self.hero.modify_power(person=self.place_3.persons[0], power=100), 100 * self.hero.person_power_modifier)
        self.assertTrue(self.hero.modify_power(person=enemy, power=100) > 100 * self.hero.person_power_modifier)
        self.assertTrue(self.hero.modify_power(person=friend, power=100) > self.hero.modify_power(person=enemy, power=100)) # friend live in hometowm

    def test_modify_place_power(self):
        self.hero.preferences.set_place(self.place_1)

        self.assertEqual(self.hero.modify_power(place=self.place_2, power=100), 100 * self.hero.person_power_modifier)
        self.assertTrue(self.hero.modify_power(place=self.place_1, power=100) > 100 * self.hero.person_power_modifier)

    def test_is_ui_caching_required(self):
        self.assertTrue(self.hero.is_ui_caching_required) # new hero must be cached, since player, who created him, is in game
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=heroes_settings.UI_CACHING_TIME + 1)
        self.assertFalse(self.hero.is_ui_caching_required)

    def test_cached_ui_info_from_cache__from_cache_is_true__for_not_visited_heroes(self):
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=heroes_settings.UI_CACHING_TIME + 1)
        self.hero.save()

        with mock.patch('game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('game.heroes.prototypes.HeroPrototype.ui_info') as ui_info:
                HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)
        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(for_last_turn=False))

    def test_cached_ui_info_for_hero__data_is_none(self):
        with mock.patch('game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('game.heroes.prototypes.HeroPrototype.ui_info') as ui_info:
                HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)
        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(for_last_turn=False))

    @mock.patch('dext.utils.cache.get', lambda x: {'ui_caching_started_at': 0})
    def test_cached_ui_info_for_hero__continue_caching_required(self):
        with mock.patch('game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('game.heroes.prototypes.HeroPrototype.ui_info') as ui_info:
                HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)
        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(for_last_turn=False))

    @mock.patch('dext.utils.cache.get', lambda x: {'ui_caching_started_at': time.time()})
    def test_cached_ui_info_for_hero__continue_caching_not_required(self):
        with mock.patch('game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('game.heroes.prototypes.HeroPrototype.ui_info') as ui_info:
                HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)

    def test_cached_ui_info_for_hero__saved_at_turn(self):
        self.assertEqual(self.hero.saved_at_turn, 0)
        self.assertEqual(HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)['saved_at_turn'], 0)

        TimePrototype(turn_number=666).save()

        self.hero.save()

        self.assertTrue(self.hero.saved_at_turn, 666)

        self.assertEqual(HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)['saved_at_turn'], 666)

    def test_cached_ui_info_for_hero__saved_at(self):
        old_saved_at = self.hero.saved_at
        self.assertEqual(HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)['saved_at'], time.mktime(old_saved_at.timetuple()))

        self.hero.save()

        self.assertTrue(old_saved_at < self.hero.saved_at)
        self.assertEqual(HeroPrototype.cached_ui_info_for_hero(self.hero.account_id)['saved_at'], time.mktime(self.hero.saved_at.timetuple()))

    def test_ui_caching_timeout_greate_then_turn_delta(self):
        self.assertTrue(heroes_settings.UI_CACHING_TIMEOUT > c.TURN_DELTA)

    def test_is_ui_continue_caching_required(self):
        self.assertTrue(HeroPrototype.is_ui_continue_caching_required(0))
        self.assertFalse(HeroPrototype.is_ui_continue_caching_required(time.time() - (heroes_settings.UI_CACHING_TIME - heroes_settings.UI_CACHING_CONTINUE_TIME - 1)))
        self.assertTrue(HeroPrototype.is_ui_continue_caching_required(time.time() - (heroes_settings.UI_CACHING_TIME - heroes_settings.UI_CACHING_CONTINUE_TIME + 1)))
        self.assertTrue(HeroPrototype.is_ui_continue_caching_required(time.time() - heroes_settings.UI_CACHING_TIME))

    def test_push_message(self):
        from game.heroes.messages import MessagesContainer
        message = MessagesContainer._prepair_message('abrakadabra')

        self.hero.messages._clear()
        self.hero.diary._clear()

        self.assertEqual(len(self.hero.messages), 0)
        self.assertEqual(len(self.hero.diary), 0)

        self.hero.push_message(message)

        self.assertEqual(len(self.hero.messages), 1)
        self.assertEqual(len(self.hero.diary), 0)

        self.hero.push_message(message, diary=True)

        self.assertEqual(len(self.hero.messages), 2)
        self.assertEqual(len(self.hero.diary), 1)

        self.hero.push_message(message, diary=True, journal=False)

        self.assertEqual(len(self.hero.messages), 2)
        self.assertEqual(len(self.hero.diary), 2)

    def test_energy_maximum(self):
        maximum_without_premium = self.hero.energy_maximum
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(days=1)
        maximum_with_premium = self.hero.energy_maximum
        self.assertTrue(maximum_without_premium < maximum_with_premium)


    def check_rests_from_risk(self, method):
        results = []
        for risk_level in RISK_LEVEL._records:
            values = []
            self.hero.preferences.set_risk_level(risk_level)
            for health_percents in xrange(1, 100, 1):
                self.hero._model.health = self.hero.max_health * float(health_percents) / 100
                values.append(method(self.hero))
            results.append(values)

        for i, result_1 in enumerate(results):
            for j, result_2 in enumerate(results):
                if i == j:
                    continue
                self.assertNotEqual(result_1, result_2)

    def test_need_rest_in_settlement__from_risk_level(self):
        self.check_rests_from_risk(lambda hero: hero.need_rest_in_settlement)

    def test_need_rest_in_move__from_risk_level(self):
        self.check_rests_from_risk(lambda hero: hero.need_rest_in_move)



class HeroPositionTest(TestCase):

    def setUp(self):
        super(HeroPositionTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

    @mock.patch('game.map.places.prototypes.PlacePrototype.safety', 1.0)
    def test_is_battle_start_needed__safety(self):
        self.assertTrue(all(not self.hero.position.is_battle_start_needed() for i in xrange(100)))

    @mock.patch('game.map.places.prototypes.PlacePrototype.safety', 0.0)
    def test_is_battle_start_needed__no_safety(self):
        self.assertTrue(all(self.hero.position.is_battle_start_needed() for i in xrange(100)))

    @mock.patch('game.map.places.prototypes.PlacePrototype.transport', 0.5)
    def test_modify_move_speed__less(self):
        self.assertEqual(self.hero.position.modify_move_speed(10), 5)

    @mock.patch('game.map.places.prototypes.PlacePrototype.transport', 2.0)
    def test_modify_move_speed_greater(self):
        self.assertEqual(self.hero.position.modify_move_speed(10), 20.0)

    def test_get_neares_place(self):

        for place in places_storage.all():
            x, y = place.x, place.y

            with mock.patch('game.heroes.prototypes.HeroPositionPrototype.cell_coordinates', (x, y)):
                self.assertEqual(place.id, self.hero.position.get_nearest_place().id)


class HeroLevelUpTests(TestCase):

    def setUp(self):
        super(HeroLevelUpTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

    def test_lvl_up(self):
        self.assertEqual(self.hero.level, 1)
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.add_experience(f.exp_on_lvl(1)/2 / self.hero.experience_modifier)
        self.assertEqual(self.hero.level, 1)

        self.hero.add_experience(f.exp_on_lvl(1) / self.hero.experience_modifier)
        self.assertEqual(self.hero.level, 2)
        self.assertEqual(self.hero.experience, f.exp_on_lvl(1)/2)

        self.hero.add_experience(f.exp_on_lvl(2) / self.hero.experience_modifier)
        self.assertEqual(self.hero.level, 3)

        self.hero.add_experience(f.exp_on_lvl(3) / self.hero.experience_modifier)
        self.assertEqual(self.hero.level, 4)

        self.hero.add_experience(f.exp_on_lvl(4) / self.hero.experience_modifier)
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
        passive_abilities = filter(lambda a: a.activation_type._is_PASSIVE, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(len(filter(lambda a: a.activation_type._is_PASSIVE, abilities)), 0)

    def test_get_abilities_for_choose_all_active_slots_busy(self):
        active_abilities = filter(lambda a: a.activation_type._is_ACTIVE, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(len(filter(lambda a: a.activation_type._is_ACTIVE, abilities)), 0)

    def test_get_abilities_for_choose_all_slots_busy(self):
        passive_abilities = filter(lambda a: a.activation_type._is_PASSIVE, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = filter(lambda a: a.activation_type._is_ACTIVE, [a(level=a.MAX_LEVEL) for a in ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(len(abilities), 0)

    @mock.patch('game.heroes.prototypes.HeroPrototype.next_ability_type', ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_slots_busy_but_one_not_max_level(self):
        passive_abilities = filter(lambda a: a.activation_type._is_PASSIVE, [a(level=a.MAX_LEVEL) for a in battle.ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = filter(lambda a: a.activation_type._is_ACTIVE, [a(level=a.MAX_LEVEL) for a in battle.ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        ability = random.choice(self.hero.abilities.abilities.values())
        ability.level -= 1

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(abilities, [ability.__class__(level=ability.level+1)])

    def test_get_abilities_for_choose_all_slots_busy_and_all_not_max_level(self):
        passive_abilities = filter(lambda a: a.activation_type._is_PASSIVE, [a(level=1) for a in ABILITIES.values()])
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = filter(lambda a: a.activation_type._is_ACTIVE, [a(level=1) for a in ABILITIES.values()])
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in xrange(100):
            abilities = self.hero.get_abilities_for_choose()
            self.assertEqual(len(abilities), c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM)


class HeroQuestsTest(TestCase):

    def setUp(self):
        super(HeroQuestsTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)


    def test_special_quests_searchsmith_without_preferences(self):
        self.assertFalse(SearchSmith.TYPE in self.hero.get_special_quests())

    def test_special_quests_searchsmith_with_preferences_without_artifact(self):
        self.hero.equipment._remove_all()
        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)
        self.hero.save()

        self.assertTrue(SearchSmith.TYPE in self.hero.get_special_quests())

    def test_special_quests_searchsmith_with_preferences_with_artifact(self):
        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)
        self.hero.save()

        self.assertTrue(self.hero.equipment.get(EQUIPMENT_SLOT.PLATE) is not None)
        self.assertTrue(SearchSmith.TYPE in self.hero.get_special_quests())

    def test_get_minimum_created_time_of_active_quests(self):
        self.hero._model.quest_created_time = datetime.datetime.now() - datetime.timedelta(days=1)
        self.hero.save()

        result, account_id, bundle_id = register_user('test_user_2')
        hero = HeroPrototype.get_by_account_id(account_id)
        hero._model.quest_created_time = datetime.datetime.now() - datetime.timedelta(days=2)
        hero.save()

        # not there are no another quests an get_minimum_created_time_of_active_quests return now()
        self.assertEqual(hero._model.quest_created_time, HeroPrototype.get_minimum_created_time_of_active_quests())
