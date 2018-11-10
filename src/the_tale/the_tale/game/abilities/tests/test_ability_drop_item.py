
import smart_imports

smart_imports.all()


class DropItemAbilityTest(helpers.UseAbilityTaskMixin, utils_testcase.TestCase):
    PROCESSOR = deck.drop_item.DropItem

    def setUp(self):
        super(DropItemAbilityTest, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.ability = self.PROCESSOR()

    @property
    def use_attributes(self):
        return super(DropItemAbilityTest, self).use_attributes(hero=self.hero, storage=self.storage)

    def test_no_items(self):
        self.assertEqual(self.hero.bag.occupation, 0)
        self.assertEqual(self.ability.use(**self.use_attributes), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    def test_success(self):
        self.hero.bag.put_artifact(artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL))

        with self.check_delta(lambda: self.hero.bag.occupation, -1):
            self.assertEqual(self.ability.use(**self.use_attributes), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    @mock.patch('the_tale.game.heroes.objects.Hero.might_crit_chance', 1)
    def test_success__critical(self):
        self.hero.bag.put_artifact(artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts, self.hero.level, rarity=artifacts_relations.RARITY.NORMAL))

        old_money_stats = self.hero.statistics.money_earned_from_help

        self.assertEqual(self.hero.bag.occupation, 1)

        self.assertEqual(self.ability.use(**self.use_attributes), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.bag.occupation, 0)

        self.assertTrue(old_money_stats < self.hero.statistics.money_earned_from_help)
