
import smart_imports

smart_imports.all()


class InstantMonsterKillTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.INSTANT_MONSTER_KILL

    def setUp(self):
        super(InstantMonsterKillTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_no_battle(self):
        self.assertFalse(self.hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    def test_use(self):
        with mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 0):
            actions_prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.mobs.create_mob_for_hero(self.hero))

        self.assertTrue(self.hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1)
        self.assertTrue(self.hero.actions.current_action.mob.health > 0)
        self.assertTrue(self.hero.actions.current_action.percents < 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.actions.current_action.mob.health <= 0)
        self.assertEqual(self.hero.actions.current_action.percents, 1)
