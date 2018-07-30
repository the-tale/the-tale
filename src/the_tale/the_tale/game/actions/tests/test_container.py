
import smart_imports

smart_imports.all()


class ActionsContainerTests(utils_testcase.TestCase):

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        super(ActionsContainerTests, self).setUp()

        game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

        self.container = self.hero.actions

        self.action_1 = self.container.current_action
        self.action_2 = helpers.TestAction.create(hero=self.hero, data=2)
        self.action_3 = helpers.TestAction.create(hero=self.hero, data=3)

    def test_create(self):
        test_container = container.ActionsContainer()
        self.assertEqual(test_container.actions_list, [])
        self.assertFalse(test_container.is_single)

    @mock.patch('the_tale.game.actions.prototypes.ACTION_TYPES', {**prototypes.ACTION_TYPES,
                                                                  **{helpers.TestAction.TYPE: helpers.TestAction}})
    def test_serialization(self):
        self.assertEqual(self.container.serialize(), container.ActionsContainer.deserialize(data=self.container.serialize()).serialize())

        test_container = container.ActionsContainer.deserialize(data=self.container.serialize())
        test_container.initialize(self.hero)
        for action in test_container.actions_list:
            self.assertEqual(id(action.hero), id(self.hero))

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def test_push_action(self):
        self.assertEqual([a.data for a in self.container.actions_list], [None, 2, 3])

        helpers.TestAction.create(hero=self.hero, data=4)

        self.assertEqual([a.data for a in self.container.actions_list], [None, 2, 3, 4])

    def test_pop_action(self):
        self.assertEqual([a.data for a in self.container.actions_list], [None, 2, 3])

        action = self.container.pop_action()

        self.assertEqual(action.data, 3)
        self.assertEqual([a.data for a in self.container.actions_list], [None, 2])

    def test_current_action(self):
        self.assertEqual(self.container.current_action.percents, self.action_3.percents)

    def test_is_single__push_and_pop_action(self):
        while self.container.number > 1:
            self.container.pop_action()

        self.assertTrue(self.container.is_single)

        helpers.TestAction.create(hero=self.hero, data=4, single=False)
        self.assertFalse(self.container.is_single)

        helpers.TestAction.create(hero=self.hero, data=4, single=True)
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
            with mock.patch('the_tale.game.actions.prototypes.ACTION_TYPES', {**prototypes.ACTION_TYPES,
                                                                              **{helpers.TestAction.TYPE: helpers.TestAction}}):
                self.assertFalse(container.ActionsContainer.deserialize(self.container.serialize()).is_single)
