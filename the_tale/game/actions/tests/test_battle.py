# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.balance.power import Damage

from the_tale.game.logic import create_test_map

from the_tale.game.actions import battle
from the_tale.game.actions.contexts import BattleContext

from the_tale.game.heroes.habilities.battle import RUN_UP_PUSH, HIT, VAMPIRE_STRIKE
from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.logic_storage import LogicStorage


class BattleTests(testcase.TestCase):

    def setUp(self):
        super(BattleTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.additional_abilities', [VAMPIRE_STRIKE(level=1)])
    def test_hero_actor(self):
        self.hero.health = 10
        self.hero.abilities.add(RUN_UP_PUSH.get_id())

        actor = battle.Actor(self.hero, BattleContext())

        self.assertEqual(self.hero.initiative, actor.initiative)
        self.assertEqual(self.hero.name, actor.name)
        self.assertEqual(self.hero.normalized_name, actor.normalized_name)
        self.assertEqual(self.hero.basic_damage, actor.basic_damage)
        self.assertEqual(self.hero.health, actor.health)
        self.assertEqual(self.hero.max_health, actor.max_health)

        self.assertEqual(actor.change_health(-5), -5)
        self.assertEqual(actor.health, 5)

        self.assertEqual(actor.change_health(-50), -5)
        self.assertEqual(actor.health, 0)

        self.assertEqual(actor.change_health(actor.max_health+50), actor.max_health)
        self.assertEqual(actor.health, actor.max_health)

        hit_selected = False
        run_up_push_selected = False
        vampire_strike_selected = False
        for i in xrange(100):
            ability = actor.choose_ability()

            if ability.get_id() == HIT.get_id():
               hit_selected = True
            elif ability.get_id() == RUN_UP_PUSH.get_id():
                run_up_push_selected = True
            elif ability.get_id() == VAMPIRE_STRIKE.get_id():
                vampire_strike_selected = True

        self.assertTrue(hit_selected)
        self.assertTrue(run_up_push_selected)
        self.assertTrue(vampire_strike_selected)

        self.storage._test_save()

    def test_initiative_change(self):
        actor = battle.Actor(self.hero, BattleContext())
        actor.context.use_initiative([2])
        self.assertEqual(actor.initiative, self.hero.initiative*2)

    @mock.patch('the_tale.game.mobs.prototypes.MobPrototype.additional_abilities', [VAMPIRE_STRIKE(level=1)])
    def test_mob_actor(self):
        mob = mobs_storage.get_random_mob(self.hero)
        mob.health = 10
        mob.abilities.add(RUN_UP_PUSH.get_id())

        actor = battle.Actor(mob, BattleContext())

        self.assertEqual(mob.initiative, actor.initiative)
        self.assertEqual(mob.name, actor.name)
        self.assertEqual(mob.normalized_name, actor.normalized_name)
        self.assertEqual(mob.basic_damage, actor.basic_damage)
        self.assertEqual(mob.health, actor.health)
        self.assertEqual(mob.max_health, actor.max_health)

        self.assertEqual(actor.change_health(-5), -5)
        self.assertEqual(actor.health, 5)

        self.assertEqual(actor.change_health(-50), -5)
        self.assertEqual(actor.health, 0)

        self.assertEqual(actor.change_health(actor.max_health+50), actor.max_health)
        self.assertEqual(actor.health, actor.max_health)

        hit_selected = False
        run_up_push_selected = False
        vampire_strike_selected = False
        for i in xrange(100):
            ability = actor.choose_ability()

            if ability.get_id() == HIT.get_id():
               hit_selected = True
            elif ability.get_id() == RUN_UP_PUSH.get_id():
                run_up_push_selected = True
            elif ability.get_id() == VAMPIRE_STRIKE.get_id():
                vampire_strike_selected = True

        self.assertTrue(hit_selected)
        self.assertTrue(run_up_push_selected)
        self.assertTrue(vampire_strike_selected)

        self.storage._test_save()

    def test_process_effects(self):
        actor = battle.Actor(self.hero, BattleContext())

        actor.context.use_damage_queue_fire([Damage(50, 50), Damage(50, 50)])
        actor.context.use_damage_queue_poison([Damage(50, 50), Damage(50, 50)])
        actor.context.on_own_turn()

        actor.context.use_incoming_damage_modifier(physic=1.0, magic=0.8)
        actor.process_effects(self.hero)
        self.assertEqual(self.hero.health, self.hero.max_health - 180)

        actor.context.on_own_turn()
        actor.context.use_incoming_damage_modifier(physic=1.2, magic=1.0)
        actor.process_effects(self.hero)
        self.assertEqual(self.hero.health, self.hero.max_health - 180 - 220)


    def check_first_strike(self, actor_1, actor_2, turn, expected_actors):
        with mock.patch('the_tale.game.actions.battle.strike') as strike:
            for i in xrange(100):
                actor_1.context.turn = turn
                actor_2.context.turn = turn
                battle.make_turn(actor_1, actor_2, self.hero)

        self.assertEqual(set(id(call[1]['attacker']) for call in strike.call_args_list), expected_actors)

    def get_actors(self):
        mob = mobs_storage.get_random_mob(self.hero)
        actor_1 = battle.Actor(self.hero, BattleContext())
        actor_2 = battle.Actor(mob, BattleContext())

        return actor_1, actor_2

    def test_first_strike__no_actors(self):
        actor_1, actor_2 = self.get_actors()
        self.check_first_strike(actor_1, actor_2, turn=0, expected_actors=set((id(actor_1), id(actor_2))))

    def test_first_strike__actor_1(self):
        actor_1, actor_2 = self.get_actors()
        actor_1.context.use_first_strike()
        self.check_first_strike(actor_1, actor_2, turn=0, expected_actors=set((id(actor_1),)))

    def test_first_strike__actor_2(self):
        actor_1, actor_2 = self.get_actors()
        actor_2.context.use_first_strike()
        self.check_first_strike(actor_1, actor_2, turn=0, expected_actors=set((id(actor_2),)))

    def test_first_strike__actor_1__not_first_turns(self):
        actor_1, actor_2 = self.get_actors()
        actor_1.context.use_first_strike()
        self.check_first_strike(actor_1, actor_2, turn=1, expected_actors=set((id(actor_1), id(actor_2))))

    def test_first_strike__actor_2__not_first_turns(self):
        actor_1, actor_2 = self.get_actors()
        actor_2.context.use_first_strike()
        self.check_first_strike(actor_1, actor_2, turn=1, expected_actors=set((id(actor_1), id(actor_2))))

    def test_first_strike__actors_1_and_2(self):
        actor_1, actor_2 = self.get_actors()
        actor_1.context.use_first_strike()
        actor_2.context.use_first_strike()
        self.check_first_strike(actor_1, actor_2, turn=0, expected_actors=set((id(actor_1), id(actor_2))))

    def test_make_turn__initialize_contexts_on_first_turn(self):
        actor_1, actor_2 = self.get_actors()

        with mock.patch('the_tale.game.actions.battle.strike') as strike:
            with mock.patch('the_tale.game.actions.battle.Actor.update_context') as update_context:
                battle.make_turn(actor_1, actor_2, self.hero)

        self.assertEqual(strike.call_count, 1)
        self.assertEqual(update_context.call_args_list, [mock.call(actor_2), mock.call(actor_1)])


    @mock.patch('the_tale.game.actions.contexts.battle.BattleContext._on_every_turn', mock.Mock())
    def test_last_chance__attacker(self):
        actor_1, actor_2 = self.get_actors()
        actor_1.change_health(-actor_1.health)
        self.assertEqual(actor_1.health, 0)
        actor_1.context.use_last_chance_probability(1.0)
        battle.strike(actor_1, actor_2, mock.Mock())
        self.assertEqual(actor_1.health, 1)

    @mock.patch('the_tale.game.actions.contexts.battle.BattleContext._on_every_turn', mock.Mock())
    def test_last_chance__defender(self):
        actor_1, actor_2 = self.get_actors()
        actor_2.change_health(-actor_2.health)
        self.assertEqual(actor_2.health, 0)
        actor_2.context.use_last_chance_probability(1.0)
        battle.strike(actor_1, actor_2, mock.Mock())
        self.assertEqual(actor_2.health, 1)

    @mock.patch('the_tale.game.actions.contexts.battle.BattleContext._on_every_turn', mock.Mock())
    def test_last_chance__second_use(self):
        actor_1, actor_2 = self.get_actors()
        actor_1.context.use_last_chance_probability(1.0)

        actor_1.change_health(-actor_1.health)
        self.assertEqual(actor_1.health, 0)
        battle.strike(actor_1, actor_2, mock.Mock())
        self.assertEqual(actor_1.health, 1)

        actor_1.change_health(-actor_1.health)
        self.assertEqual(actor_1.health, 0)
        battle.strike(actor_1, actor_2, mock.Mock())
        self.assertEqual(actor_1.health, 1)
