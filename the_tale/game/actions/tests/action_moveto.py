# coding: utf-8
import mock

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map
from game.actions.prototypes import ActionMoveToPrototype, ActionInPlacePrototype, ActionRestPrototype, ActionResurrectPrototype, ActionBattlePvE1x1Prototype


class MoveToActionTest(TestCase):

    def setUp(self):
        p1, p2, p3 = create_test_map()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

        self.bundle = create_test_bundle('MoveToActionTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.position.set_place(self.p1)

        self.action_idl = self.bundle.tests_get_last_action()
        self.bundle.add_action(ActionMoveToPrototype.create(self.action_idl, self.p3))
        self.action_move = self.bundle.tests_get_last_action()


    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_move.leader, True)


    def test_processed(self):
        self.hero.position.set_place(self.p3)
        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 1)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_idl)


    def test_not_ready(self):
        self.bundle.process_turn(1)
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_move)
        self.assertTrue(self.hero.position.road)


    def test_full_move(self):

        while self.hero.position.place is None or self.hero.position.place.id != self.p3.id:
            self.bundle.process_turn(1)

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionInPlacePrototype.TYPE)


    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 0)
    def test_short_teleport(self):
        self.bundle.process_turn(1)

        old_road_percents = self.hero.position.percents
        self.action_move.short_teleport(1)
        self.assertTrue(old_road_percents < self.hero.position.percents)

        self.action_move.short_teleport(self.hero.position.road.length)
        self.assertEqual(self.hero.position.percents, 1)
        self.bundle.process_turn(1)

        self.assertEqual(self.hero.position.place.id, self.p2.id)


    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 1.0)
    def test_battle(self):
        self.bundle.process_turn(1)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionBattlePvE1x1Prototype.TYPE)


    def test_rest(self):
        self.hero.health = 1
        self.action_move.state = self.action_move.STATE.BATTLE
        self.bundle.process_turn(1)

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionRestPrototype.TYPE)


    def test_resurrect(self):
        self.hero.kill()
        self.action_move.state = self.action_move.STATE.BATTLE
        self.bundle.process_turn(1)

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionResurrectPrototype.TYPE)


    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 0)
    def test_inplace(self):
        self.bundle.process_turn(1)
        self.hero.position.percents = 1
        self.bundle.process_turn(1)

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionInPlacePrototype.TYPE)


class MoveToActionWithBreaksTest(TestCase):

    def setUp(self):
        p1, p2, p3 = create_test_map()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

        self.bundle = create_test_bundle('MoveToActionTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.position.set_place(self.p1)

        self.action_idl = self.bundle.tests_get_last_action()
        self.bundle.add_action(ActionMoveToPrototype.create(self.action_idl, self.p3, 0.75))
        self.action_move = self.bundle.tests_get_last_action()


    def test_sequence_move(self):

        while self.bundle.tests_get_last_action() != self.action_idl:
            self.bundle.process_turn(1)
        self.assertEqual(self.hero.position.road.point_1_id, self.p2.id)
        self.assertEqual(self.hero.position.road.point_2_id, self.p3.id)

        self.bundle.add_action(ActionMoveToPrototype.create(self.action_idl, self.p1, 0.9))
        while self.bundle.tests_get_last_action() != self.action_idl:
            self.bundle.process_turn(1)
        self.assertEqual(self.hero.position.road.point_1_id, self.p1.id)
        self.assertEqual(self.hero.position.road.point_2_id, self.p2.id)

        self.bundle.add_action(ActionMoveToPrototype.create(self.action_idl, self.p2))
        while self.hero.position.place is None or self.hero.position.place.id != self.p2.id:
            self.bundle.process_turn(1)
        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionInPlacePrototype.TYPE)
