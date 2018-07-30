
import smart_imports

smart_imports.all()


def companion_total_experience(companion):
    n = companion.coherence - 1

    if n == 0:
        return companion.experience

    return companion.experience + n * (n - 1) / 2


class AddCompanionExperienceTestMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddCompanionExperienceTestMixin, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertFalse(self.hero.companion.is_dead)

        with self.check_increased(lambda: companion_total_experience(self.hero.companion)):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    def test_use__coherence_restriction_does_not_work(self):
        companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        # test that coherence restriction does not work
        self.hero.companion.experience = self.hero.companion.experience_to_next_level

        self.assertFalse(self.hero.companion.is_dead)

        with self.check_increased(lambda: self.hero.companion.coherence):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    def test_use__companion_is_dead(self):
        companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.hero.companion.health = 0

        self.assertTrue(self.hero.companion.is_dead)

        with self.check_increased(lambda: companion_total_experience(self.hero.companion)):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    def test_no_companion(self):
        self.assertEqual(self.hero.companion, None)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))


class AddExperienceCommonTests(AddCompanionExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_COMPANION_EXPERIENCE_COMMON


class AddExperienceUncommonTests(AddCompanionExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_COMPANION_EXPERIENCE_UNCOMMON


class AddExperienceRareTests(AddCompanionExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_COMPANION_EXPERIENCE_RARE


class AddExperienceEpicTests(AddCompanionExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_COMPANION_EXPERIENCE_EPIC


class AddExperienceLegendaryTests(AddCompanionExperienceTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_COMPANION_EXPERIENCE_LEGENDARY
