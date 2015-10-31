# coding: utf-8

import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype

from the_tale.game.balance import constants as c

from the_tale.game.pvp.models import Battle1x1, Battle1x1Result
from the_tale.game.pvp.relations import BATTLE_1X1_STATE
from the_tale.game.pvp.prototypes import Battle1x1Prototype
from the_tale.game.pvp.tests.helpers import PvPTestsMixin
from the_tale.game.pvp.abilities import ABILITIES, Flame

from .. import meta_actions


class ArenaPvP1x1Test(testcase.TestCase, PvPTestsMixin):

    def setUp(self):
        super(ArenaPvP1x1Test, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        # for test data reset
        self.hero_1.health = self.hero_1.max_health / 2
        self.hero_1.pvp.set_advantage(1)
        self.hero_1.pvp.set_effectiveness(0.5)

        # for test data reset
        self.hero_2.pvp.set_advantage(1)
        self.hero_2.pvp.set_effectiveness(0.5)

        self.battle_1 = self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.battle_1.calculate_rating = True
        self.battle_1.save()

        self.battle_2 = self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.battle_2.calculate_rating = True
        self.battle_2.save()

        self.meta_action_battle = meta_actions.ArenaPvP1x1.create(self.storage, self.hero_1, self.hero_2)
        self.meta_action_battle.set_storage(self.storage)


    def test_serialization(self):
        self.assertEqual(self.meta_action_battle.serialize(),
                         meta_actions.ArenaPvP1x1.deserialize(self.meta_action_battle.serialize()).serialize())


    def test_initialization(self):
        self.assertTrue(self.meta_action_battle.storage)

        self.assertEqual(self.meta_action_battle.hero_1, self.hero_1)
        self.assertEqual(self.meta_action_battle.hero_2, self.hero_2)

        self.assertEqual(self.meta_action_battle.uid, '%s#%d#%d' % (self.meta_action_battle.TYPE.value, self.hero_1.id, self.hero_2.id))

        # test reset of pvp_data
        self.assertEqual(self.meta_action_battle.hero_1.health, self.hero_1.max_health)
        self.assertEqual(self.meta_action_battle.hero_1.pvp.advantage, 0)
        self.assertEqual(self.meta_action_battle.hero_1.pvp.effectiveness, c.PVP_EFFECTIVENESS_INITIAL)
        self.assertEqual(self.meta_action_battle.hero_1.pvp.energy, 0)
        self.assertEqual(self.meta_action_battle.hero_1.pvp.energy_speed, 1)
        self.assertEqual(self.meta_action_battle.hero_1.pvp.turn_advantage, 0)
        self.assertEqual(self.meta_action_battle.hero_1.pvp.turn_effectiveness, c.PVP_EFFECTIVENESS_INITIAL)
        self.assertEqual(self.meta_action_battle.hero_1.pvp.turn_energy, 0)
        self.assertEqual(self.meta_action_battle.hero_1.pvp.turn_energy_speed, 1)
        self.assertTrue(self.meta_action_battle.hero_1_context.pvp_advantage_strike_damage > 0)

        self.assertEqual(self.meta_action_battle.hero_2.health, self.hero_2.max_health)
        self.assertEqual(self.meta_action_battle.hero_2.pvp.advantage, 0)
        self.assertEqual(self.meta_action_battle.hero_2.pvp.effectiveness, c.PVP_EFFECTIVENESS_INITIAL)
        self.assertEqual(self.meta_action_battle.hero_2.pvp.energy, 0)
        self.assertEqual(self.meta_action_battle.hero_2.pvp.energy_speed, 1)
        self.assertEqual(self.meta_action_battle.hero_2.pvp.turn_advantage, 0)
        self.assertEqual(self.meta_action_battle.hero_2.pvp.turn_effectiveness, c.PVP_EFFECTIVENESS_INITIAL)
        self.assertEqual(self.meta_action_battle.hero_2.pvp.turn_energy, 0)
        self.assertEqual(self.meta_action_battle.hero_2.pvp.turn_energy_speed, 1)
        self.assertTrue(self.meta_action_battle.hero_2_context.pvp_advantage_strike_damage > 0)

    def test_one_hero_killed(self):
        current_time = TimePrototype.get_current_time()
        self.hero_1.health = 0
        self.meta_action_battle.process()
        self.assertEqual(self.meta_action_battle.state, meta_actions.ArenaPvP1x1.STATE.BATTLE_ENDING)
        current_time.increment_turn()
        self.meta_action_battle.process()

        self.assertEqual(self.meta_action_battle.state, meta_actions.ArenaPvP1x1.STATE.PROCESSED)
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

        self.assertEqual(Battle1x1Prototype._model_class.objects.all().count(), 0)

        self.check_hero_pvp_statistics(self.hero_1, 1, 1, 0, 0)
        self.check_hero_pvp_statistics(self.hero_2, 1, 0, 0, 1)

    def test_hero_2_win(self):
        self._end_battle(hero_1_health=0, hero_2_health=self.hero_2.max_health)

        self.assertEqual(Battle1x1Prototype._model_class.objects.all().count(), 0)

        self.check_hero_pvp_statistics(self.hero_1, 1, 0, 0, 1)
        self.check_hero_pvp_statistics(self.hero_2, 1, 1, 0, 0)

    def test_draw(self):
        self._end_battle(hero_1_health=0, hero_2_health=0)

        self.assertEqual(Battle1x1Prototype._model_class.objects.all().count(), 0)

        self.check_hero_pvp_statistics(self.hero_1, 1, 0, 1, 0)
        self.check_hero_pvp_statistics(self.hero_2, 1, 0, 1, 0)

    @mock.patch('the_tale.game.pvp.prototypes.Battle1x1Prototype.calculate_rating', False)
    def test_hero_1_win_no_stats(self):
        self._end_battle(hero_1_health=self.hero_1.max_health, hero_2_health=0)

        self.check_hero_pvp_statistics(self.hero_1, 0, 0, 0, 0)
        self.check_hero_pvp_statistics(self.hero_2, 0, 0, 0, 0)

    @mock.patch('the_tale.game.pvp.prototypes.Battle1x1Prototype.calculate_rating', False)
    def test_hero_2_win_no_stats(self):
        self._end_battle(hero_1_health=0, hero_2_health=self.hero_1.max_health)

        self.check_hero_pvp_statistics(self.hero_1, 0, 0, 0, 0)
        self.check_hero_pvp_statistics(self.hero_2, 0, 0, 0, 0)

    @mock.patch('the_tale.game.pvp.prototypes.Battle1x1Prototype.calculate_rating', False)
    def test_draw_no_stats(self):
        self._end_battle(hero_1_health=0, hero_2_health=0)

        self.check_hero_pvp_statistics(self.hero_1, 0, 0, 0, 0)
        self.check_hero_pvp_statistics(self.hero_2, 0, 0, 0, 0)


    def test_second_process_call_in_one_turn(self):

        with mock.patch('the_tale.game.actions.meta_actions.ArenaPvP1x1._process') as meta_action_process_counter:
            self.meta_action_battle.process()
            self.meta_action_battle.process()

        self.assertEqual(meta_action_process_counter.call_count, 1)

    def test_update_hero_pvp_info(self):
        self.hero_2.pvp.set_effectiveness(50)

        self.meta_action_battle.update_hero_pvp_info(self.hero_2)
        self.assertTrue(self.hero_2.pvp.energy > self.hero_1.pvp.energy)

        self.assertTrue(0 < self.hero_2.pvp.effectiveness < 50)

    # rename quest to fixt segmentation fault
    def test_z_advantage_after_turn(self):
        self.hero_1.pvp.set_effectiveness(50)
        self.hero_2.pvp.set_effectiveness(25)

        self.meta_action_battle.process()

        self.assertTrue(self.hero_1.pvp.advantage > 0)
        self.assertTrue(self.hero_2.pvp.advantage < 0)


    def test_full_battle(self):
        current_time = TimePrototype.get_current_time()

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSING).count(), 2)

        while self.meta_action_battle.state != meta_actions.ArenaPvP1x1.STATE.PROCESSED:
            self.meta_action_battle.process()
            current_time.increment_turn()

        self.assertEqual(self.meta_action_battle.state, meta_actions.ArenaPvP1x1.STATE.PROCESSED)
        self.assertTrue(self.hero_1.is_alive and self.hero_2.is_alive)
        self.assertEqual(self.hero_1.health, self.hero_1.max_health / 2)
        self.assertEqual(self.hero_2.health, self.hero_2.max_health)

        self.assertEqual(Battle1x1.objects.all().count(), 0)
        self.assertEqual(Battle1x1Result.objects.all().count(), 1)

        battle_result = Battle1x1Result.objects.all()[0]

        self.assertNotEqual(battle_result.participant_1_id, battle_result.participant_2_id)

    def test_get_bot_pvp_properties(self):
        properties = self.meta_action_battle.bot_pvp_properties

        self.assertEqual(set(properties.keys()), set(('ability_chance', 'priorities')))
        self.assertTrue(0 < properties['ability_chance'] <= 1)
        self.assertEqual(set(properties['priorities']), set(ABILITIES.keys()))

        for ability_priority in properties['priorities']:
            self.assertTrue(ability_priority > 0)

    def test_process_bot_called__hero_1(self):
        self.hero_1.is_bot = True

        with mock.patch('the_tale.game.actions.meta_actions.ArenaPvP1x1.process_bot') as process_bot:
            self.meta_action_battle.process()

        self.assertEqual(process_bot.call_count, 1)
        self.assertEqual(process_bot.call_args[1]['bot'].id, self.hero_1.id )
        self.assertEqual(process_bot.call_args[1]['enemy'].id, self.hero_2.id )


    def test_process_bot_called__hero_2(self):
        self.hero_2.is_bot = True

        with mock.patch('the_tale.game.actions.meta_actions.ArenaPvP1x1.process_bot') as process_bot:
            self.meta_action_battle.process()

        self.assertEqual(process_bot.call_count, 1)
        self.assertEqual(process_bot.call_args[1]['bot'].id, self.hero_2.id )
        self.assertEqual(process_bot.call_args[1]['enemy'].id, self.hero_1.id )


    def test_process_bot_called__use_ability(self):
        self.hero_1.is_bot = True
        self.hero_1.pvp.set_energy(10)

        properties = self.meta_action_battle.bot_pvp_properties
        properties['ability_chance'] = 1.0

        self.hero_2.pvp.set_energy_speed(2) # flame abilitie will not be used, if enemy energy speed is 1

        self.meta_action_battle.process()

        self.assertTrue(self.hero_1.pvp.energy in (1, 2))

    def test_initialize_bots__bot_is_second(self):
        account_1 = self.accounts_factory.create_account()
        account_2 = self.accounts_factory.create_account(is_bot=True)

        storage = LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1.id]
        hero_2 = storage.accounts_to_heroes[account_2.id]

        hero_1.level = 50
        self.assertEqual(hero_2.level, 1)

        meta_actions.ArenaPvP1x1.create(storage, hero_1, hero_2)

        self.assertEqual(hero_2.level, 50)
        self.assertTrue(len(hero_2.abilities.all) > 1)
        self.assertEqual(hero_2.health, hero_2.max_health)


    def test_initialize_bots__bot_is_first(self):
        account_1 = self.accounts_factory.create_account(is_bot=True)
        account_2 = self.accounts_factory.create_account()

        storage = LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1.id]
        hero_2 = storage.accounts_to_heroes[account_2.id]

        hero_2.level = 50
        self.assertEqual(hero_1.level, 1)

        meta_actions.ArenaPvP1x1.create(storage, hero_1, hero_2)

        self.assertEqual(hero_1.level, 50)
        self.assertTrue(len(hero_1.abilities.all) > 1)
        self.assertEqual(hero_1.health, hero_1.max_health)


    def test_initialize_bots__second_create(self):
        account_1 = self.accounts_factory.create_account()
        account_2 = self.accounts_factory.create_account(is_bot=True)

        storage = LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1.id]
        hero_2 = storage.accounts_to_heroes[account_2.id]

        hero_1.level = 50
        self.assertEqual(hero_2.level, 1)

        self.pvp_create_battle(account_1, account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(account_2, account_1, BATTLE_1X1_STATE.PROCESSING)

        meta_action = meta_actions.ArenaPvP1x1.create(storage, hero_1, hero_2)
        meta_action.process_battle_ending()

        meta_actions.ArenaPvP1x1.create(storage, hero_1, hero_2)

        self.assertEqual(hero_2.level, 50)
        self.assertTrue(len(hero_2.abilities.all) > 1)
        self.assertEqual(hero_2.health, hero_2.max_health)


    def test_process_bot__flame_ability_not_used(self):
        account_1 = self.accounts_factory.create_account(is_bot=True)
        account_2 = self.accounts_factory.create_account()

        storage = LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1.id]
        hero_2 = storage.accounts_to_heroes[account_2.id]

        self.meta_action_battle.bot_pvp_properties = {'priorities': {Flame.TYPE: 1}, 'ability_chance': 1}

        self.assertEqual(hero_2.pvp.energy_speed, 1)

        with mock.patch('the_tale.game.pvp.abilities.Flame.use') as use:
            for i in xrange(100):
                self.meta_action_battle.process_bot(hero_1, hero_2)

        self.assertEqual(use.call_count, 0)
