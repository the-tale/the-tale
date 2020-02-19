
import smart_imports

smart_imports.all()


class QuestForPersonTest(helpers.CardsTestMixin,
                         quests_helpers.QuestTestsMixin,
                         pvp_helpers.PvPTestsMixin,
                         utils_testcase.TestCase):

    CARD = types.CARD.QUEST_FOR_PERSON

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(days=30)

        self.random_person = random.choice(persons_storage.persons.all())

    def use_card(self,
                 success,
                 action=quests_relations.PERSON_ACTION.HELP,
                 person_id=None,
                 available_for_auction=True):

        if person_id is None:
            person_id = self.random_person.id

        card = self.CARD.effect.create_card(type=self.CARD,
                                            available_for_auction=available_for_auction,
                                            action=action)

        result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage,
                                                                               hero=self.hero,
                                                                               card=card,
                                                                               value=person_id))

        if success:
            self.assertEqual((result, step, postsave_actions),
                             (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                              game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                              ()))
        else:
            self.assertEqual((result, step, postsave_actions),
                             (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED,
                              game_postponed_tasks.ComplexChangeTask.STEP.ERROR,
                              ()))

    def test_use__help(self):
        self.use_card(success=True,
                      action=quests_relations.PERSON_ACTION.HELP)

        politic_power_storage.persons.sync(force=True)

        with self.check_increased(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            with self.check_increased(lambda: politic_power_storage.persons.inner_power(self.random_person.id)):
                self.complete_quest(self.hero)
                politic_power_storage.persons.sync(force=True)

    def test_use__harm(self):
        self.use_card(success=True,
                      action=quests_relations.PERSON_ACTION.HARM)

        politic_power_storage.persons.sync(force=True)

        with self.check_decreased(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            with self.check_decreased(lambda: politic_power_storage.persons.inner_power(self.random_person.id)):
                self.complete_quest(self.hero)
                politic_power_storage.persons.sync(force=True)

    def test_wrong_person_id(self):
        self.use_card(success=False, available_for_auction=False, person_id=-1)

        politic_power_storage.persons.sync(force=True)

        with self.check_not_changed(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            with self.check_not_changed(lambda: politic_power_storage.persons.inner_power(self.random_person.id)):
                self.complete_quest(self.hero)
                politic_power_storage.persons.sync(force=True)

    def test_hero_in_pvp(self):
        pvp_tt_services.matchmaker.cmd_debug_clear_service()

        battle_info = self.create_pvp_battle(self.account)
        game_turn.increment()
        battle_info.meta_action.process()

        self.hero = battle_info.hero_1

        self.assertTrue(self.hero.actions.has_proxy_actions())

        self.use_card(success=False, available_for_auction=False)

        self.assertTrue(self.hero.actions.has_proxy_actions())
        self.assertTrue(self.hero.actions.current_action.TYPE.is_META_PROXY)
