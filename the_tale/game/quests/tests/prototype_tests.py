# coding: utf-8
import mock

from django.test import TestCase

from common.utils.fake import FakeWorkerCommand

from game.logic import create_test_bundle, create_test_map
from game.actions.prototypes import ActionQuestPrototype
from game.quests.logic import create_random_quest_for_hero
from game.prototypes import TimePrototype


class QuestPrototypeTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('QuestActionTest')
        self.hero = self.bundle.tests_get_hero()
        self.action_idl = self.bundle.tests_get_last_action()
        self.quest = create_random_quest_for_hero(self.hero)
        self.action_quest = ActionQuestPrototype.create(self.action_idl, quest=self.quest)

    def tearDown(self):
        pass

    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        # just test that quest will be ended
        while not self.action_idl.leader:
            self.bundle.process_turn()
            current_time.increment_turn()

    def test_power_on_end_quest_for_fast_account_hero(self):
        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power', fake_cmd):
            self.complete_quest()

        self.assertFalse(fake_cmd.commands)

    def test_power_on_end_quest_for_normal_account_hero(self):

        self.hero.is_fast = False

        fake_cmd = FakeWorkerCommand()

        with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power', fake_cmd):
            self.complete_quest()

        self.assertTrue(fake_cmd.commands)
