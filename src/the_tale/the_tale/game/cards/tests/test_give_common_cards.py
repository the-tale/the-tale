
import smart_imports

smart_imports.all()


class GiveCommonCardsMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(GiveCommonCardsMixin, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        tt_services.storage.cmd_debug_clear_service()

    def prepair_data(self, available_for_auction):

        card = self.CARD.effect.create_card(type=self.CARD, available_for_auction=available_for_auction)

        self.assertEqual(tt_services.storage.cmd_get_items(self.account_1.id), {})

        return card

    def check_give(self, available_for_auction):

        cards = tt_services.storage.cmd_get_items(self.account_1.id)

        self.assertEqual(len(cards), self.CARD.effect.upper_modificator)

        self.assertTrue(all(card.type.rarity.is_COMMON for card in cards.values()))
        self.assertTrue(all(card.available_for_auction == available_for_auction for card in cards.values()))

    def test_use__available_for_auction(self):
        card = self.prepair_data(available_for_auction=True)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.check_give(available_for_auction=True)

    def test_use__has_companion__not_available_for_auction(self):
        card = self.prepair_data(available_for_auction=False)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.check_give(available_for_auction=False)


class GiveCommonCardsUncommonTests(GiveCommonCardsMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_COMMON_CARDS_UNCOMMON


class GiveCommonCardsRareTests(GiveCommonCardsMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_COMMON_CARDS_RARE


class GiveCommonCardsEpicTests(GiveCommonCardsMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_COMMON_CARDS_EPIC


class GiveCommonCardsLegendaryTests(GiveCommonCardsMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_COMMON_CARDS_LEGENDARY
