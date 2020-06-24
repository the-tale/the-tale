
import smart_imports

smart_imports.all()


class GetCompanionCreateTests(utils_testcase.TestCase):

    def setUp(self):
        super(GetCompanionCreateTests, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.disabled_companion = companions_logic.create_random_companion_record('disbled')
        self.manual_companion = companions_logic.create_random_companion_record('manual', mode=companions_relations.MODE.MANUAL)

        self.effect = effects.GetCompanion(rarity=companions_relations.RARITY.COMMON)

    def test__no_disabled_companions(self):

        for i in range(100):
            card = self.effect.create_card(type=types.CARD.GET_COMPANION_COMMON, available_for_auction=True)
            self.assertNotEqual(card.data['companion_id'], self.disabled_companion.id)
            self.assertTrue(companions_storage.companions[card.data['companion_id']].state.is_ENABLED)

    def test__no_manual_companions(self):

        for i in range(100):
            card = self.effect.create_card(type=types.CARD.GET_COMPANION_COMMON, available_for_auction=True)
            self.assertNotEqual(card.data['companion_id'], self.manual_companion.id)
            self.assertTrue(companions_storage.companions[card.data['companion_id']].mode.is_AUTOMATIC)


class GetCompanionMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(GetCompanionMixin, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)

        self.card = self.CARD.effect.create_card(type=self.CARD, available_for_auction=True)

    def test_use(self):

        self.assertEqual(self.hero.companion, None)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=self.card))

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.companion.record.rarity.card_rarity, self.CARD.rarity)

    def test_use__companion_exists(self):

        old_companion_record = random.choice([companion
                                              for companion in companions_storage.companions.all()
                                              if companion.rarity.card_rarity != self.CARD.rarity])

        self.hero.set_companion(companions_logic.create_companion(old_companion_record))

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=self.card))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.companion.record.rarity.card_rarity, self.CARD.rarity)
        self.assertNotEqual(self.hero.companion.record.id, old_companion_record.id)

    def test_available(self):
        self.assertTrue(self.CARD.effect.available(self.CARD))

        for companion in companions_storage.companions.all():
            if companion.rarity.card_rarity == self.CARD.rarity:
                companion.state = companions_relations.STATE.DISABLED

        self.assertFalse(self.CARD.effect.available(self.CARD))


class GetCompanionCommonTests(GetCompanionMixin, utils_testcase.TestCase):
    CARD = types.CARD.GET_COMPANION_COMMON


class GetCompanionUncommonTests(GetCompanionMixin, utils_testcase.TestCase):
    CARD = types.CARD.GET_COMPANION_UNCOMMON


class GetCompanionRareTests(GetCompanionMixin, utils_testcase.TestCase):
    CARD = types.CARD.GET_COMPANION_RARE


class GetCompanionEpicTests(GetCompanionMixin, utils_testcase.TestCase):
    CARD = types.CARD.GET_COMPANION_EPIC


class GetCompanionLegendaryTests(GetCompanionMixin, utils_testcase.TestCase):
    CARD = types.CARD.GET_COMPANION_LEGENDARY
