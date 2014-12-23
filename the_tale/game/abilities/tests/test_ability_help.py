# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.prototypes import TimePrototype
from the_tale.game.actions import prototypes as actions_prototypes

from the_tale.game.heroes.relations import HABIT_CHANGE_SOURCE

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts import relations as artifacts_relations

from the_tale.game.abilities.deck.help import Help
from the_tale.game.abilities.relations import HELP_CHOICES

from the_tale.game.pvp.prototypes import Battle1x1Prototype
from the_tale.game.pvp.models import BATTLE_1X1_STATE

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.abilities.tests.helpers import UseAbilityTaskMixin


class HelpAbilityTest(UseAbilityTaskMixin, testcase.TestCase):
    ABILITY = Help

    def setUp(self):
        super(HelpAbilityTest, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()


        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.action_idl = self.hero.actions.current_action

        self.ability = self.ABILITY()

    @property
    def use_attributes(self):
        return super(HelpAbilityTest, self).use_attributes(hero=self.hero, storage=self.storage)

    def test_none(self):
        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: None):
            with self.check_not_changed(lambda: self.hero.statistics.help_count):
                with self.check_not_changed(lambda: self.hero.cards.help_count):
                    self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

    def test_success(self):
        with self.check_delta(lambda: self.hero.statistics.help_count, 1):
            with self.check_delta(lambda: self.hero.cards.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_help_when_battle_waiting(self):
        battle = Battle1x1Prototype.create(self.account)
        self.assertTrue(battle.state.is_WAITING)
        with self.check_delta(lambda: self.hero.statistics.help_count, 1):
            self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_help_when_battle_not_waiting(self):
        battle = Battle1x1Prototype.create(self.account)
        battle.state = BATTLE_1X1_STATE.PREPAIRING
        battle.save()

        self.assertFalse(battle.state.is_WAITING)
        with self.check_not_changed(lambda: self.hero.statistics.help_count):
            self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

    def test_heal(self):
        self.hero.health = 1
        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.HEAL):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))
                self.assertTrue(self.hero.health > 1)

    def test_start_quest(self):
        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.START_QUEST):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))
                self.assertTrue(self.action_idl.percents >= 1)

    def test_experience(self):
        old_experience = self.hero.experience
        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.EXPERIENCE):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(old_experience < self.hero.experience)

    def test_stock_up_energy(self):

        with self.check_changed(lambda: self.hero.energy_bonus):
            with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.STOCK_UP_ENERGY):
                with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                    self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_money(self):
        old_hero_money = self.hero.money
        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.MONEY):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))
                self.assertTrue(self.hero.money > old_hero_money)

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_teleport(self):
        move_place = self.p3
        if move_place.id == self.hero.position.place.id:
            move_place = self.p1

        current_time = TimePrototype.get_current_time()

        action_move = actions_prototypes.ActionMoveToPrototype.create(hero=self.hero, destination=move_place)

        current_time.increment_turn()
        self.storage.process_turn()

        old_road_percents = self.hero.position.percents
        old_percents = action_move.percents

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.TELEPORT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(old_road_percents < self.hero.position.percents)
        self.assertTrue(old_percents < action_move.percents)
        self.assertEqual(self.hero.actions.current_action.percents, action_move.percents)

    @mock.patch('the_tale.game.balance.constants.ANGEL_HELP_CRIT_TELEPORT_DISTANCE', 9999999999)
    @mock.patch('the_tale.game.balance.constants.ANGEL_HELP_TELEPORT_DISTANCE', 9999999999)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_teleport__inplace_action_created(self):
        move_place = self.p3
        if move_place.id == self.hero.position.place.id:
            move_place = self.p1

        current_time = TimePrototype.get_current_time()

        actions_prototypes.ActionMoveToPrototype.create(hero=self.hero, destination=move_place)

        current_time.increment_turn()
        self.storage.process_turn()

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.TELEPORT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.actions.current_action.TYPE, actions_prototypes.ActionInPlacePrototype.TYPE)


    def test_lighting(self):
        current_time = TimePrototype.get_current_time()
        action_battle = actions_prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.create_mob_for_hero(self.hero))

        current_time.increment_turn()
        self.storage.process_turn()

        old_mob_health = action_battle.mob.health
        old_percents = action_battle.percents

        self.assertTrue(HELP_CHOICES.LIGHTING in action_battle.help_choices)

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.LIGHTING):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(old_mob_health > action_battle.mob.health)
        self.assertEqual(self.hero.actions.current_action.percents, action_battle.percents)
        self.assertTrue(old_percents < action_battle.percents)

    def test_lighting_when_mob_killed(self):
        current_time = TimePrototype.get_current_time()
        action_battle = actions_prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.create_mob_for_hero(self.hero))

        current_time.increment_turn()
        self.storage.process_turn()

        action_battle.mob.health = 0

        self.assertFalse(HELP_CHOICES.LIGHTING in action_battle.help_choices)

    def test_resurrect(self):
        current_time = TimePrototype.get_current_time()

        self.hero.kill()
        action_resurrect = actions_prototypes.ActionResurrectPrototype.create(hero=self.hero)

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.RESURRECT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                current_time.increment_turn()
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)
        self.assertEqual(action_resurrect.state, action_resurrect.STATE.PROCESSED)


    def test_process_turn_called_if_current_action_processed(self):
        current_time = TimePrototype.get_current_time()

        self.hero.kill()
        actions_prototypes.ActionResurrectPrototype.create(hero=self.hero)

        with mock.patch('the_tale.game.logic_storage.LogicStorage.process_turn__single_hero') as process_turn__single_hero:
            with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.RESURRECT):
                with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                    current_time.increment_turn()
                    self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(process_turn__single_hero.call_args_list, [mock.call(hero=self.hero,
                                                                              logger=None,
                                                                              continue_steps_if_needed=True)])


    def test_resurrect__two_times(self):
        current_time = TimePrototype.get_current_time()

        self.hero.kill()
        actions_prototypes.ActionResurrectPrototype.create(hero=self.hero)

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.RESURRECT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                current_time.increment_turn()
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.RESURRECT):
            with self.check_not_changed(lambda: self.hero.statistics.help_count):
                current_time.increment_turn()
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.IGNORE, ComplexChangeTask.STEP.SUCCESS, ()))

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.AGGRESSIVE', False)
    def test_update_habits__aggressive_action(self):

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.update_habits') as update_habits:
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(update_habits.call_args_list, [mock.call(HABIT_CHANGE_SOURCE.HELP_UNAGGRESSIVE)])

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.AGGRESSIVE', True)
    def test_update_habits__unaggressive_action(self):
        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.update_habits') as update_habits:
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(update_habits.call_args_list, [mock.call(HABIT_CHANGE_SOURCE.HELP_AGGRESSIVE)])


    @mock.patch('the_tale.game.artifacts.effects.Health.REMOVE_ON_HELP', True)
    def test_return_child_gifts(self):
        not_child_gift, child_gift, removed_artifact = artifacts_storage.all()[:3]

        child_gift.special_effect = artifacts_relations.ARTIFACT_EFFECT.CHILD_GIFT
        removed_artifact.rare_effect = artifacts_relations.ARTIFACT_EFFECT.HEALTH

        self.hero.bag.put_artifact(not_child_gift.create_artifact(level=1, power=0))
        self.hero.bag.put_artifact(not_child_gift.create_artifact(level=1, power=0))
        self.hero.bag.put_artifact(not_child_gift.create_artifact(level=1, power=0))

        self.hero.bag.put_artifact(child_gift.create_artifact(level=1, power=0))
        self.hero.bag.put_artifact(child_gift.create_artifact(level=1, power=0))

        self.hero.bag.put_artifact(removed_artifact.create_artifact(level=1, power=0))
        self.hero.bag.put_artifact(removed_artifact.create_artifact(level=1, power=0, rarity=artifacts_relations.RARITY.RARE))

        with self.check_delta(lambda: self.hero.statistics.gifts_returned, 2):
            with self.check_delta(lambda: self.hero.bag.occupation, -3):
                self.ability.use(**self.use_attributes)
