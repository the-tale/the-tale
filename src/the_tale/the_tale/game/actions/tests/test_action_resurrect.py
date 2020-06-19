
import smart_imports

smart_imports.all()


class ResurrectActionTest(utils_testcase.TestCase):

    def setUp(self):
        super(ResurrectActionTest, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.action_idl = self.hero.actions.current_action

        self.hero.kill()

        self.action_resurrect = prototypes.ActionResurrectPrototype.create(hero=self.hero)

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_resurrect.leader, True)
        self.assertEqual(self.action_resurrect.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_processed(self):

        for i in range(c.TURNS_TO_RESURRECT - 1):

            self.storage.process_turn()

            game_turn.increment()

            self.assertEqual(len(self.hero.actions.actions_list), 2)
            self.assertEqual(self.hero.actions.current_action, self.action_resurrect)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)

        self.storage._test_save()

    def test_one_step(self):

        with self.check_increased(lambda: self.action_resurrect.percents):
            with self.check_not_changed(lambda: self.hero.is_alive):
                self.storage.process_turn(continue_steps_if_needed=False)

        self.storage._test_save()

    def test_one_step__already_alive(self):

        self.hero.resurrect()

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_resurrect.percents, 1.0)
        self.assertEqual(self.action_resurrect.state, self.action_resurrect.STATE.PROCESSED)
        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)

        self.storage._test_save()

    def test_full(self):

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

            game_turn.increment()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.assertEqual(self.hero.is_alive, True)

        self.storage._test_save()
