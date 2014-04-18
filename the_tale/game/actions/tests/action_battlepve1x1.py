# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power

from the_tale.game.heroes.logic import create_mob_for_hero
from the_tale.game.heroes.relations import HABIT_HONOR_INTERVAL, HABIT_PEACEFULNESS_INTERVAL

from the_tale.game.mobs.storage import mobs_storage

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
        self.action_idl = self.hero.actions.current_action

        with mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 0):
            self.action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=create_mob_for_hero(self.hero))

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
        self.storage.process_turn(second_step_if_needed=False)
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
        self.storage.process_turn(second_step_if_needed=False)
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

    def test_bit_mob(self):
        old_mob_health = self.action_battle.mob.health
        old_action_percents = self.action_battle.percents

        self.action_battle.bit_mob(0.33)

        self.assertTrue(self.action_battle.mob.health < old_mob_health)
        self.assertTrue(self.action_battle.percents > old_action_percents)
        self.assertTrue(self.action_battle.updated)

    def test_bit_mob_and_kill(self):

        self.action_battle.bit_mob(1)

        self.assertEqual(self.action_battle.mob.health, 0)
        self.assertEqual(self.action_battle.percents, 1)
        self.assertTrue(self.action_battle.updated)

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
    @mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.LEFT_3)
    def test_kill_before_start(self):

        self.hero.actions.pop_action()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 1):
            action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=create_mob_for_hero(self.hero))

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)


    @mock.patch('the_tale.game.balance.constants.PEACEFULL_BATTLE_PROBABILITY', 1.01)
    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', HABIT_PEACEFULNESS_INTERVAL.RIGHT_3)
    def test_peacefull_battle(self):

        self.hero.actions.pop_action()

        mob = (m for m in mobs_storage.all() if m.type.is_CIVILIZED).next()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 0):
            action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob.create_mob(self.hero, is_boss=False))

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)


    @mock.patch('the_tale.game.balance.constants.EXP_FOR_KILL_PROBABILITY', 1.01)
    @mock.patch('the_tale.game.balance.constants.EXP_FOR_KILL_DELTA', 0)
    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', HABIT_PEACEFULNESS_INTERVAL.LEFT_3)
    def test_experience_for_kill(self):
        mob = create_mob_for_hero(self.hero)
        mob.health = 0

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 1):
            with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.add_experience') as add_experience:
                with mock.patch('the_tale.game.actions.prototypes.ActionBattlePvE1x1Prototype.process_artifact_breaking') as process_artifact_breaking:
                    action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)
                    self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(add_experience.call_args_list, [mock.call(c.EXP_FOR_KILL)])
        self.assertEqual(process_artifact_breaking.call_count, 1)

        self.assertEqual(action_battle.percents, 1.0)
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
