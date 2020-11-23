
import smart_imports

smart_imports.all()


class StopIdlenessTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.STOP_IDLENESS

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.assertTrue(self.hero.actions.current_action.TYPE.is_IDLENESS)

    def test_idleness__success(self):

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                          game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                          ()))

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)
        self.assertTrue(self.hero.quests.has_quests)

    def test_idleness__dead_hero(self):

        self.hero.kill()

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED,
                          game_postponed_tasks.ComplexChangeTask.STEP.ERROR,
                          ()))

        self.assertTrue(self.hero.actions.current_action.TYPE.is_IDLENESS)
        self.assertFalse(self.hero.quests.has_quests)

    def test_idleness__not_in_place(self):
        self.hero.position.set_position(0.5, 0.5)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED,
                          game_postponed_tasks.ComplexChangeTask.STEP.ERROR,
                          ()))

        self.assertTrue(self.hero.actions.current_action.TYPE.is_IDLENESS)
        self.assertFalse(self.hero.quests.has_quests)

    def test_idleness__has_subaction(self):
        actions_prototypes.ActionReligionCeremonyPrototype.create(hero=self.hero)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED,
                          game_postponed_tasks.ComplexChangeTask.STEP.ERROR,
                          ()))

        self.assertTrue(self.hero.actions.current_action.TYPE.is_RELIGION_CEREMONY)
        self.assertFalse(self.hero.quests.has_quests)
