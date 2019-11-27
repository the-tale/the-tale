
import smart_imports

smart_imports.all()


class CreateClanTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.CREATE_CLAN

    def setUp(self):
        super(CreateClanTests, self).setUp()

        forum_prototypes.CategoryPrototype.create(caption='category-1', slug=clans_conf.settings.FORUM_CATEGORY_SLUG, order=0)

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

    def test_use(self):

        self.assertEqual(clans_models.Clan.objects.count(), 0)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, extra_data={'name': 'xxx', 'abbr': 'yyy'}))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(clans_models.Clan.objects.count(), 1)

        clan = clans_models.Clan.objects.all()[0]

        self.assertEqual(clan.name, 'xxx')
        self.assertEqual(clan.abbr, 'yyy')

        # default devis MUST be specified, because it used by linguistics
        self.assertEqual(clan.motto, 'Veni, vidi, vici!')

        membership = clans_models.Membership.objects.all()[0]

        self.assertEqual(membership.clan.id, clan.id)
        self.assertEqual(membership.account.id, self.account_1.id)
        self.assertTrue(membership.role.is_MASTER)

    def test_fast_account(self):
        self.account_1.is_fast = True
        self.account_1.save()

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero,
                                                                                    storage=self.storage,
                                                                                    extra_data={'name': 'xxx',
                                                                                                'abbr': 'yyy'}))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(clans_models.Clan.objects.count(), 0)

    def test_already_in_clan(self):
        clans_logic.create_clan(owner=self.account_1,
                                              abbr='aaa',
                                              name='bbb',
                                              motto='Veni, vidi, vici!',
                                              description='')

        self.assertEqual(clans_models.Clan.objects.count(), 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, extra_data={'name': 'xxx', 'abbr': 'yyy'}))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(clans_models.Clan.objects.count(), 1)

    def test_name_exists(self):
        clans_logic.create_clan(owner=self.account_2,
                                              abbr='aaa',
                                              name='xxx',
                                              motto='Veni, vidi, vici!',
                                              description='')

        self.assertEqual(clans_models.Clan.objects.count(), 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, extra_data={'name': 'xxx', 'abbr': 'yyy'}))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(clans_models.Clan.objects.count(), 1)

    def test_abbr_exists(self):
        clans_logic.create_clan(owner=self.account_2,
                                              abbr='yyy',
                                              name='bbb',
                                              motto='Veni, vidi, vici!',
                                              description='')

        self.assertEqual(clans_models.Clan.objects.count(), 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, extra_data={'name': 'xxx', 'abbr': 'yyy'}))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(clans_models.Clan.objects.count(), 1)
