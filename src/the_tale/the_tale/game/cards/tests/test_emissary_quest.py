
import smart_imports

smart_imports.all()


class EmissaryQuestsTest(helpers.CardsTestMixin,
                         clans_helpers.ClansTestsMixin,
                         quests_helpers.QuestTestsMixin,
                         emissaries_helpers.EmissariesTestsMixin,
                         pvp_helpers.PvPTestsMixin,
                         utils_testcase.TestCase):
    CARD = types.CARD.EMISSARY_QUEST

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        self.prepair_forum_for_clans()

        self.account = self.accounts_factory.create_account()

        clans_tt_services.currencies.cmd_debug_clear_service()

        self.clan = self.create_clan(self.account, 0)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=self.places[0].id)

        self.enable_emissary_pvp(self.emissary)

    @contextlib.contextmanager
    def check_free_quests_change(self, delta, clan_id=None):
        if clan_id is None:
            clan_id = self.clan.id

        with self.check_delta(lambda: clans_tt_services.currencies.cmd_balance(clan_id,
                                                                               currency=clans_relations.CURRENCY.FREE_QUESTS),
                              delta):
            yield

    def emissary_power(self, emissary_id=None):
        if emissary_id is None:
            emissary_id = self.emissary.id

        return politic_power_logic.get_emissaries_power([emissary_id])[emissary_id]

    def use_card(self,
                 success,
                 action=quests_relations.PERSON_ACTION.HELP,
                 emissary_id=None,
                 available_for_auction=True):

        if emissary_id is None:
            emissary_id = self.emissary.id

        card = self.CARD.effect.create_card(type=self.CARD,
                                            available_for_auction=available_for_auction,
                                            action=action)

        result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage,
                                                                               hero=self.hero,
                                                                               card=card,
                                                                               value=emissary_id))

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

    def test_use__own_emissary(self):
        with self.check_free_quests_change(0):
            self.use_card(success=True)

        with self.check_increased(lambda: self.emissary_power()):
            self.complete_quest(self.hero)

    def test_use__harm_not_own_emissary(self):
        enemy_account = self.accounts_factory.create_account()

        enemy_clan = self.create_clan(enemy_account, 1)

        enemy_emissary = self.create_emissary(clan=enemy_clan,
                                              initiator=enemy_account,
                                              place_id=self.places[1].id)

        with self.check_free_quests_change(0):
            self.use_card(success=True,
                          action=quests_relations.PERSON_ACTION.HARM,
                          emissary_id=enemy_emissary.id)

        with self.check_decreased(lambda: self.emissary_power(emissary_id=enemy_emissary.id)):
            with self.check_not_changed(lambda: self.emissary_power(emissary_id=self.emissary.id)):
                self.complete_quest(self.hero)

    def test_use__help_not_own_emissary(self):
        enemy_account = self.accounts_factory.create_account()

        enemy_clan = self.create_clan(enemy_account, 1)

        enemy_emissary = self.create_emissary(clan=enemy_clan,
                                              initiator=enemy_account,
                                              place_id=self.places[1].id)

        with self.check_free_quests_change(0):
            self.use_card(success=True,
                          action=quests_relations.PERSON_ACTION.HELP,
                          emissary_id=enemy_emissary.id)

        with self.check_increased(lambda: self.emissary_power(emissary_id=enemy_emissary.id)):
            with self.check_not_changed(lambda: self.emissary_power(emissary_id=self.emissary.id)):
                self.complete_quest(self.hero)

    def test_use__not_own_emissary__not_ready_for_pvp(self):
        self.disable_emissary_pvp(self.emissary)

        enemy_account = self.accounts_factory.create_account()

        enemy_clan = self.create_clan(enemy_account, 1)

        enemy_emissary = self.create_emissary(clan=enemy_clan,
                                              initiator=enemy_account,
                                              place_id=self.places[1].id)

        with self.check_free_quests_change(0):
            self.use_card(success=False,
                          action=quests_relations.PERSON_ACTION.random(),
                          emissary_id=enemy_emissary.id)

        with self.check_not_changed(lambda: self.emissary_power(emissary_id=enemy_emissary.id)):
            with self.check_not_changed(lambda: self.emissary_power(emissary_id=self.emissary.id)):
                self.complete_quest(self.hero)

    def test_wrong_emissary_id(self):
        with self.check_free_quests_change(0):
            self.use_card(success=False, available_for_auction=False, emissary_id=-1)

        with self.check_not_changed(lambda: self.emissary_power()):
            self.complete_quest(self.hero)

    def test_emissary_is_out_game(self):
        emissaries_logic.dismiss_emissary(self.emissary.id)

        with self.check_free_quests_change(0):
            self.use_card(success=False, available_for_auction=False)

        with self.check_not_changed(lambda: self.emissary_power()):
            self.complete_quest(self.hero)

    def test_emissary_hero_in_pvp(self):
        pvp_tt_services.matchmaker.cmd_debug_clear_service()

        battle_info = self.create_pvp_battle(self.account)
        game_turn.increment()
        battle_info.meta_action.process()

        self.hero = battle_info.hero_1

        self.assertTrue(self.hero.actions.has_proxy_actions())

        with self.check_free_quests_change(0):
            self.use_card(success=False, available_for_auction=False)

        self.assertTrue(self.hero.actions.has_proxy_actions())
        self.assertTrue(self.hero.actions.current_action.TYPE.is_META_PROXY)

        with self.check_not_changed(lambda: self.emissary_power()):
            self.complete_quest(self.hero)

    def test_has_free_quests(self):
        enemy_account = self.accounts_factory.create_account()

        enemy_clan = self.create_clan(enemy_account, 1)

        self.create_emissary(clan=enemy_clan,
                             initiator=enemy_account,
                             place_id=self.places[1].id)

        with self.check_free_quests_change(-1, clan_id=self.emissary.clan_id):
            with self.check_free_quests_change(0, clan_id=enemy_clan.id):
                self.use_card(success=True, available_for_auction=False, emissary_id=self.emissary.id)

        with self.check_increased(lambda: self.emissary_power(emissary_id=self.emissary.id)):
            self.complete_quest(self.hero)

    def test_no_free_quests(self):
        clans_tt_services.currencies.cmd_debug_clear_service()

        with self.check_free_quests_change(0):
            self.use_card(success=False, available_for_auction=False)

        with self.check_not_changed(lambda: self.emissary_power()):
            self.complete_quest(self.hero)

    def test_has_free_quests__enemy_clan(self):
        enemy_account = self.accounts_factory.create_account()

        enemy_clan = self.create_clan(enemy_account, 1)

        enemy_emissary = self.create_emissary(clan=enemy_clan,
                                              initiator=enemy_account,
                                              place_id=self.places[1].id)

        with self.check_free_quests_change(0, clan_id=self.emissary.clan_id):
            with self.check_free_quests_change(0, clan_id=enemy_clan.id):
                self.use_card(success=False, available_for_auction=False, emissary_id=enemy_emissary.id)

        with self.check_not_changed(lambda: self.emissary_power(emissary_id=self.emissary.id)):
            with self.check_not_changed(lambda: self.emissary_power(emissary_id=enemy_emissary.id)):
                self.complete_quest(self.hero)

    def test_use__no_clan(self):
        new_leader = self.accounts_factory.create_account()
        clans_logic._add_member(clan=self.clan,
                                account=new_leader,
                                role=clans_relations.MEMBER_ROLE.MASTER)
        clans_logic.change_role(clan=self.clan,
                                initiator=self.account,
                                member=self.account,
                                new_role=clans_relations.MEMBER_ROLE.RECRUIT)
        clans_logic.remove_member(initiator=self.account,
                                  clan=self.clan,
                                  member=self.account)

        with self.check_free_quests_change(0):
            self.use_card(success=False)

        with self.check_not_changed(lambda: self.emissary_power()):
            self.complete_quest(self.hero)
