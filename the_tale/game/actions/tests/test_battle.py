# coding: utf-8
import random
import contextlib

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.balance import power as p
from the_tale.game.balance import constants as c

from the_tale.game.logic import create_test_map

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.actions import battle
from the_tale.game.actions.contexts import BattleContext

from the_tale.game.heroes.habilities.battle import RUN_UP_PUSH, HIT, VAMPIRE_STRIKE
from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.logic_storage import LogicStorage


class TestsBase(testcase.TestCase):

    def setUp(self):
        super(TestsBase, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

    def get_actors(self):
        mob = mobs_storage.get_random_mob(self.hero)
        actor_1 = battle.Actor(self.hero, BattleContext())
        actor_2 = battle.Actor(mob, BattleContext())

        return actor_1, actor_2


    def set_hero_companion(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        companion = companions_logic.create_companion(companion_record)
        self.hero.set_companion(companion)


class BattleTests(TestsBase):

    @mock.patch('the_tale.game.heroes.objects.Hero.additional_abilities', [VAMPIRE_STRIKE(level=1)])
    def test_hero_actor(self):
        self.hero.health = 10
        self.hero.abilities.add(RUN_UP_PUSH.get_id())

        actor = battle.Actor(self.hero, BattleContext())

        self.assertEqual(self.hero.initiative, actor.initiative)
        self.assertEqual(self.hero.name, actor.name)
        self.assertEqual(self.hero.utg_name, actor.utg_name)
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

    def test_choose_ability__additional_abilities(self):
        from the_tale.game.heroes.habilities import ABILITIES
        all_abilities = [ability(level=ability.MAX_LEVEL) for ability in ABILITIES.values()]

        active_abilities = set(ability.get_id() for ability in all_abilities if ability.activation_type.is_ACTIVE)

        self.hero.health = 1 # allow regeneration

        actor = battle.Actor(self.hero, BattleContext())

        chosen_abilities = set()

        with mock.patch('the_tale.game.heroes.objects.Hero.additional_abilities', all_abilities):
            for i in xrange(1000):
                chosen_abilities.add(actor.choose_ability().get_id())

        self.assertEqual(active_abilities, chosen_abilities)


    def test_choose_ability__additional_companion_abilities(self):
        from the_tale.game.heroes.habilities import ABILITIES
        from the_tale.game.companions.abilities import effects as companions_effects
        from the_tale.game.companions.abilities import container as abilities_container
        from the_tale.game.companions import logic as companions_logic
        from the_tale.game.companions import relations as companions_relations

        abilities = [ability for ability in companions_effects.ABILITIES.records
                     if ( isinstance(ability.effect, companions_effects.BaseBattleAbility) and
                          ability.effect.ABILITY.get_id() != 'hit' )]
        companion_ability = random.choice(abilities)

        all_abilities = [ability(level=ability.MAX_LEVEL)
                         for ability in ABILITIES.values()
                         if ability.get_id() != companion_ability.effect.ABILITY.get_id()]

        active_abilities = set(ability.get_id() for ability in ABILITIES.values() if ability.ACTIVATION_TYPE.is_ACTIVE)

        companion_record = companions_logic.create_random_companion_record(u'battle',
                                                                           abilities=abilities_container.Container(start=(companion_ability,)),
                                                                           state=companions_relations.STATE.ENABLED)
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.hero.health = 1 # allow regeneration

        actor = battle.Actor(self.hero, BattleContext())

        chosen_abilities = set()

        # mock abilities modify_attribute instead of hereos, since we test correct work of it
        def modify_attribute(self, modifier, value):
            if modifier.is_ADDITIONAL_ABILITIES:
                return all_abilities
            return value

        with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.modify_attribute', modify_attribute):
            for i in xrange(1000):
                chosen_abilities.add(actor.choose_ability().get_id())

        self.assertEqual(len(active_abilities), len(chosen_abilities) + 1)
        self.assertEqual(active_abilities - set([companion_ability.effect.ABILITY.get_id()]), chosen_abilities)

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
        self.assertEqual(mob.utg_name, actor.utg_name)
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

        actor.context.use_damage_queue_fire([p.Damage(50, 50), p.Damage(50, 50)])
        actor.context.use_damage_queue_poison([p.Damage(50, 50), p.Damage(50, 50)])
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


class TryCompanionBlockTests(TestsBase):

    @mock.patch('the_tale.game.actions.battle.try_companion_block', mock.Mock(return_value=True))
    def test_try_companion_block__successed(self):
        actor_1, actor_2 = self.get_actors()

        with mock.patch('the_tale.game.actions.battle.strike_without_contact') as strike_without_contact:
            with mock.patch('the_tale.game.actions.battle.strike_with_contact') as strike_with_contact:
                battle.make_turn(actor_1, actor_2, self.hero)

        self.assertEqual(strike_without_contact.call_count, 0)
        self.assertEqual(strike_with_contact.call_count, 0)

    @mock.patch('the_tale.game.actions.battle.try_companion_block', mock.Mock(return_value=False))
    def test_try_companion_block__failed(self):
        actor_1, actor_2 = self.get_actors()

        with mock.patch('the_tale.game.actions.battle.strike_without_contact') as strike_without_contact:
            with mock.patch('the_tale.game.actions.battle.strike_with_contact') as strike_with_contact:
                battle.make_turn(actor_1, actor_2, self.hero)

        self.assertEqual(strike_without_contact.call_count+strike_with_contact.call_count, 1)


    @mock.patch('the_tale.game.balance.formulas.companions_defend_in_battle_probability', mock.Mock(return_value=1.0))
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage_probability', 1.0)
    def test_no_companion(self):
        actor_1, actor_2 = self.get_actors()

        self.assertFalse(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        self.assertFalse(battle.try_companion_block(attacker=actor_2, defender=actor_1, messenger=self.hero))


    @mock.patch('the_tale.game.balance.formulas.companions_defend_in_battle_probability', mock.Mock(return_value=1.0))
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage_probability', 1.0)
    def test_no_companion__attacker_has_companion(self):
        actor_1, actor_2 = self.get_actors()

        self.set_hero_companion()

        self.assertTrue(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        self.assertFalse(battle.try_companion_block(attacker=actor_1, defender=actor_2, messenger=self.hero))


    @mock.patch('the_tale.game.balance.formulas.companions_defend_in_battle_probability', mock.Mock(return_value=0.0))
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage_probability', 1.0)
    def test_not_defend(self):
        actor_1, actor_2 = self.get_actors()

        self.set_hero_companion()

        self.assertTrue(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        with self.check_not_changed(self.hero.diary.__len__):
            with self.check_not_changed(self.hero.journal.__len__):
                with self.check_not_changed(lambda: self.hero.companion.health):
                    self.assertFalse(battle.try_companion_block(attacker=actor_2, defender=actor_1, messenger=self.hero))


    @mock.patch('the_tale.game.balance.formulas.companions_defend_in_battle_probability', mock.Mock(return_value=1.0))
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage_probability', 0.0)
    @mock.patch('the_tale.game.balance.constants.COMPANIONS_WOUNDS_IN_HOUR_FROM_HEAL', 0.0)
    def test_success_block(self):
        actor_1, actor_2 = self.get_actors()

        self.set_hero_companion()

        self.assertTrue(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        with self.check_not_changed(self.hero.diary.__len__):
            with self.check_delta(self.hero.journal.__len__, 1):
                with self.check_not_changed(lambda: self.hero.companion.health):
                    self.assertTrue(battle.try_companion_block(attacker=actor_2, defender=actor_1, messenger=self.hero))

        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_BLOCK)


    @mock.patch('the_tale.game.balance.formulas.companions_defend_in_battle_probability', mock.Mock(return_value=1.0))
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage_probability', 1.0)
    def test_wounded_on_block(self):
        actor_1, actor_2 = self.get_actors()

        self.set_hero_companion()

        self.assertTrue(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        with self.check_not_changed(self.hero.diary.__len__):
            with self.check_delta(self.hero.journal.__len__, 1):
                with self.check_delta(lambda: self.hero.companion.health, -c.COMPANIONS_DAMAGE_PER_WOUND):
                    self.assertTrue(battle.try_companion_block(attacker=actor_2, defender=actor_1, messenger=self.hero))

        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_WOUND)


    @mock.patch('the_tale.game.balance.formulas.companions_defend_in_battle_probability', mock.Mock(return_value=1.0))
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage_probability', 1.0)
    def test_killed_on_block(self):
        actor_1, actor_2 = self.get_actors()

        self.set_hero_companion()

        self.assertTrue(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        with self.check_delta(self.hero.diary.__len__, 1):
            while self.hero.companion:
                self.assertTrue(battle.try_companion_block(attacker=actor_2, defender=actor_1, messenger=self.hero))

        self.assertEqual(self.hero.companion, None)
        self.assertFalse(actor_1.has_companion)
        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_KILLED)


    @mock.patch('the_tale.game.balance.formulas.companions_defend_in_battle_probability', mock.Mock(return_value=1.0))
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage_probability', 1.0)
    @mock.patch('the_tale.game.heroes.messages.JournalContainer.MESSAGES_LOG_LENGTH', 10000)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_broke_to_spare_parts', lambda self: True)
    def test_killed_on_block__has_spare_parts(self):
        actor_1, actor_2 = self.get_actors()

        self.set_hero_companion()

        self.assertTrue(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        with contextlib.nested(
            self.check_increased(lambda: self.hero.money),
            self.check_increased(lambda: self.hero.statistics.money_earned_from_companions),
            self.check_delta(self.hero.diary.__len__, 2)):

            while self.hero.companion:
                self.assertTrue(battle.try_companion_block(attacker=actor_2, defender=actor_1, messenger=self.hero))

        self.assertEqual(self.hero.companion, None)
        self.assertFalse(actor_1.has_companion)
        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_BROKE_TO_SPARE_PARTS)


class TryCompanionStrikeTests(TestsBase):

    def setUp(self):
        super(TryCompanionStrikeTests, self).setUp()
        self.set_hero_companion()


    @mock.patch('the_tale.game.balance.constants.COMPANIONS_BATTLE_STRIKE_PROBABILITY', 1.0)
    def test_no_companion(self):
        self.hero.remove_companion()

        actor_1, actor_2 = self.get_actors()

        self.assertFalse(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        self.assertFalse(battle.try_companion_strike(attacker=actor_1, defender=actor_2, messenger=self.hero))


    @mock.patch('the_tale.game.balance.constants.COMPANIONS_BATTLE_STRIKE_PROBABILITY', 0.0)
    def test_no_probability(self):
        actor_1, actor_2 = self.get_actors()

        self.assertTrue(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        self.assertFalse(battle.try_companion_strike(attacker=actor_1, defender=actor_2, messenger=self.hero))


    @mock.patch('the_tale.game.balance.constants.COMPANIONS_BATTLE_STRIKE_PROBABILITY', 1.0)
    def test_no_battle_abilities(self):
        actor_1, actor_2 = self.get_actors()

        self.assertTrue(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        self.assertFalse(battle.try_companion_strike(attacker=actor_1, defender=actor_2, messenger=self.hero))


    @mock.patch('the_tale.game.balance.constants.COMPANIONS_BATTLE_STRIKE_PROBABILITY', 1.0)
    def test_strike(self):
        from the_tale.game.companions.abilities import effects
        from the_tale.game.companions.abilities import container

        battle_ability = random.choice([ability
                                        for ability in effects.ABILITIES.records
                                        if isinstance(ability.effect, effects.BaseBattleAbility)])
        self.hero.companion.record.abilities = container.Container(start=(battle_ability,))
        self.hero.reset_accessors_cache()

        actor_1, actor_2 = self.get_actors()

        self.assertTrue(actor_1.has_companion)
        self.assertFalse(actor_2.has_companion)

        self.assertTrue(battle.try_companion_strike(attacker=actor_1, defender=actor_2, messenger=self.hero))
