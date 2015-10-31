# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.actions.prototypes import ACTION_TYPES

from the_tale.game.actions.tests.helpers import TestAction
from the_tale.game.actions.container import ActionsContainer



class ActionsContainerTests(testcase.TestCase):

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        super(ActionsContainerTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.bundle_id = bundle_id

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        self.container = self.hero.actions

        self.action_1 = self.container.current_action
        self.action_2 = TestAction.create(hero=self.hero, data=2)
        self.action_3 = TestAction.create(hero=self.hero, data=3)

    def test_create(self):
        container = ActionsContainer()
        self.assertFalse(container.updated)
        self.assertEqual(container.actions_list, [])
        self.assertFalse(container.is_single)

    @mock.patch('the_tale.game.actions.prototypes.ACTION_TYPES', dict(ACTION_TYPES, **{TestAction.TYPE: TestAction}))
    def test_serialization(self):
        self.assertEqual(self.container.serialize(), ActionsContainer.deserialize(data=self.container.serialize()).serialize())

        container = ActionsContainer.deserialize(data=self.container.serialize())
        container.initialize(self.hero)
        for action in container.actions_list:
            self.assertEqual(id(action.hero), id(self.hero))

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
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


    def test_is_single__push_and_pop_action(self):
        while self.container.number > 1:
            self.container.pop_action()

        self.assertTrue(self.container.is_single)

        TestAction.create(hero=self.hero, data=4, single=False)
        self.assertFalse(self.container.is_single)

        TestAction.create(hero=self.hero, data=4, single=True)
        self.assertFalse(self.container.is_single)

        self.container.pop_action()
        self.assertFalse(self.container.is_single)

        self.container.pop_action()
        self.assertTrue(self.container.is_single)


    def test_is_single__deserialize(self):
        while self.container.number > 1:
            self.container.pop_action()

        self.assertTrue(self.container.is_single)

        with mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.SINGLE', False):
            with mock.patch('the_tale.game.actions.prototypes.ACTION_TYPES', dict(ACTION_TYPES, **{TestAction.TYPE: TestAction})):
                self.assertFalse(ActionsContainer.deserialize(self.container.serialize()).is_single)
