# coding: utf-8

import mock

import collections

from questgen import facts as questgen_facts
from questgen import knowledge_base as questgen_knowlege_base

from the_tale import amqp_environment

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.quests import logic
from the_tale.game.quests.workers import quests_generator


class QuestsGeneratorWorkerTests(testcase.TestCase):

    def setUp(self):
        super(QuestsGeneratorWorkerTests, self).setUp()
        create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)
        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.worker = quests_generator.Worker(name='game_quests_generator')

        self.worker.initialize()


    def test_process_request_quest(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_setup_quest') as cmd_setup_quest:
            self.worker.process_request_quest(self.hero_1.account_id, logic.create_hero_info(self.hero_1).serialize())
            self.worker.generate_quest()

        self.assertEqual(cmd_setup_quest.call_count, 1)

        self.assertEqual(cmd_setup_quest.call_args_list[0][0][0], self.hero_1.account_id)
        self.assertTrue(questgen_knowlege_base.KnowledgeBase.deserialize(cmd_setup_quest.call_args_list[0][0][1], fact_classes=questgen_facts.FACTS))


    def test_generate_quest__empty_queue(self):
        self.worker.generate_quest()


    def test_process_request_quest__query(self):
        old_hero_1_info = logic.create_hero_info(self.hero_1)

        self.hero_1.level = 666

        new_hero_1_info = logic.create_hero_info(self.hero_1)

        hero_2_info = logic.create_hero_info(self.hero_2)

        self.assertNotEqual(old_hero_1_info, new_hero_1_info)

        self.worker.process_request_quest(self.hero_1.account_id, old_hero_1_info.serialize())
        self.worker.process_request_quest(self.hero_2.account_id, hero_2_info.serialize())
        self.worker.process_request_quest(self.hero_1.account_id, new_hero_1_info.serialize())

        self.assertEqual(self.worker.requests_query, collections.deque([self.account_1.id, self.account_2.id]))
        self.assertEqual(self.worker.requests_heroes_infos, {self.account_1.id: new_hero_1_info, self.account_2.id: hero_2_info})

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_setup_quest') as cmd_setup_quest:
            self.worker.generate_quest()

        self.assertEqual(cmd_setup_quest.call_args_list[0][0][0], self.account_1.id)

        self.assertEqual(self.worker.requests_query, collections.deque([self.account_2.id]))
        self.assertEqual(self.worker.requests_heroes_infos, {self.account_2.id: hero_2_info})

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_setup_quest') as cmd_setup_quest:
            self.worker.generate_quest()

        self.assertEqual(cmd_setup_quest.call_args_list[0][0][0], self.account_2.id)

        self.assertEqual(self.worker.requests_query, collections.deque())
        self.assertEqual(self.worker.requests_heroes_infos, {})
