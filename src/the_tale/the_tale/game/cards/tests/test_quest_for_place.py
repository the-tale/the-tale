
import smart_imports

smart_imports.all()


class QuestForPlaceTest(helpers.CardsTestMixin,
                        quests_helpers.QuestTestsMixin,
                        pvp_helpers.PvPTestsMixin,
                        utils_testcase.TestCase):

    CARD = types.CARD.QUEST_FOR_PLACE

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(days=30)

        self.random_place = random.choice(self.places)

    def use_card(self,
                 success,
                 action=quests_relations.PERSON_ACTION.HELP,
                 place_id=None,
                 available_for_auction=True):

        if place_id is None:
            place_id = self.random_place.id

        card = self.CARD.effect.create_card(type=self.CARD,
                                            available_for_auction=available_for_auction,
                                            action=action)

        result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage,
                                                                               hero=self.hero,
                                                                               card=card,
                                                                               value=place_id))

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

        politic_power_storage.places.sync(force=True)

        with self.check_increased(lambda: politic_power_storage.places.outer_power(self.random_place.id)):
            with self.check_increased(lambda: politic_power_storage.places.inner_power(self.random_place.id)):
                self.complete_quest(self.hero)
                politic_power_storage.places.sync(force=True)

    def test_use__harm(self):
        self.use_card(success=True,
                      action=quests_relations.PERSON_ACTION.HARM)

        politic_power_storage.places.sync(force=True)

        with self.check_decreased(lambda: politic_power_storage.places.outer_power(self.random_place.id)):
            with self.check_decreased(lambda: politic_power_storage.places.inner_power(self.random_place.id)):
                self.complete_quest(self.hero)
                politic_power_storage.places.sync(force=True)

    def test_wrong_place_id(self):
        self.use_card(success=False, available_for_auction=False, place_id=-1)

        politic_power_storage.places.sync(force=True)

        with self.check_not_changed(lambda: politic_power_storage.places.outer_power(self.random_place.id)):
            with self.check_not_changed(lambda: politic_power_storage.places.inner_power(self.random_place.id)):
                self.complete_quest(self.hero)
                politic_power_storage.places.sync(force=True)

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
