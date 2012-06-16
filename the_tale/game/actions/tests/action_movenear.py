# coding: utf-8
import mock

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionMoveNearPlacePrototype, ActionRestPrototype, ActionResurrectPrototype, ActionIdlenessPrototype, ActionBattlePvE1x1Prototype
from game.prototypes import TimePrototype

class MoveNearActionTest(TestCase):

    def setUp(self):
        p1, p2, p3 = create_test_map()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

        self.bundle = create_test_bundle('MoveToActionTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.position.set_place(self.p1)

        self.action_idl = self.bundle.tests_get_last_action()
        self.bundle.add_action(ActionMoveNearPlacePrototype.create(self.action_idl, TimePrototype.get_current_time(), self.p1, False))
        self.action_move = self.bundle.tests_get_last_action()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_move.leader, True)
        test_bundle_save(self, self.bundle)


    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 0)
    def test_processed(self):

        current_time = TimePrototype.get_current_time()

        self.bundle.process_turn(current_time)

        x, y = self.action_move.get_destination()
        self.hero.position.set_coordinates(x, y, x, y, percents=1)

        current_time.increment_turn()
        self.bundle.process_turn(current_time)

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionIdlenessPrototype.TYPE)
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place) # can end in start place

        test_bundle_save(self, self.bundle)


    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 0)
    def test_not_ready(self):
        self.bundle.process_turn(TimePrototype.get_current_time())
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_move)
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place) # can end in start place
        test_bundle_save(self, self.bundle)

    def test_full_move_and_back(self):

        current_time = TimePrototype.get_current_time()

        while len(self.bundle.actions) != 1:
            self.bundle.process_turn(current_time)
            current_time.increment_turn()

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionIdlenessPrototype.TYPE)
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place)  # can end in start place

        self.bundle.add_action(ActionMoveNearPlacePrototype.create(self.action_idl, TimePrototype.get_current_time(), self.p1, True))
        while self.hero.position.place is None or self.hero.position.place.id != self.p1.id:
            self.bundle.process_turn(current_time)
            current_time.increment_turn()

        self.assertTrue(not self.hero.position.is_walking)
        test_bundle_save(self, self.bundle)


    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 1.0)
    def test_battle(self):
        self.bundle.process_turn(TimePrototype.get_current_time())
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionBattlePvE1x1Prototype.TYPE)
        test_bundle_save(self, self.bundle)


    def test_rest(self):
        self.hero.health = 1
        self.action_move.state = self.action_move.STATE.BATTLE
        self.bundle.process_turn(TimePrototype.get_current_time())

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionRestPrototype.TYPE)
        test_bundle_save(self, self.bundle)


    def test_resurrect(self):
        self.hero.kill()
        self.action_move.state = self.action_move.STATE.BATTLE
        self.bundle.process_turn(TimePrototype.get_current_time())

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionResurrectPrototype.TYPE)
        test_bundle_save(self, self.bundle)
