
import smart_imports

smart_imports.all()


class ForceNewHeroQuestTests(utils_testcase.TestCase,
                             quests_helpers.QuestTestsMixin,
                             clans_helpers.ClansTestsMixin,
                             emissaries_helpers.EmissariesTestsMixin,
                             pvp_helpers.PvPTestsMixin):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.prepair_forum_for_clans()

        self.clan = self.create_clan(owner=self.account, uid=1)

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=self.places[0].id)

    def test_no_quest__idleness_for_emissary(self):
        self.assertTrue(self.hero.actions.current_action.TYPE.is_IDLENESS)

        with mock.patch('the_tale.game.actions.prototypes.ActionQuestPrototype.technical_setup_quest_required', lambda self: False):
            logic.force_new_hero_quest(hero=self.hero,
                                       logger=mock.Mock(),
                                       emissary_id=self.emissary.id,
                                       person_action=quests_relations.PERSON_ACTION.random())

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        self.storage.process_turn()

        quest_actor = self.hero.quests.current_quest.current_info.actors[questgen_quests_base_quest.ROLES.INITIATOR]

        actor_internal_type, actor_id, actor_name = quest_actor

        self.assertEqual(actor_internal_type, game_relations.ACTOR.EMISSARY.value)
        self.assertEqual(actor_id, self.emissary.id)

        with self.check_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    def test_no_quest__idleness_for_normal_quest(self):
        self.assertTrue(self.hero.actions.current_action.TYPE.is_IDLENESS)

        with mock.patch('the_tale.game.actions.prototypes.ActionQuestPrototype.technical_setup_quest_required', lambda self: False):
            logic.force_new_hero_quest(hero=self.hero,
                                       logger=mock.Mock())

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        with self.check_not_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    def test_no_quest__idleness_wih_non_quest_action(self):
        self.storage.process_turn()

        self.assertTrue(self.hero.actions.current_action.TYPE.is_FIRST_STEPS)

        with mock.patch('the_tale.game.actions.prototypes.ActionQuestPrototype.technical_setup_quest_required', lambda self: False):
            logic.force_new_hero_quest(hero=self.hero,
                                       logger=mock.Mock(),
                                       emissary_id=self.emissary.id,
                                       person_action=quests_relations.PERSON_ACTION.random())

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        self.complete_quest(self.hero)

    def test_has_quest__no_subactions(self):
        self.turn_to_quest(storage=self.storage,
                           hero_id=self.hero.id,
                           continue_steps_if_needed=False,
                           generate_quest=False)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)
        self.assertFalse(self.hero.quests.has_quests)

        with mock.patch('the_tale.game.actions.prototypes.ActionQuestPrototype.technical_setup_quest_required', lambda self: False):
            logic.force_new_hero_quest(hero=self.hero,
                                       logger=mock.Mock(),
                                       emissary_id=self.emissary.id,
                                       person_action=quests_relations.PERSON_ACTION.random())

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        with self.check_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    def test_has_quest__no_quest_generated(self):
        self.turn_to_quest(storage=self.storage,
                           hero_id=self.hero.id,
                           continue_steps_if_needed=False,
                           generate_quest=False)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)
        self.assertFalse(self.hero.quests.has_quests)

        with mock.patch('the_tale.game.actions.prototypes.ActionQuestPrototype.technical_setup_quest_required', lambda self: False):
            logic.force_new_hero_quest(hero=self.hero,
                                       logger=mock.Mock(),
                                       emissary_id=self.emissary.id,
                                       person_action=quests_relations.PERSON_ACTION.random())

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        with self.check_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    def test_has_quest__has_subactions(self):
        self.turn_to_quest(storage=self.storage,
                           hero_id=self.hero.id,
                           continue_steps_if_needed=False)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        while self.hero.actions.current_action.TYPE.is_QUEST:
            self.storage.process_turn()

        with mock.patch('the_tale.game.actions.prototypes.ActionQuestPrototype.technical_setup_quest_required', lambda self: False):
            logic.force_new_hero_quest(hero=self.hero,
                                       logger=mock.Mock(),
                                       emissary_id=self.emissary.id,
                                       person_action=quests_relations.PERSON_ACTION.random())

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        with self.check_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    def test_has_quest__on_battle(self):
        self.turn_to_quest(storage=self.storage,
                           hero_id=self.hero.id,
                           continue_steps_if_needed=False)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        while self.hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1:
            self.storage.process_turn()

        with mock.patch('the_tale.game.actions.prototypes.ActionQuestPrototype.technical_setup_quest_required', lambda self: False):
            logic.force_new_hero_quest(hero=self.hero,
                                       logger=mock.Mock(),
                                       emissary_id=self.emissary.id,
                                       person_action=quests_relations.PERSON_ACTION.random())

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        with self.check_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    def test_when_pvp(self):
        pvp_tt_services.matchmaker.cmd_debug_clear_service()

        battle_info = self.create_pvp_battle()

        game_turn.increment()
        battle_info.meta_action.process()

        with self.assertRaises(NotImplementedError):
            with mock.patch('the_tale.game.actions.prototypes.ActionQuestPrototype.technical_setup_quest_required', lambda self: False):
                logic.force_new_hero_quest(hero=battle_info.meta_action.hero_1,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=quests_relations.PERSON_ACTION.random())

        while battle_info.meta_action.state != meta_actions.ArenaPvP1x1.STATE.PROCESSED:
            game_turn.increment()
            battle_info.meta_action.process()
