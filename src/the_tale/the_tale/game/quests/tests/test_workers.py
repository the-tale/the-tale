
import smart_imports

smart_imports.all()


class QuestsGeneratorWorkerTests(clans_helpers.ClansTestsMixin,
                                 emissaries_helpers.EmissariesTestsMixin,
                                 utils_testcase.TestCase):

    def setUp(self):
        super(QuestsGeneratorWorkerTests, self).setUp()
        self.places = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)
        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.prepair_forum_for_clans()

        self.clan = self.create_clan(owner=self.account_1, uid=1)

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account_1,
                                             place_id=self.places[0].id)

        self.worker = quests_workers_quests_generator.Worker(name='game_quests_generator')

        self.worker.initialize()

    def test_process_request_quest(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_setup_quest') as cmd_setup_quest:
            self.worker.process_request_quest(self.hero_1.account_id,
                                              hero_info=logic.create_hero_info(self.hero_1).serialize(),
                                              emissary_id=None,
                                              person_action=None)
            self.worker.generate_quest()

        self.assertEqual(cmd_setup_quest.call_count, 1)

        self.assertEqual(cmd_setup_quest.call_args_list[0][0][0], self.hero_1.account_id)
        self.assertTrue(questgen_knowledge_base.KnowledgeBase.deserialize(cmd_setup_quest.call_args_list[0][0][1], fact_classes=questgen_facts.FACTS))

    def test_generate_quest__empty_queue(self):
        self.worker.generate_quest()

    maxDiff=None
    def test_process_request_quest__query(self):
        old_hero_1_info = logic.create_hero_info(self.hero_1)

        self.hero_1.level = 666

        new_hero_1_info = logic.create_hero_info(self.hero_1)

        hero_2_info = logic.create_hero_info(self.hero_2)

        self.assertNotEqual(old_hero_1_info, new_hero_1_info)

        self.worker.process_request_quest(self.hero_1.account_id,
                                          hero_info=old_hero_1_info.serialize(),
                                          emissary_id=None,
                                          person_action=None)
        self.worker.process_request_quest(self.hero_2.account_id,
                                          hero_info=hero_2_info.serialize(),
                                          emissary_id=self.emissary.id,
                                          person_action=relations.PERSON_ACTION.HARM.value)
        self.worker.process_request_quest(self.hero_1.account_id,
                                          hero_info=new_hero_1_info.serialize(),
                                          emissary_id=None,
                                          person_action=None)

        self.assertEqual(self.worker.requests_query, collections.deque([self.account_1.id, self.account_2.id]))

        self.assertEqual(self.worker.requests_heroes_infos,
                         {self.account_1.id: {'info': new_hero_1_info,
                                              'emissary_id': None,
                                              'person_action': None},
                          self.account_2.id: {'info': hero_2_info,
                                              'emissary_id': self.emissary.id,
                                              'person_action': relations.PERSON_ACTION.HARM}})

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_setup_quest') as cmd_setup_quest:
            self.worker.generate_quest()

        self.assertEqual(cmd_setup_quest.call_args_list[0][0][0], self.account_1.id)

        self.assertEqual(self.worker.requests_query, collections.deque([self.account_2.id]))
        self.assertEqual(self.worker.requests_heroes_infos,
                         {self.account_2.id: {'info': hero_2_info,
                                              'emissary_id': self.emissary.id,
                                              'person_action': relations.PERSON_ACTION.HARM}})

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_setup_quest') as cmd_setup_quest:
            self.worker.generate_quest()

        self.assertEqual(cmd_setup_quest.call_args_list[0][0][0], self.account_2.id)

        self.assertEqual(self.worker.requests_query, collections.deque())
        self.assertEqual(self.worker.requests_heroes_infos, {})
