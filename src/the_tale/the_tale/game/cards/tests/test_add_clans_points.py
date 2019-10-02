
import smart_imports

smart_imports.all()


class AddClansPointsTestMixin(helpers.CardsTestMixin,
                              clans_helpers.ClansTestsMixin):
    CARD = None

    def setUp(self):
        super(AddClansPointsTestMixin, self).setUp()

        forum_prototypes.CategoryPrototype.create(caption='category-1', slug=clans_conf.settings.FORUM_CATEGORY_SLUG, order=0)

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.clan_1 = self.create_clan(self.account_1, 0)

        clans_tt_services.chronicle.cmd_debug_clear_service()
        clans_tt_services.currencies.cmd_debug_clear_service()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_use(self):
        with self.check_delta(lambda: clans_tt_services.currencies.cmd_balance(self.clan_1.id,
                                                                               currency=clans_relations.CURRENCY.ACTION_POINTS),
                              self.CARD.effect.upper_modificator):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                          game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                          ()))

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan_1, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan_1.meta_object().tag,
                          clans_relations.EVENT.MEMBER_ADD_POINTS.meta_object().tag,
                          self.account_1.meta_object().tag})

    def test_error(self):
        clans_tt_services.currencies.cmd_change_balance(account_id=self.clan_1.id,
                                                        type='test',
                                                        amount=tt_clans_constants.MAXIMUM_POINTS,
                                                        async=False,
                                                        currency=clans_relations.CURRENCY.ACTION_POINTS,
                                                        autocommit=True)

        with self.check_not_changed(lambda: clans_tt_services.currencies.cmd_balance(self.clan_1.id,
                                                                                     currency=clans_relations.CURRENCY.ACTION_POINTS)):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED,
                          game_postponed_tasks.ComplexChangeTask.STEP.ERROR,
                          ()))


class AddClansPointsRareTests(AddClansPointsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_CLANS_POINTS_RARE


class AddClansPointsEpicTests(AddClansPointsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_CLANS_POINTS_EPIC


class AddClansPointsLegendaryTests(AddClansPointsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.ADD_CLANS_POINTS_LEGENDARY


class CommonTests(utils_testcase.TestCase):

    def test_expected_values(self):
        self.assertEqual(types.CARD.ADD_CLANS_POINTS_LEGENDARY.effect.upper_modificator, tt_clans_constants.TOP_CARD_POINTS_BONUS)
        self.assertTrue(types.CARD.ADD_CLANS_POINTS_RARE.effect.upper_modificator <
                        types.CARD.ADD_CLANS_POINTS_EPIC.effect.upper_modificator <
                        types.CARD.ADD_CLANS_POINTS_LEGENDARY.effect.upper_modificator)
