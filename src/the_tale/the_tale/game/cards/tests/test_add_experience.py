
import smart_imports

smart_imports.all()


class AddExperienceTestMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddExperienceTestMixin, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    @mock.patch('the_tale.game.heroes.objects.Hero.is_first_quest_path_required', False)
    def test_use(self):
        self.action_quest = actions_prototypes.ActionQuestPrototype.create(hero=self.hero)
        quests_helpers.setup_quest(self.hero)

        self.assertTrue(self.hero.quests.has_quests)

        old_ui_experience = self.hero.quests.current_quest.current_info.ui_info(self.hero)['experience']

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            with self.check_not_changed(lambda: self.hero.experience):
                with self.check_not_changed(lambda: self.hero.level):
                    with self.check_not_changed(lambda: self.hero.quests.current_quest.current_info.experience):
                        with self.check_delta(lambda: self.hero.quests.current_quest.current_info.experience_bonus, self.CARD.effect.modificator):
                            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
                            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(mark_updated.call_count, 1)

        while self.hero.quests.has_quests:
            self.assertEqual(self.hero.quests.current_quest.quests_stack[0].experience_bonus, self.CARD.effect.modificator)
            self.assertEqual(self.hero.quests.current_quest.quests_stack[0].ui_info(self.hero)['experience'], old_ui_experience + self.CARD.effect.modificator)
            self.storage.process_turn()

    def test_no_quest(self):
        self.assertFalse(self.hero.quests.has_quests)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))


class AddExperienceCommonTests(AddExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_EXPERIENCE_COMMON


class AddExperienceUncommonTests(AddExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_EXPERIENCE_UNCOMMON


class AddExperienceRareTests(AddExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_EXPERIENCE_RARE


class AddExperienceEpicTests(AddExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_EXPERIENCE_EPIC


class AddExperienceLegendaryTests(AddExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_EXPERIENCE_LEGENDARY
