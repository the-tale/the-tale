# coding: utf-8

import random

import mock

from dext.settings import settings

from common.utils.testcase import TestCase, CallCounter

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic_storage import LogicStorage

from game.logic import create_test_map
from game.prototypes import TimePrototype

from game.actions.meta_actions import MetaActionArenaPvP1x1Prototype
from game.actions.models import MetaAction, MetaActionMember

from game.pvp.models import Battle1x1

from game.pvp.models import BATTLE_1X1_STATE, BATTLE_RESULT
from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.tests.helpers import PvPTestsMixin
from game.pvp.combat_styles import COMBAT_STYLES

class ArenaPvP1x1MetaActionTest(TestCase, PvPTestsMixin):

    def setUp(self):
        settings.refresh()

        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user_1')
        result, account_2_id, bundle_id = register_user('test_user_2')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.hero_1.health = self.hero_1.max_health / 2
        self.hero_1.pvp_advantage = 1
        self.hero_1.pvp_rage = 390

        self.battle_1 = self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.battle_1.calculate_rating = True
        self.battle_1.save()

        self.battle_2 = self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.battle_2.calculate_rating = True
        self.battle_2.save()

        self.meta_action_battle = MetaActionArenaPvP1x1Prototype.create(self.storage, self.hero_1, self.hero_2)
        self.meta_action_battle.set_storage(self.storage)


    def test_initialization(self):
        self.assertEqual(MetaAction.objects.all().count(), 1)
        self.assertEqual(MetaActionMember.objects.all().count(), 2)

        self.assertEqual(len(self.meta_action_battle.members), 2)
        self.assertEqual(len(self.meta_action_battle.members_by_roles), 2)
        self.assertTrue(self.meta_action_battle.storage)

        self.assertEqual(self.meta_action_battle.hero_1, self.hero_1)
        self.assertEqual(self.meta_action_battle.hero_2, self.hero_2)

        self.assertEqual(self.meta_action_battle.hero_1.health, self.hero_1.max_health)
        self.assertEqual(self.meta_action_battle.hero_1.pvp_combat_style, None)
        self.assertEqual(self.meta_action_battle.hero_1.pvp_advantage, 0)
        self.assertEqual(self.meta_action_battle.hero_1.pvp_power, 0)
        self.assertEqual(self.meta_action_battle.hero_1.pvp_power_modified, 0)
        self.assertEqual(self.meta_action_battle.hero_1.pvp_rage, 0)
        self.assertEqual(self.meta_action_battle.hero_1.pvp_initiative, 0)
        self.assertEqual(self.meta_action_battle.hero_1.pvp_concentration, 0)
        self.assertTrue(self.meta_action_battle.hero_1_context.pvp_advantage_strike_damage > 0)

        self.assertEqual(self.meta_action_battle.hero_2.health, self.hero_2.max_health)
        self.assertEqual(self.meta_action_battle.hero_2.pvp_combat_style, None)
        self.assertEqual(self.meta_action_battle.hero_2.pvp_advantage, 0)
        self.assertEqual(self.meta_action_battle.hero_2.pvp_power, 0)
        self.assertEqual(self.meta_action_battle.hero_2.pvp_power_modified, 0)
        self.assertEqual(self.meta_action_battle.hero_2.pvp_rage, 0)
        self.assertEqual(self.meta_action_battle.hero_2.pvp_initiative, 0)
        self.assertEqual(self.meta_action_battle.hero_2.pvp_concentration, 0)
        self.assertTrue(self.meta_action_battle.hero_2_context.pvp_advantage_strike_damage > 0)

    def test_one_hero_killed(self):
        current_time = TimePrototype.get_current_time()
        self.hero_1.health = 0
        self.meta_action_battle.process()
        self.assertEqual(self.meta_action_battle.state, MetaActionArenaPvP1x1Prototype.STATE.BATTLE_ENDING)
        current_time.increment_turn()
        self.meta_action_battle.process()

        self.assertEqual(self.meta_action_battle.state, MetaActionArenaPvP1x1Prototype.STATE.PROCESSED)
        self.assertTrue(self.hero_1.is_alive and self.hero_2.is_alive)
        self.assertEqual(self.hero_1.health, self.hero_1.max_health / 2)
        self.assertEqual(self.hero_2.health, self.hero_2.max_health)

    def check_hero_pvp_statistics(self, hero, battles, victories, draws, defeats):
        self.assertEqual(hero.statistics.pvp_battles_1x1_number, battles)
        self.assertEqual(hero.statistics.pvp_battles_1x1_victories, victories)
        self.assertEqual(hero.statistics.pvp_battles_1x1_draws, draws)
        self.assertEqual(hero.statistics.pvp_battles_1x1_defeats, defeats)

    def _end_battle(self, hero_1_health, hero_2_health):
        self.hero_1.health = hero_1_health
        self.hero_2.health = hero_2_health
        current_time = TimePrototype.get_current_time()
        self.meta_action_battle.process()
        current_time.increment_turn()
        self.meta_action_battle.process()

    def test_hero_1_win(self):
        self._end_battle(hero_1_health=self.hero_1.max_health, hero_2_health=0)

        self.assertTrue(Battle1x1Prototype.get_by_id(self.battle_1.id).result.is_victory)
        self.assertTrue(Battle1x1Prototype.get_by_id(self.battle_2.id).result.is_defeat)

        self.check_hero_pvp_statistics(self.hero_1, 1, 1, 0, 0)
        self.check_hero_pvp_statistics(self.hero_2, 1, 0, 0, 1)

    def test_hero_2_win(self):
        self._end_battle(hero_1_health=0, hero_2_health=self.hero_2.max_health)

        self.assertTrue(Battle1x1Prototype.get_by_id(self.battle_1.id).result.is_defeat)
        self.assertTrue(Battle1x1Prototype.get_by_id(self.battle_2.id).result.is_victory)

        self.check_hero_pvp_statistics(self.hero_1, 1, 0, 0, 1)
        self.check_hero_pvp_statistics(self.hero_2, 1, 1, 0, 0)

    def test_draw(self):
        self._end_battle(hero_1_health=0, hero_2_health=0)

        self.assertTrue(Battle1x1Prototype.get_by_id(self.battle_1.id).result.is_draw)
        self.assertTrue(Battle1x1Prototype.get_by_id(self.battle_2.id).result.is_draw)

        self.check_hero_pvp_statistics(self.hero_1, 1, 0, 1, 0)
        self.check_hero_pvp_statistics(self.hero_2, 1, 0, 1, 0)

    @mock.patch('game.pvp.prototypes.Battle1x1Prototype.calculate_rating', False)
    def test_hero_1_win_no_stats(self):
        self._end_battle(hero_1_health=self.hero_1.max_health, hero_2_health=0)

        self.check_hero_pvp_statistics(self.hero_1, 0, 0, 0, 0)
        self.check_hero_pvp_statistics(self.hero_2, 0, 0, 0, 0)

    @mock.patch('game.pvp.prototypes.Battle1x1Prototype.calculate_rating', False)
    def test_hero_2_win_no_stats(self):
        self._end_battle(hero_1_health=0, hero_2_health=self.hero_1.max_health)

        self.check_hero_pvp_statistics(self.hero_1, 0, 0, 0, 0)
        self.check_hero_pvp_statistics(self.hero_2, 0, 0, 0, 0)

    @mock.patch('game.pvp.prototypes.Battle1x1Prototype.calculate_rating', False)
    def test_draw_no_stats(self):
        self._end_battle(hero_1_health=0, hero_2_health=0)

        self.check_hero_pvp_statistics(self.hero_1, 0, 0, 0, 0)
        self.check_hero_pvp_statistics(self.hero_2, 0, 0, 0, 0)


    def test_second_process_call_in_one_turn(self):

        meta_action_process_counter = CallCounter()

        with mock.patch('game.actions.meta_actions.MetaActionArenaPvP1x1Prototype._process', meta_action_process_counter):
            self.meta_action_battle.process()
            self.meta_action_battle.process()

        self.assertEqual(meta_action_process_counter.count, 1)

    def test_update_hero_pvp_info(self):
        self.hero_2.pvp_power = 50

        self.meta_action_battle.update_hero_pvp_info(self.hero_2, self.hero_1)

        self.assertTrue(self.hero_2.pvp_rage > self.hero_1.pvp_rage)
        self.assertTrue(self.hero_2.pvp_initiative > self.hero_1.pvp_initiative)
        self.assertTrue(self.hero_2.pvp_concentration > self.hero_1.pvp_concentration)

        self.assertTrue(0 < self.hero_2.pvp_power < 50)
        self.assertEqual(self.hero_2.pvp_power, self.hero_2.pvp_power_modified)


    def test_update_hero_pvp_info_with_styles(self):
        combat_style_1 = random.choice(COMBAT_STYLES.values())
        combat_style_2 = COMBAT_STYLES[combat_style_1.advantages[0][0]]

        combat_style_1._give_resources_to_hero(self.hero_1)
        combat_style_1.apply_to_hero(self.hero_1, self.hero_2)

        combat_style_2._give_resources_to_hero(self.hero_2)
        combat_style_2.apply_to_hero(self.hero_2, self.hero_1)

        self.meta_action_battle.update_hero_pvp_info(self.hero_1, self.hero_2)

        self.assertTrue(0 < self.hero_1.pvp_power)
        self.assertTrue(self.hero_1.pvp_power < self.hero_1.pvp_power_modified)

    def test_advantage_after_turn(self):
        combat_style_1 = random.choice(COMBAT_STYLES.values())
        combat_style_2 = COMBAT_STYLES[combat_style_1.advantages[0][0]]

        combat_style_1._give_resources_to_hero(self.hero_1)
        combat_style_1.apply_to_hero(self.hero_1, self.hero_2)

        combat_style_2._give_resources_to_hero(self.hero_2)
        combat_style_2.apply_to_hero(self.hero_2, self.hero_1)

        self.meta_action_battle.process()

        self.assertTrue(self.hero_1.pvp_advantage > 0)
        self.assertTrue(self.hero_2.pvp_advantage < 0)


    def test_full_battle(self):
        current_time = TimePrototype.get_current_time()

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSING).count(), 2)

        while self.meta_action_battle.state != MetaActionArenaPvP1x1Prototype.STATE.PROCESSED:
            self.meta_action_battle.process()
            current_time.increment_turn()

        self.assertEqual(self.meta_action_battle.state, MetaActionArenaPvP1x1Prototype.STATE.PROCESSED)
        self.assertTrue(self.hero_1.is_alive and self.hero_2.is_alive)
        self.assertEqual(self.hero_1.health, self.hero_1.max_health / 2)
        self.assertEqual(self.hero_2.health, self.hero_2.max_health)

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSED).count(), 2)
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_RESULT.UNKNOWN).count(), 0)

    def test_remove(self):
        self.assertEqual(MetaAction.objects.all().count(), 1)
        self.assertEqual(MetaActionMember.objects.all().count(), 2)
        self.meta_action_battle.remove()
        self.assertEqual(MetaAction.objects.all().count(), 0)
        self.assertEqual(MetaActionMember.objects.all().count(), 0)
