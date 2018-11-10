
import smart_imports

smart_imports.all()


class RestActionTest(abilities_helpers.UseAbilityTaskMixin, utils_testcase.TestCase):
    PROCESSOR = abilities_deck.help.Help

    def setUp(self):
        super(RestActionTest, self).setUp()

        game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]
        self.action_idl = self.hero.actions.current_action

        self.action_rest = prototypes.ActionRestPrototype.create(hero=self.hero)

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_rest.leader, True)
        self.assertEqual(self.action_rest.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_processed(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()

    def test_not_ready(self):
        self.hero.health = 1
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_rest)
        self.assertTrue(self.hero.health > 1)
        self.storage._test_save()

    def test_ability_heal(self):

        self.hero.health = 1

        old_percents = self.action_rest.percents

        ability = self.PROCESSOR()

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: abilities_relations.HELP_CHOICES.HEAL):
            self.assertTrue(ability.use(**self.use_attributes(hero=self.hero, storage=self.storage)))

        self.assertTrue(self.hero.health > 1)
        self.assertTrue(old_percents < self.action_rest.percents)
        self.assertEqual(self.hero.actions.current_action.percents, self.action_rest.percents)

    def test_ability_heal__healed(self):

        self.hero.health = self.hero.max_health - 1

        ability = self.PROCESSOR()

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: abilities_relations.HELP_CHOICES.HEAL):
            self.assertTrue(ability.use(**self.use_attributes(hero=self.hero, storage=self.storage)))

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertTrue(self.action_rest.percents, 1)
        self.assertEqual(self.action_rest.state, self.action_rest.STATE.PROCESSED)

    def test_full(self):
        self.hero.health = 1

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            game_turn.increment()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.storage._test_save()
