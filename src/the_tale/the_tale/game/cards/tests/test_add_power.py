
import smart_imports

smart_imports.all()


class AddPoliticPowerTestMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddPoliticPowerTestMixin, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        self.action_quest = actions_prototypes.ActionQuestPrototype.create(hero=self.hero)
        quests_helpers.setup_quest(self.hero)

        self.assertTrue(self.hero.quests.has_quests)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            with self.check_not_changed(lambda: self.hero.power):
                with self.check_not_changed(lambda: self.hero.level):
                    with self.check_not_changed(lambda: self.hero.quests.current_quest.current_info.power):
                        with self.check_delta(lambda: self.hero.quests.current_quest.current_info.power_bonus, self.CARD.effect.modificator):
                            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
                            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(mark_updated.call_count, 1)

    def test_second_use(self):
        self.action_quest = actions_prototypes.ActionQuestPrototype.create(hero=self.hero)
        quests_helpers.setup_quest(self.hero)

        self.assertTrue(self.hero.quests.has_quests)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            with self.check_not_changed(lambda: self.hero.power):
                with self.check_not_changed(lambda: self.hero.level):
                    with self.check_not_changed(lambda: self.hero.quests.current_quest.current_info.power):
                        with self.check_delta(lambda: self.hero.quests.current_quest.current_info.power_bonus,
                                              self.CARD.effect.modificator):
                            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage,
                                                                                                        hero=self.hero))
                            self.assertEqual((result, step, postsave_actions),
                                             (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                                              game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                                             ()))

                        with self.check_not_changed(lambda: self.hero.quests.current_quest.current_info.power_bonus):
                            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage,
                                                                                                        hero=self.hero))
                            self.assertEqual((result, step, postsave_actions),
                                             (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED,
                                              game_postponed_tasks.ComplexChangeTask.STEP.ERROR,
                                             ()))

        self.assertEqual(mark_updated.call_count, 1)

    def test_no_quest(self):
        self.assertFalse(self.hero.quests.has_quests)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))


class AddPoliticPowerCommonTests(AddPoliticPowerTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_POWER_COMMON


class AddPoliticPowerUncommonTests(AddPoliticPowerTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_POWER_UNCOMMON


class AddPoliticPowerRareTests(AddPoliticPowerTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_POWER_RARE


class AddPoliticPowerEpicTests(AddPoliticPowerTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_POWER_EPIC


class AddPoliticPowerLegendaryTests(AddPoliticPowerTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_POWER_LEGENDARY
