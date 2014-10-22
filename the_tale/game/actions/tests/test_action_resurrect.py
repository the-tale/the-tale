# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map
from the_tale.game.actions.prototypes import ActionResurrectPrototype
from the_tale.game.balance import constants as c
from the_tale.game.prototypes import TimePrototype

class ResurrectActionTest(testcase.TestCase):

    def setUp(self):
        super(ResurrectActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.account = AccountPrototype.get_by_id(account_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.hero.kill()

        self.action_resurrect = ActionResurrectPrototype.create(hero=self.hero)

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_resurrect.leader, True)
        self.assertEqual(self.action_resurrect.bundle_id, self.action_idl.bundle_id)
        self.assertEqual(len(self.action_resurrect.HELP_CHOICES), 1)
        self.assertTrue(list(self.action_resurrect.HELP_CHOICES)[0].is_RESURRECT)
        self.storage._test_save()

    def test_processed(self):

        current_time = TimePrototype.get_current_time()

        for i in xrange(c.TURNS_TO_RESURRECT-1):

            self.storage.process_turn()
            current_time.increment_turn()
            self.assertEqual(len(self.hero.actions.actions_list), 2)
            self.assertEqual(self.hero.actions.current_action, self.action_resurrect)

        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)

        self.storage._test_save()

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(second_step_if_needed=False)
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.assertEqual(self.hero.is_alive, True)

        self.storage._test_save()

    def test_fast_resurrect(self):

        self.action_resurrect.fast_resurrect()

        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)

        self.storage._test_save()
