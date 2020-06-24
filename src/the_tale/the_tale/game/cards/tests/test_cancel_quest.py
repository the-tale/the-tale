
import smart_imports

smart_imports.all()


class CancelQuestTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.CANCEL_QUEST

    def setUp(self):
        super(CancelQuestTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_no_quests(self):
        self.assertFalse(self.hero.quests.has_quests)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertFalse(self.hero.quests.has_quests)

    def test_use(self):
        self.hero.quests.push_quest('QUEST')
        self.assertTrue(self.hero.quests.has_quests)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual(mark_updated.call_count, 2)

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertFalse(self.hero.quests.has_quests)
