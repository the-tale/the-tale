# coding: utf-8


from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map
from the_tale.game.actions.prototypes import ActionFirstStepsPrototype
from the_tale.game.balance import constants as c
from the_tale.game.prototypes import TimePrototype


class FirstStepsActionTest(testcase.TestCase):

    def setUp(self):
        super(FirstStepsActionTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.action_idl = self.hero.actions.current_action

        with self.check_calls_count('the_tale.game.heroes.logic.push_message_to_diary', 1):
            self.action_first_steps = ActionFirstStepsPrototype.create(hero=self.hero)


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_first_steps.leader, True)
        self.assertEqual(self.action_first_steps.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()


    def test_processed(self):
        current_time = TimePrototype.get_current_time()

        self.assertEqual(self.hero.journal.messages_number(), 2)

        with self.check_calls_count('the_tale.game.heroes.logic.push_message_to_diary', 0):
            self.storage.process_turn()

            current_time.increment_turn()

            self.assertEqual(self.hero.journal.messages_number(), 3)

            self.storage.process_turn()
            current_time.increment_turn()

            self.assertEqual(self.hero.journal.messages_number(), 4)

            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

            self.assertEqual(self.hero.journal.messages_number(), 5)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_IDLENESS)

        self.storage._test_save()
