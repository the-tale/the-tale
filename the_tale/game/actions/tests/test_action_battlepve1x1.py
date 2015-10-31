# coding: utf-8
import mock

import random

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic
from the_tale.game.companions import relations as companions_relations
from the_tale.game.companions.abilities import effects
from the_tale.game.companions.abilities import container


from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power
from the_tale.game import relations as game_relations

from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.mobs import prototypes as mobs_prototypes
from the_tale.game.mobs import relations as mobs_relations

from the_tale.game.logic import create_test_map
from the_tale.game.actions.prototypes import ActionBattlePvE1x1Prototype
from the_tale.game.prototypes import TimePrototype

from the_tale.game.abilities.relations import HELP_CHOICES




class BattlePvE1x1ActionTest(testcase.TestCase):

    def setUp(self):
        super(BattlePvE1x1ActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        self.hero.level = 6
        self.hero.health = self.hero.max_health

        # do half of tests with companion
        if random.random() < 0.5:
            companion_record = companions_storage.companions.enabled_companions().next()
            companion = companions_logic.create_companion(companion_record)
            self.hero.set_companion(companion)
            self.hero.companion.health = 1

        self.action_idl = self.hero.actions.current_action

        with mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 0):
            self.action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.create_mob_for_hero(self.hero))

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_battle.leader, True)
        self.assertEqual(self.action_battle.bundle_id, self.action_idl.bundle_id)
        self.assertEqual(self.action_battle.percents, 0.0)
        self.assertEqual(self.action_battle.state, self.action_battle.STATE.BATTLE_RUNNING)
        self.storage._test_save()

    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_mob_killed(self):
        self.assertEqual(self.hero.statistics.pve_kills, 0)
        self.action_battle.mob.health = 0
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertEqual(self.hero.statistics.pve_kills, 1)
        self.storage._test_save()


    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 0)
    @mock.patch('the_tale.game.balance.constants.GET_LOOT_PROBABILITY', 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_loot(self):
        self.assertEqual(self.hero.statistics.loot_had, 0)
        self.assertEqual(len(self.hero.bag.items()), 0)
        self.action_battle.mob.health = 0
        self.storage.process_turn()
        self.assertEqual(self.hero.statistics.loot_had, 1)
        self.assertEqual(len(self.hero.bag.items()), 1)
        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_artifacts(self):
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.assertEqual(len(self.hero.bag.items()), 0)
        self.action_battle.mob.health = 0
        self.storage.process_turn()
        self.assertEqual(self.hero.statistics.artifacts_had, 1)
        self.assertEqual(len(self.hero.bag.items()), 1)
        self.storage._test_save()

    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_hero_killed(self):
        self.assertEqual(self.hero.statistics.pve_deaths, 0)
        self.hero.health = 0
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertTrue(not self.hero.is_alive)
        self.assertEqual(self.hero.statistics.pve_deaths, 1)
        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_hero_and_mob_killed(self):
        self.hero.health = 0
        self.action_battle.mob.health = 0
        with self.check_not_changed(lambda: self.hero.statistics.artifacts_had):
            with self.check_not_changed(lambda: self.hero.bag.occupation):
                self.storage.process_turn(continue_steps_if_needed=False)
        self.assertTrue(self.hero.journal.messages[-1].key.is_ACTION_BATTLEPVE1X1_JOURNAL_HERO_AND_MOB_KILLED)
        self.assertTrue(self.hero.diary.messages[-1].key.is_ACTION_BATTLEPVE1X1_DIARY_HERO_AND_MOB_KILLED)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertTrue(not self.hero.is_alive)
        self.assertEqual(self.hero.statistics.pve_deaths, 1)
        self.storage._test_save()

    def test_full_battle(self):

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()


    def test_full_battle__with_companion(self):
        battle_ability = random.choice([ability
                                        for ability in effects.ABILITIES.records
                                        if isinstance(ability.effect, effects.BaseBattleAbility)])

        companion_record = companions_storage.companions.enabled_companions().next()
        companion_record.abilities = container.Container(start=(battle_ability,))

        companion = companions_logic.create_companion(companion_record)
        self.hero.set_companion(companion)

        self.hero.reset_accessors_cache()

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage_probability', 0.0)
    @mock.patch('the_tale.game.balance.constants.COMPANIONS_WOUNDS_IN_HOUR_FROM_HEAL', 0.0)
    @mock.patch('the_tale.game.balance.constants.COMPANIONS_EATEN_CORPSES_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.mobs.prototypes.MobPrototype.mob_type', game_relations.BEING_TYPE.ANIMAL)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_eat_corpses', lambda hero: True)
    def test_full_battle__with_companion__eat_corpse(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.hero.reset_accessors_cache()

        self.hero.companion.health = 10

        current_time = TimePrototype.get_current_time()

        while self.hero.actions.current_action.TYPE == ActionBattlePvE1x1Prototype.TYPE:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.companion.health, 10 + c.COMPANIONS_EATEN_CORPSES_HEAL_AMOUNT)

        self.storage._test_save()

    def test_bit_mob(self):
        old_mob_health = self.action_battle.mob.health
        old_action_percents = self.action_battle.percents

        self.action_battle.bit_mob(0.33)

        self.assertTrue(self.action_battle.mob.health < old_mob_health)
        self.assertTrue(self.action_battle.percents > old_action_percents)
        self.assertTrue(self.action_battle.updated)

    def test_bit_mob_and_kill(self):

        self.action_battle.bit_mob(1)

        self.assertEqual(self.action_battle.mob.health, self.action_battle.mob.max_health - 1)
        self.assertTrue(0 < self.action_battle.percents < 1)
        self.assertTrue(self.action_battle.updated)

        self.assertEqual(self.action_battle.state, self.action_battle.STATE.BATTLE_RUNNING)

        self.action_battle.bit_mob(self.action_battle.mob.max_health)
        self.assertEqual(self.action_battle.mob.health, 0)
        self.assertEqual(self.action_battle.percents, 1)
        self.assertTrue(self.action_battle.updated)

        self.assertEqual(self.action_battle.state, self.action_battle.STATE.PROCESSED)

    def test_fast_resurrect__not_processed(self):
        self.action_battle.hero.kill()
        self.assertFalse(self.action_battle.fast_resurrect())
        self.assertFalse(self.action_battle.hero.is_alive)

    def test_fast_resurrect__hero_is_alive(self):
        self.action_battle.state = self.action_battle.STATE.PROCESSED
        self.assertFalse(self.action_battle.fast_resurrect())
        self.assertTrue(self.action_battle.hero.is_alive)

    def test_fast_resurrect__success(self):
        self.action_battle.hero.kill()
        self.action_battle.state = self.action_battle.STATE.PROCESSED
        self.assertTrue(self.action_battle.fast_resurrect())
        self.assertTrue(self.action_battle.hero.is_alive)

    def test_help_choices(self):
        self.assertTrue(HELP_CHOICES.LIGHTING in self.action_battle.HELP_CHOICES)

        self.action_battle.mob.health = 0
        self.assertFalse(HELP_CHOICES.LIGHTING in self.action_battle.HELP_CHOICES)

        self.action_battle.mob.health = 1
        self.action_battle.hero.kill()

        self.assertEqual(self.action_battle.HELP_CHOICES, set((HELP_CHOICES.RESURRECT,)))

    @mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 1.01)
    @mock.patch('the_tale.game.heroes.habits.Honor.interval', game_relations.HABIT_HONOR_INTERVAL.LEFT_3)
    def test_kill_before_start(self):

        self.hero.actions.pop_action()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 1):
            action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.create_mob_for_hero(self.hero))

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)


    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_do_exorcism', lambda hero: True)
    def test_companion_exorcims__demon(self):

        self.companion_record = companions_logic.create_random_companion_record('exorcist', state=companions_relations.STATE.ENABLED)
        self.hero.set_companion(companions_logic.create_companion(self.companion_record))

        demon_record = mobs_prototypes.MobRecordPrototype.create_random('demon', type=game_relations.BEING_TYPE.DEMON)
        demon = mobs_prototypes.MobPrototype(record_id=demon_record.id, level=self.hero.level, is_boss=False)

        self.hero.actions.pop_action()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 1):
            action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=demon)

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_do_exorcism', lambda hero: True)
    def test_companion_exorcims__not_demon(self):

        self.companion_record = companions_logic.create_random_companion_record('exorcist', state=companions_relations.STATE.ENABLED)
        self.hero.set_companion(companions_logic.create_companion(self.companion_record))

        not_demon_record = mobs_prototypes.MobRecordPrototype.create_random('demon', type=game_relations.BEING_TYPE.random(exclude=(game_relations.BEING_TYPE.DEMON, )))
        not_demon = mobs_prototypes.MobPrototype(record_id=not_demon_record.id, level=self.hero.level, is_boss=False)

        self.hero.actions.pop_action()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 0):
            action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=not_demon)

        self.assertEqual(action_battle.percents, 0.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.BATTLE_RUNNING)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, action_battle)


    @mock.patch('the_tale.game.balance.constants.PEACEFULL_BATTLE_PROBABILITY', 1.01)
    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_3)
    def test_peacefull_battle(self):

        self.hero.actions.pop_action()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 0):
            action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.create_mob_for_hero(self.hero))

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_leave_battle_in_fear', lambda self: True)
    def test_fear_battle(self):

        self.hero.actions.pop_action()

        mob = (m for m in mobs_storage.all() if m.type.is_CIVILIZED).next()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 0):
            action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob.create_mob(self.hero, is_boss=False))

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)


    @mock.patch('the_tale.game.balance.constants.EXP_FOR_KILL_PROBABILITY', 1.01)
    @mock.patch('the_tale.game.balance.constants.EXP_FOR_KILL_DELTA', 0)
    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_3)
    def test_experience_for_kill(self):
        mob = mobs_storage.create_mob_for_hero(self.hero)
        mob.health = 0

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 1):
            with mock.patch('the_tale.game.heroes.objects.Hero.add_experience') as add_experience:
                with mock.patch('the_tale.game.actions.prototypes.ActionBattlePvE1x1Prototype.process_artifact_breaking') as process_artifact_breaking:
                    action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)
                    self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(add_experience.call_args_list, [mock.call(c.EXP_FOR_KILL)])
        self.assertEqual(process_artifact_breaking.call_count, 1)

        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)


    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_BREAKS_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.artifacts.prototypes.ArtifactPrototype.can_be_broken', lambda self: True)
    def test_process_artifact_breaking__no_equipment(self):
        self.hero.equipment._remove_all()
        old_power = self.hero.power.clone()
        self.action_battle.process_artifact_breaking()
        self.assertEqual(old_power, self.hero.power)

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_BREAKS_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.artifacts.prototypes.ArtifactPrototype.can_be_broken', lambda self: True)
    def test_process_artifact_breaking__broken(self):
        for artifact in self.hero.equipment.values():
            artifact.power = Power(100, 100)

        old_power = self.hero.power.total()
        self.action_battle.process_artifact_breaking()
        self.assertTrue(old_power > self.hero.power.total())

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_BREAKS_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.artifacts.prototypes.ArtifactPrototype.can_be_broken', lambda self: False)
    def test_process_artifact_breaking__not_broken(self):
        for artifact in self.hero.equipment.values():
            artifact.power = Power(100, 100)

        old_power = self.hero.power.total()
        self.action_battle.process_artifact_breaking()
        self.assertEqual(old_power, self.hero.power.total())

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_BREAKS_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.artifacts.prototypes.ArtifactPrototype.can_be_broken', lambda self: False)
    def test_process_artifact_breaking__break_only_mostly_damaged(self):
        for artifact in self.hero.equipment.values():
            artifact.power = Power(100, 100)
            artifact.integrity = 0

        artifact.integrity = artifact.max_integrity

        for i in xrange(100):
            self.action_battle.process_artifact_breaking()

        self.assertEqual(artifact.power, Power(100, 100))


    def test_process_artifact_breaking__integrity_damage(self):
        for artifact in self.hero.equipment.values():
            artifact.integrity = artifact.max_integrity

        self.action_battle.process_artifact_breaking()

        for artifact in self.hero.equipment.values():
            self.assertEqual(artifact.integrity, artifact.max_integrity - 1)
