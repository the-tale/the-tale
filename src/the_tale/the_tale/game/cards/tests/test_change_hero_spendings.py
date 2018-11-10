
import smart_imports

smart_imports.all()


class ChangeHeroSpendings(utils_testcase.TestCase, helpers.CardsTestMixin):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        old_companion_record = random.choice(companions_storage.companions.all())
        self.hero.set_companion(companions_logic.create_companion(old_companion_record))

    def test_use(self):

        # sure that quests will be loaded and not cal mark_updated
        self.hero.quests.mark_updated()

        for item in heroes_relations.ITEMS_OF_EXPENDITURE.records:
            card = types.CARD.CHANGE_HERO_SPENDINGS.effect.create_card(type=types.CARD.CHANGE_HERO_SPENDINGS,
                                                                       available_for_auction=True,
                                                                       item=item)

            while self.hero.next_spending == item:
                self.hero.switch_spending()

            with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
                result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))

            self.assertEqual(mark_updated.call_count, 1)

            self.assertEqual(self.hero.next_spending, item)

            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    def test_equal(self):
        card = types.CARD.CHANGE_HERO_SPENDINGS.effect.create_card(type=types.CARD.CHANGE_HERO_SPENDINGS,
                                                                   available_for_auction=True,
                                                                   item=self.hero.next_spending)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))

        self.assertEqual(mark_updated.call_count, 0)

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    def test_use__no_companion(self):
        self.hero.remove_companion()

        item = heroes_relations.ITEMS_OF_EXPENDITURE.HEAL_COMPANION

        card = types.CARD.CHANGE_HERO_SPENDINGS.effect.create_card(type=types.CARD.CHANGE_HERO_SPENDINGS,
                                                                   available_for_auction=True,
                                                                   item=item)

        while self.hero.next_spending == item:
            self.hero.switch_spending()

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero, card=card))

        self.assertEqual(mark_updated.call_count, 0)

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertNotEqual(self.hero.next_spending, item)
