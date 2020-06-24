
import smart_imports

smart_imports.all()


class QuestsTests(utils_testcase.TestCase,
                  helpers.QuestTestsMixin):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero_uid = uids.hero(self.hero.id)

        self.knowledge_base = questgen_knowledge_base.KnowledgeBase()

        self.hero_info = logic.create_hero_info(self.hero)

        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(days=30)

        self.random_person = random.choice(persons_storage.persons.all())

    def test_create(self):
        knowledge_base = logic.create_random_quest_for_person(hero_info=self.hero_info,
                                                              person=self.random_person,
                                                              person_action=relations.PERSON_ACTION.random(),
                                                              logger=mock.Mock())

        self.assertNotEqual(knowledge_base, None)

        enter_uids = set(jump.state_to for jump in knowledge_base.filter(questgen_facts.Jump))
        starts = [start for start in knowledge_base.filter(questgen_facts.Start) if start.uid not in enter_uids]

        self.assertEqual(len(starts), 1)

        start = starts[0]

        person_uid = uids.person(self.random_person.id)

        self.assertTrue(any(participant.start == start.uid and participant.participant == person_uid)
                            for participant in knowledge_base.filter(questgen_facts.QuestParticipant))

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete__help(self):

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           person_id=self.random_person.id,
                                           person_action=relations.PERSON_ACTION.HELP)

        politic_power_storage.places.sync(force=True)

        with self.check_increased(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            self.complete_quest(self.hero)
            politic_power_storage.persons.sync(force=True)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete__help__enemy(self):

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.ENEMY, self.random_person)

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           person_id=self.random_person.id,
                                           person_action=relations.PERSON_ACTION.HELP)

        politic_power_storage.places.sync(force=True)

        with self.check_increased(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            self.complete_quest(self.hero)
            politic_power_storage.persons.sync(force=True)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete__harm(self):

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           person_id=self.random_person.id,
                                           person_action=relations.PERSON_ACTION.HARM)

        politic_power_storage.places.sync(force=True)

        with self.check_decreased(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            self.complete_quest(self.hero)
            politic_power_storage.persons.sync(force=True)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete__harm__friend(self):

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.FRIEND, self.random_person)

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           person_id=self.random_person.id,
                                           person_action=relations.PERSON_ACTION.HARM)

        politic_power_storage.places.sync(force=True)

        with self.check_decreased(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            self.complete_quest(self.hero)
            politic_power_storage.persons.sync(force=True)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_complete__harm__hometown(self):

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, self.random_person.place)

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           person_id=self.random_person.id,
                                           person_action=relations.PERSON_ACTION.HARM)

        politic_power_storage.places.sync(force=True)

        with self.check_decreased(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            self.complete_quest(self.hero)
            politic_power_storage.persons.sync(force=True)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_hero_in_same_place(self):

        self.hero.position.set_place(self.random_person.place)

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           person_id=self.random_person.id,
                                           person_action=relations.PERSON_ACTION.random())

        politic_power_storage.places.sync(force=True)

        with self.check_changed(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            self.complete_quest(self.hero)
            politic_power_storage.persons.sync(force=True)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.check_is_alive', lambda *argv, **kwargs: True)
    def test_hero_in_other_place(self):

        for place in self.places:
            if place.id == self.random_person.place.id:
                continue

            self.hero.position.set_place(self.random_person.place)

            break

        actions_logic.force_new_hero_quest(hero=self.hero,
                                           logger=mock.Mock(),
                                           person_id=self.random_person.id,
                                           person_action=relations.PERSON_ACTION.random())

        politic_power_storage.places.sync(force=True)

        with self.check_changed(lambda: politic_power_storage.persons.outer_power(self.random_person.id)):
            self.complete_quest(self.hero)
            politic_power_storage.persons.sync(force=True)
