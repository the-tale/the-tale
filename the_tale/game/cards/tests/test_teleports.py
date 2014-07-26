# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin
from the_tale.game.actions.prototypes import ActionMoveToPrototype

class ShortTeleportTests(CardsTestMixin, testcase.TestCase):
    CARD = prototypes.ShortTeleport

    def setUp(self):
        super(ShortTeleportTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero.position.set_place(self.place_1)

        self.card = self.CARD()

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_moving(self):
        self.assertFalse(self.hero.actions.current_action.TYPE.is_MOVE_TO)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_use(self):
        ActionMoveToPrototype.create(hero=self.hero, destination=self.place_3)

        self.storage.process_turn(second_step_if_needed=False)

        self.assertTrue(self.hero.actions.current_action.state == ActionMoveToPrototype.STATE.MOVING)

        self.assertTrue(self.hero.position.percents < 1)

        with self.check_increased(lambda: self.hero.actions.current_action.percents):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.position.place.id, self.place_2.id)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.storage.process_turn(second_step_if_needed=False)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.position.place.id, self.place_3.id)
        self.assertEqual(self.hero.actions.current_action.percents, 1)

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_use__wrong_state(self):
        ActionMoveToPrototype.create(hero=self.hero, destination=self.place_3)
        self.assertTrue(self.hero.actions.current_action.state != ActionMoveToPrototype.STATE.MOVING)

        with self.check_not_changed(lambda: self.hero.actions.current_action.percents):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertTrue(self.hero.position.place.id, self.place_1.id)


class LongTeleportTests(CardsTestMixin, testcase.TestCase):
    CARD = prototypes.LongTeleport

    def setUp(self):
        super(LongTeleportTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero.position.set_place(self.place_1)

        self.card = self.CARD()

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_moving(self):
        self.assertFalse(self.hero.actions.current_action.TYPE.is_MOVE_TO)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_use(self):
        ActionMoveToPrototype.create(hero=self.hero, destination=self.place_3)

        self.storage.process_turn(second_step_if_needed=False)

        self.assertTrue(self.hero.actions.current_action.state == ActionMoveToPrototype.STATE.MOVING)

        self.assertTrue(self.hero.position.percents < 1)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.position.place.id, self.place_3.id)
        self.assertEqual(self.hero.actions.current_action.percents, 1)

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_use__wrong_state(self):
        ActionMoveToPrototype.create(hero=self.hero, destination=self.place_3)
        self.assertTrue(self.hero.actions.current_action.state != ActionMoveToPrototype.STATE.MOVING)

        with self.check_not_changed(lambda: self.hero.actions.current_action.percents):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertTrue(self.hero.position.place.id, self.place_1.id)
