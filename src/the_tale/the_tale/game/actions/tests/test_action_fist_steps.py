
import smart_imports

smart_imports.all()


class FirstStepsActionTest(utils_testcase.TestCase):

    def setUp(self):
        super(FirstStepsActionTest, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.action_idl = self.hero.actions.current_action

        with self.check_calls_count('the_tale.game.heroes.tt_services.diary.cmd_push_message', 1):
            self.action_first_steps = prototypes.ActionFirstStepsPrototype.create(hero=self.hero)

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_first_steps.leader, True)
        self.assertEqual(self.action_first_steps.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_processed(self):

        self.assertEqual(self.hero.journal.messages_number(), 2)

        with self.check_calls_count('the_tale.game.heroes.tt_services.diary.cmd_push_message', 0):
            self.storage.process_turn()

            game_turn.increment()

            self.assertEqual(self.hero.journal.messages_number(), 3)

            self.storage.process_turn()

            game_turn.increment()

            self.assertEqual(self.hero.journal.messages_number(), 4)

            self.storage.process_turn(continue_steps_if_needed=False)

            game_turn.increment()

            self.assertEqual(self.hero.journal.messages_number(), 5)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_IDLENESS)

        self.storage._test_save()
