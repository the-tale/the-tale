# coding: utf-8

import mock

from questgen import facts as questgen_facts
from questgen import knowledge_base as questgen_knowlege_base

from the_tale import amqp_environment

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.quests import logic


class QuestsGeneratorWorkerTests(testcase.TestCase):

    def setUp(self):
        super(QuestsGeneratorWorkerTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        self.worker = amqp_environment.environment.workers.quests_generator

        self.worker.initialize()


    def test_process_request_quest(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_setup_quest') as cmd_setup_quest:
            self.worker.process_request_quest(self.hero.account_id, logic.create_hero_info(self.hero).serialize())

        self.assertEqual(cmd_setup_quest.call_count, 1)

        self.assertEqual(cmd_setup_quest.call_args_list[0][0][0], self.hero.account_id)
        self.assertTrue(questgen_knowlege_base.KnowledgeBase.deserialize(cmd_setup_quest.call_args_list[0][0][1], fact_classes=questgen_facts.FACTS))
