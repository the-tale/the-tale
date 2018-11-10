
import smart_imports

smart_imports.all()


class RegenerateEnergyActionTest(utils_testcase.TestCase):

    def setUp(self):
        super(RegenerateEnergyActionTest, self).setUp()
        game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]
        self.action_idl = self.hero.actions.current_action

        self.action_regenerate = prototypes.ActionRegenerateEnergyPrototype.create(hero=self.hero)

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_regenerate.leader, True)
        self.assertEqual(self.action_regenerate.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_not_ready(self):
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_regenerate)
        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_double_energy', False)
    def test_full(self):

        with self.check_delta(lambda: game_tt_services.energy.cmd_balance(self.hero.account_id),
                              self.hero.preferences.energy_regeneration_type.amount):

            while len(self.hero.actions.actions_list) != 1:
                self.storage.process_turn(continue_steps_if_needed=False)
                game_turn.increment()

            time.sleep(0.1)

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, game_turn.number() - 1)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_double_energy', False)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_energy', False)
    def test_full__regeneration_restricted(self):

        with self.check_not_changed(lambda: game_tt_services.energy.cmd_balance(self.hero.account_id)):

            while len(self.hero.actions.actions_list) != 1:
                self.storage.process_turn(continue_steps_if_needed=False)
                game_turn.increment()

            time.sleep(0.1)

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, game_turn.number() - 1)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_double_energy', True)
    def test_full__double_energy(self):
        with self.check_delta(lambda: game_tt_services.energy.cmd_balance(self.hero.account_id),
                              self.hero.preferences.energy_regeneration_type.amount * 2):

            while len(self.hero.actions.actions_list) != 1:
                self.storage.process_turn(continue_steps_if_needed=False)
                game_turn.increment()

            time.sleep(0.1)

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, game_turn.number() - 1)

        self.storage._test_save()
