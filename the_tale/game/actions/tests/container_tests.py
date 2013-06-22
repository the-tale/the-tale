# coding: utf-8
import mock

from common.utils import testcase

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.balance import constants as c
from game.logic import create_test_map
from game.prototypes import TimePrototype

from game.heroes.logic import create_mob_for_hero

from game.actions.prototypes import ACTION_TYPES, ActionBattlePvE1x1Prototype, ActionBase
from game.actions import contexts

from game.actions.tests.helpers import TestAction
from game.actions.container import ActionsContainer
from game.actions.prototypes import ACTION_TYPES


class ActionsContainerTests(testcase.TestCase):

    @mock.patch('game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        super(ActionsContainerTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.bundle_id = bundle_id
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.container = self.hero.actions

        self.action_1 = self.container.current_action
        self.action_2 = TestAction.create(hero=self.hero, data=2)
        self.action_3 = TestAction.create(hero=self.hero, data=3)

    def test_create(self):
        container = ActionsContainer()
        self.assertFalse(container.updated)
        self.assertEqual(container.actions_list, [])

    @mock.patch('game.actions.prototypes.ACTION_TYPES', dict(ACTION_TYPES, **{TestAction.TYPE: TestAction}))
    def test_serialization(self):
        self.assertEqual(self.container.serialize(), ActionsContainer.deserialize(self.hero, data=self.container.serialize()).serialize())

        container = ActionsContainer.deserialize(self.hero, data=self.container.serialize())
        for action in container.actions_list:
            self.assertEqual(id(action.hero), id(self.hero))

    @mock.patch('game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def test_push_action(self):
        self.assertEqual([a.data for a in self.container.actions_list], [None, 2, 3])

        self.container.updated = False

        TestAction.create(hero=self.hero, data=4)

        self.assertTrue(self.container.updated)

        self.assertEqual([a.data for a in self.container.actions_list], [None, 2, 3, 4])

    def test_pop_action(self):
        self.assertEqual([a.data for a in self.container.actions_list], [None, 2, 3])
        self.container.updated = False

        action = self.container.pop_action()

        self.assertEqual(action.data, 3)
        self.assertTrue(self.container.updated)
        self.assertEqual([a.data for a in self.container.actions_list], [None, 2])

    def test_current_action(self):
        self.assertEqual(self.container.current_action.percents, self.action_3.percents)
