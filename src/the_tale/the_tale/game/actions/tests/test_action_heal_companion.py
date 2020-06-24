
import smart_imports

smart_imports.all()


class HealCompanionActionTest(utils_testcase.TestCase):

    def setUp(self):
        super(HealCompanionActionTest, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(self.companion_record))

        self.action_idl = self.hero.actions.current_action

        self.hero.companion.healed_at_turn = -1

        with self.check_increased(lambda: self.hero.companion.healed_at_turn):
            self.action_heal_companion = prototypes.ActionHealCompanionPrototype.create(hero=self.hero)

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_heal_companion.leader, True)
        self.assertEqual(self.action_heal_companion.bundle_id, self.action_heal_companion.bundle_id)
        self.assertEqual(self.action_heal_companion.percents, 0)
        self.storage._test_save()

    def test_processed__no_companion(self):
        self.hero.remove_companion()
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()

    def test_processed__max_health(self):
        self.assertEqual(self.hero.companion.health, self.hero.companion.max_health)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()

    def test_not_ready(self):
        self.hero.companion.health = 1

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_heal_companion)
        self.assertTrue(self.hero.companion.health, 1)
        self.assertTrue(self.action_heal_companion.percents > 0)
        self.storage._test_save()

    def test_full(self):
        self.hero.companion.health = 1

        with self.check_delta(lambda: self.hero.companion.health, c.COMPANIONS_HEALTH_PER_HEAL):
            while len(self.hero.actions.actions_list) != 1:
                self.storage.process_turn(continue_steps_if_needed=False)
                game_turn.increment()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_exp_per_heal', lambda hero: True)
    def test_full__exp_per_heal(self):
        self.hero.companion.health = 1

        with self.check_delta(lambda: self.hero.experience, c.COMPANIONS_EXP_PER_HEAL):

            while len(self.hero.actions.actions_list) != 1:
                self.storage.process_turn(continue_steps_if_needed=False)
                game_turn.increment()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()

    @mock.patch('the_tale.common.utils.logic.randint_from_1', lambda v: v)
    @mock.patch('the_tale.game.balance.constants.COMPANIONS_REGEN_ON_HEAL_PER_HEAL', 1.0)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_regenerate', lambda hero: True)
    def test_full__regeneration(self):
        self.hero.companion.health = 1

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            game_turn.increment()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.companion.health, 1 + c.COMPANIONS_HEALTH_PER_HEAL + c.COMPANIONS_REGEN_ON_HEAL_AMOUNT)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.companion_heal_probability', 1)
    @mock.patch('the_tale.common.utils.logic.randint_from_1', lambda v: v)
    def test_companion_healing_by_hero(self):

        self.hero.companion.health = 1

        with self.check_delta(lambda: self.hero.companion.health, c.COMPANIONS_HEALTH_PER_HEAL + c.COMPANIONS_REGEN_BY_HERO):
            self.action_heal_companion.state = self.action_heal_companion.STATE.PROCESSED
            self.storage.process_turn(continue_steps_if_needed=False)
            game_turn.increment()

    @mock.patch('the_tale.game.heroes.objects.Hero.companion_heal_probability', 0)
    @mock.patch('the_tale.common.utils.logic.randint_from_1', lambda v: v)
    def test_companion_healing_by_hero__not_healed(self):

        self.hero.companion.health = 1

        with self.check_delta(lambda: self.hero.companion.health, c.COMPANIONS_HEALTH_PER_HEAL):
            self.action_heal_companion.state = self.action_heal_companion.STATE.PROCESSED
            self.storage.process_turn(continue_steps_if_needed=False)
            game_turn.increment()
