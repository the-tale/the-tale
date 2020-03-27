
import smart_imports

smart_imports.all()


class QuestsTests(utils_testcase.TestCase,
                  helpers.QuestTestsMixin,
                  clans_helpers.ClansTestsMixin,
                  emissaries_helpers.EmissariesTestsMixin):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero_uid = uids.hero(self.hero.id)

        self.knowledge_base = questgen_knowledge_base.KnowledgeBase()

        self.prepair_forum_for_clans()

        self.clan = self.create_clan(owner=self.account, uid=1)

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=self.places[0].id)

        self.hero_info = logic.create_hero_info(self.hero)

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(days=30)

    def test_create(self):
        knowledge_base = logic.create_random_quest_for_emissary(hero_info=self.hero_info,
                                                                emissary=self.emissary,
                                                                person_action=relations.PERSON_ACTION.random(),
                                                                logger=mock.Mock())

        self.assertNotEqual(knowledge_base, None)

        enter_uids = set(jump.state_to for jump in knowledge_base.filter(questgen_facts.Jump))
        starts = [start for start in knowledge_base.filter(questgen_facts.Start) if start.uid not in enter_uids]

        self.assertEqual(len(starts), 1)

        start = starts[0]

        emissary_uid = uids.emissary(self.emissary.id)

        self.assertTrue(any(participant.start == start.uid and participant.participant == emissary_uid)
                            for participant in knowledge_base.filter(questgen_facts.QuestParticipant))

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete__help(self):

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=relations.PERSON_ACTION.HELP)

        with self.check_increased(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete__help__enemy(self):

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=relations.PERSON_ACTION.HELP)

        with self.check_increased(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete__harm(self):

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=relations.PERSON_ACTION.HARM)

        with self.check_decreased(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete__harm__hometown(self):

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, self.emissary.place)

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=relations.PERSON_ACTION.HARM)

        with self.check_decreased(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_emissary_in_same_place_with_hero(self):

        self.hero.position.set_place(self.emissary.place)

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=relations.PERSON_ACTION.random())

        with self.check_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    # этот тест проверяет логику выполнения условий стартового узла задания
    # когда герой не находится в точке старта задания
    # в случае переработки логики эмиссаров, необходимо сохранить эту проверку
    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_emissary_in_other_place_that_hero(self):

        for place in self.places:
            if place.id == self.emissary.place.id:
                continue

            self.hero.position.set_place(place)

            break

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=relations.PERSON_ACTION.random())

        self.hero.actions.current_action.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.hero.quests.has_quests)

        while not self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE:
            self.hero.actions.current_action.storage.process_turn(continue_steps_if_needed=False)
            game_turn.increment()

        # проверяем, что первым делом герой идёт в город эмиссара
        self.assertEqual(self.hero.actions.current_action.place_id, self.emissary.place_id)

        with self.check_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    # этот тест проверяет логику выполнения условий стартового узла задания
    # когда герой не находится в точке старта задания
    # в случае переработки логики эмиссаров, необходимо сохранить эту проверку
    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_emissary_hero_on_road(self):

        xy = (0, 0)

        self.assertFalse(any(xy == (place.x, place.y) for place in self.places))

        self.hero.position.set_position(*xy)

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=relations.PERSON_ACTION.random())

        while not self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE:
            self.hero.actions.current_action.storage.process_turn(continue_steps_if_needed=False)
            game_turn.increment()

        # проверяем, что первым делом герой идёт в город эмиссара
        self.assertEqual(self.hero.actions.current_action.place_id, self.emissary.place_id)

        with self.check_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete_after_emissary_removed__no_quest_generated(self):

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=relations.PERSON_ACTION.HELP)

        self.assertFalse(self.hero.quests.has_quests)

        emissaries_logic.dismiss_emissary(emissary_id=self.emissary.id)

        with self.check_not_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete_after_emissary_removed__has_quest_generated(self):

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           emissary_id=self.emissary.id,
                                           person_action=relations.PERSON_ACTION.HELP)

        while not self.hero.quests.has_quests:
            self.storage.process_turn(continue_steps_if_needed=False)

        emissaries_logic.dismiss_emissary(emissary_id=self.emissary.id)

        with self.check_not_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
            self.complete_quest(self.hero)
