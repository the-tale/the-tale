# coding: utf-8
import mock

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionQuestPrototype
from game.quests.logic import create_random_quest_for_hero
from game.prototypes import TimePrototype


class workers_environment__highlevel__cmd_change_person_power(object):

    def __init__(self):
        self.commands = []

    def __call__(self, person_id, power):
        self.commands.append((person_id, power))


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
        fake_cmd = workers_environment__highlevel__cmd_change_person_power()

        with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power', fake_cmd):
            self.complete_quest()

        self.assertTrue(not fake_cmd.commands)

    def test_power_on_end_quest_for_normal_account_hero(self):

        self.hero.is_fast = False

        fake_cmd = workers_environment__highlevel__cmd_change_person_power()

        with mock.patch('game.workers.environment.workers_environment.highlevel.cmd_change_person_power', fake_cmd):
            self.complete_quest()

        self.assertTrue(fake_cmd.commands)
