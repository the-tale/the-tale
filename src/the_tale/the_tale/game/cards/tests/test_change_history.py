
import smart_imports

smart_imports.all()


HISTORY_TYPE = types.CARD.CHANGE_HISTORY.effect.HISTORY_TYPE


class ChangeHistory(utils_testcase.TestCase, helpers.CardsTestMixin):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_has_form(self):
        for history_type in HISTORY_TYPE.records:
            card = types.CARD.CHANGE_HISTORY.effect.create_card(type=types.CARD.CHANGE_HISTORY,
                                                                available_for_auction=True,
                                                                history=history_type)
            self.assertNotEqual(card.get_form(hero=self.hero), None)

    def use_card(self, history, form_value, success=True):
        card = types.CARD.CHANGE_HISTORY.effect.create_card(type=types.CARD.CHANGE_HISTORY,
                                                            available_for_auction=True,
                                                            history=history)

        form = card.get_form(data={'value': form_value}, hero=self.hero)

        self.assertTrue(form.is_valid())

        result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage,
                                                                               hero=self.hero,
                                                                               value=form.get_card_data()['value'],
                                                                               card=card))

        expected_result = (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ())

        if not success:
            expected_result = (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ())

        self.assertEqual((result, step, postsave_actions), expected_result)

    def test_upbringing__changed(self):
        new_upbringing = tt_beings_relations.UPBRINGING.random(exclude=(self.hero.upbringing,))

        self.use_card(HISTORY_TYPE.UPBRINGING, new_upbringing)

        self.assertEqual(self.hero.upbringing, new_upbringing)

    def test_upbringing__not_changed(self):
        self.use_card(HISTORY_TYPE.UPBRINGING, self.hero.upbringing, success=False)

    def test_death_age__changed(self):
        new_age = tt_beings_relations.AGE.random(exclude=(self.hero.death_age,))

        self.use_card(HISTORY_TYPE.DEATH_AGE, new_age)

        self.assertEqual(self.hero.death_age, new_age)

    def test_death_age__not_changed(self):
        self.use_card(HISTORY_TYPE.DEATH_AGE, self.hero.death_age, success=False)

    def test_first_death__changed(self):
        new_first_death = tt_beings_relations.FIRST_DEATH.random(exclude=(self.hero.first_death,))

        self.use_card(HISTORY_TYPE.FIRST_DEATH, new_first_death)

        self.assertEqual(self.hero.first_death, new_first_death)

    def test_first_death__not_changed(self):
        self.use_card(HISTORY_TYPE.FIRST_DEATH, self.hero.first_death, success=False)
