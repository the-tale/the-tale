
import smart_imports

smart_imports.all()


class UpgradeArtifactTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.INCREMENT_ARTIFACT_RARITY

    def setUp(self):
        super(UpgradeArtifactTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.assertTrue(len(list(self.hero.equipment.values())) > 1)

    def test_use(self):

        for rarity in artifacts_relations.RARITY.records[:-1]:
            for artifact in list(self.hero.equipment.values()):
                artifact.rarity = rarity

            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

            self.assertEqual(len([artifact for artifact in list(self.hero.equipment.values()) if artifact.rarity == rarity]), len(list(self.hero.equipment.values())) - 1)
            self.assertEqual(len([artifact for artifact in list(self.hero.equipment.values()) if artifact.rarity == artifacts_relations.RARITY(rarity.value + 1)]), 1)

    def test_all_epic(self):
        rarity = artifacts_relations.RARITY.records[-1]

        for artifact in list(self.hero.equipment.values()):
            artifact.rarity = rarity

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(len([artifact for artifact in list(self.hero.equipment.values()) if artifact.rarity == rarity]), len(list(self.hero.equipment.values())))

    def test_no_artifacts(self):
        self.hero.equipment._remove_all()
        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))
