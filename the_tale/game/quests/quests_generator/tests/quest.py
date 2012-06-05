# coding: utf-8

from django.test import TestCase

from game.quests.quests_generator import commands as cmd
from game.quests.quests_generator.environment import BaseEnvironment
from game.quests.quests_generator.lines import BaseQuestsSource
from game.quests.quests_generator.knowlege_base import KnowlegeBase
from game.quests.quests_generator.exceptions import QuestGeneratorException
from game.quests.quests_generator.tests.helpers import FakeQuest, JustQuest, FakeCmd

quests_source = BaseQuestsSource()
writers_constructor = lambda hero, quest_type, env, quest_env_local: 0

class QuestTest(TestCase):

    def setUp(self):
        self.knowlege_base = KnowlegeBase()
        self.knowlege_base.add_place('place_1')
        self.knowlege_base.add_place('place_2')
        self.knowlege_base.add_person('person_1', place='place_1', external_data={})
        self.knowlege_base.add_person('person_2', place='place_2', external_data={})
        self.knowlege_base.initialize()

        self.FIRST_CHOICE_LINE = 'line_2'
        self.SECOND_CHOICE_LINE = 'line_3'

        self.env = BaseEnvironment(quests_source=quests_source, writers_constructor=writers_constructor, knowlege_base=self.knowlege_base)

        self.fake_quest = FakeQuest(commands_number=13)
        self.fake_quest.initialize('fake_quest', self.env)
        self.fake_quest.create_line(self.env)
        self.env.quests['quest_1'] = self.fake_quest

        self.quest = JustQuest()
        self.quest.initialize('quest', self.env)
        self.quest.create_line(self.env)

        self.cmd_linear_move = cmd.Move(event='event_1_1', place='place_1')
        self.cmd_linear_give_power = cmd.GivePower(event='event_1_8', person='person_1', power=2, multiply=3, depends_on='person_2')

        self.cmd_quest_move = cmd.Move(event='event_2_1', place='place_2')
        self.cmd_quest_quest = cmd.Quest(event='event_2_2', quest='quest_1')
        self.cmd_quest_get_reward = cmd.GetReward(event='event_2_3', person='person_2')

        self.cmd_move = cmd.Move(event='event_3_1', place='place_3')
        self.cmd_choose = cmd.Choose(id='choose_1',
                                     default='choice_1',
                                     choices={'choice_1': self.FIRST_CHOICE_LINE,
                                              'choice_2': self.SECOND_CHOICE_LINE },
                                     event='event_3_2',
                                     choice='choice_id_1')


    def test_initialize(self):
        self.assertTrue(self.quest.env_local.place_start)
        self.assertTrue(self.quest.env_local.person_start)
        self.assertTrue(self.quest.env_local.place_end)
        self.assertTrue(self.quest.env_local.person_end)

    def test_wrong_initialization(self):
        self.quest = JustQuest()
        self.assertRaises(QuestGeneratorException, self.quest.initialize, 'quest', self.env, person_start='person_1')
        self.assertRaises(QuestGeneratorException, self.quest.initialize, 'quest', self.env, person_end='person_1')

    def test_get_commands_number(self):
        self.assertEqual(self.quest.get_commands_number(self.env), 19)
        self.assertEqual(self.quest.get_commands_number(self.env, pointer=[1]), 1)
        self.assertEqual(self.quest.get_commands_number(self.env, [1, self.FIRST_CHOICE_LINE, 0]), 2)
        self.assertEqual(self.quest.get_commands_number(self.env, [1, self.FIRST_CHOICE_LINE, 7]), 9)
        self.assertEqual(self.quest.get_commands_number(self.env, [1, self.SECOND_CHOICE_LINE, 0]), 2)
        self.assertEqual(self.quest.get_commands_number(self.env, [1, self.SECOND_CHOICE_LINE, 2]), 17)
        self.assertEqual(self.quest.get_commands_number(self.env, pointer=[2]), 18)
        self.assertRaises(QuestGeneratorException, self.quest.get_commands_number, self.env, pointer=[9])

    def test_get_percents(self):
        self.assertTrue(self.quest.get_percents(self.env, [0]) == 0.0)

        self.assertTrue(0.052 < self.quest.get_percents(self.env, pointer=[1]) < 0.053)
        self.assertTrue(0.1052 < self.quest.get_percents(self.env, [1, self.FIRST_CHOICE_LINE, 0]) < 0.1053)
        self.assertTrue(0.473 < self.quest.get_percents(self.env, [1, self.FIRST_CHOICE_LINE, 7]) < 0.474)
        self.assertTrue(0.1052 < self.quest.get_percents(self.env, [1, self.SECOND_CHOICE_LINE, 0]) < 0.1053)
        self.assertTrue(0.894 < self.quest.get_percents(self.env, [1, self.SECOND_CHOICE_LINE, 2]) < 0.895)
        self.assertTrue(0.947 < self.quest.get_percents(self.env, pointer=[2]) < 0.948)
        self.assertRaises(QuestGeneratorException, self.quest.get_commands_number, self.env, pointer=[9])

    def test_get_start_pointer(self):
        self.assertEqual(self.quest.get_start_pointer(self.env), [0])


    def test_increment_pointer(self):
        self.assertEqual(self.quest.increment_pointer(self.env, [0], {}), [1])
        self.assertEqual(self.quest.increment_pointer(self.env, [1], {}), [1, self.FIRST_CHOICE_LINE, 0])
        self.assertEqual(self.quest.increment_pointer(self.env, [1, self.FIRST_CHOICE_LINE, 0], {}), [1, self.FIRST_CHOICE_LINE, 1])
        self.assertEqual(self.quest.increment_pointer(self.env, [1, self.FIRST_CHOICE_LINE, 7], {}), [2])
        self.assertEqual(self.quest.increment_pointer(self.env, [1], {'choose_1': 'choice_2'}), [1, self.SECOND_CHOICE_LINE, 0])
        self.assertEqual(self.quest.increment_pointer(self.env, [1, self.SECOND_CHOICE_LINE, 0], {'choose_1': 'choice_2'}), [1, self.SECOND_CHOICE_LINE, 1])
        self.assertEqual(self.quest.increment_pointer(self.env, [1, self.SECOND_CHOICE_LINE, 2], {'choose_1': 'choice_2'}), [2])
        self.assertEqual(self.quest.increment_pointer(self.env, [2], {}), None)
        self.assertRaises(QuestGeneratorException, self.quest.increment_pointer, self.env, [3], {})

    def test_get_quest_action_chain(self):
        self.assertEqual(self.quest.get_quest_action_chain(self.env, [0]), [(self.quest, self.cmd_move)])
        self.assertEqual(self.quest.get_quest_action_chain(self.env, [1]), [(self.quest, self.cmd_choose)])

        self.assertRaises(QuestGeneratorException, self.quest.get_quest_action_chain, self.env, [1, 'line_1', 0])

        self.assertEqual(self.quest.get_quest_action_chain(self.env, [1, self.FIRST_CHOICE_LINE, 0]), [(self.quest, self.cmd_linear_move)])
        self.assertEqual(self.quest.get_quest_action_chain(self.env, [1, self.FIRST_CHOICE_LINE, 7]), [(self.quest, self.cmd_linear_give_power)])
        self.assertRaises(QuestGeneratorException, self.quest.get_quest_action_chain, self.env, [1, self.FIRST_CHOICE_LINE, 7, 8])
        self.assertRaises(QuestGeneratorException, self.quest.get_quest_action_chain, self.env, [1, self.FIRST_CHOICE_LINE, 8])

        self.assertEqual(self.quest.get_quest_action_chain(self.env, [1, self.SECOND_CHOICE_LINE, 0]), [(self.quest, self.cmd_quest_move)])
        self.assertEqual(self.quest.get_quest_action_chain(self.env, [1, self.SECOND_CHOICE_LINE, 1]), [(self.quest, self.cmd_quest_quest)])
        self.assertEqual(self.quest.get_quest_action_chain(self.env, [1, self.SECOND_CHOICE_LINE, 1, 0]), [(self.quest, self.cmd_quest_quest), (self.fake_quest, FakeCmd('fake_event'))])
        self.assertEqual(self.quest.get_quest_action_chain(self.env, [1, self.SECOND_CHOICE_LINE, 1, 2]), [(self.quest, self.cmd_quest_quest), (self.fake_quest, FakeCmd('fake_event'))])
        self.assertEqual(self.quest.get_quest_action_chain(self.env, [1, self.SECOND_CHOICE_LINE, 2]), [(self.quest, self.cmd_quest_get_reward)])
        self.assertRaises(QuestGeneratorException, self.quest.get_quest_action_chain, self.env, [1, self.SECOND_CHOICE_LINE, 3])

    def test_get_command(self):
        self.assertEqual(self.quest.get_command(self.env, [0]), self.cmd_move)
        self.assertEqual(self.quest.get_command(self.env, [1]), self.cmd_choose)
        self.assertEqual(self.quest.get_command(self.env, [1, self.FIRST_CHOICE_LINE, 0]), self.cmd_linear_move)
        self.assertEqual(self.quest.get_command(self.env, [1, self.FIRST_CHOICE_LINE, 7]), self.cmd_linear_give_power)
        self.assertRaises(QuestGeneratorException, self.quest.get_command, self.env, [1, self.FIRST_CHOICE_LINE, 7, 8])
        self.assertRaises(QuestGeneratorException, self.quest.get_command, self.env, [1, self.FIRST_CHOICE_LINE, 8])

        self.assertEqual(self.quest.get_command(self.env, [1, self.SECOND_CHOICE_LINE, 0]), self.cmd_quest_move)
        self.assertEqual(self.quest.get_command(self.env, [1, self.SECOND_CHOICE_LINE, 1]), self.cmd_quest_quest)
        self.assertEqual(self.quest.get_command(self.env, [1, self.SECOND_CHOICE_LINE, 1, 0]), FakeCmd('fake_event'))
        self.assertEqual(self.quest.get_command(self.env, [1, self.SECOND_CHOICE_LINE, 1, 2]), FakeCmd('fake_event'))
        self.assertEqual(self.quest.get_command(self.env, [1, self.SECOND_CHOICE_LINE, 2]), self.cmd_quest_get_reward)
        self.assertRaises(QuestGeneratorException, self.quest.get_command, self.env, [1, self.SECOND_CHOICE_LINE, 3])

    def test_get_quest(self):
        self.assertEqual(self.quest.get_quest(self.env, [0]), self.quest)
        self.assertEqual(self.quest.get_quest(self.env, [1]), self.quest)
        self.assertEqual(self.quest.get_quest(self.env, [1, self.FIRST_CHOICE_LINE, 0]), self.quest)
        self.assertEqual(self.quest.get_quest(self.env, [1, self.FIRST_CHOICE_LINE, 7]), self.quest)
        self.assertRaises(QuestGeneratorException, self.quest.get_quest, self.env, [1, self.FIRST_CHOICE_LINE, 7, 8])
        self.assertRaises(QuestGeneratorException, self.quest.get_quest, self.env, [1, self.FIRST_CHOICE_LINE, 8])

        self.assertEqual(self.quest.get_quest(self.env, [1, self.SECOND_CHOICE_LINE, 0]), self.quest)
        self.assertEqual(self.quest.get_quest(self.env, [1, self.SECOND_CHOICE_LINE, 1]), self.quest)
        self.assertEqual(self.quest.get_quest(self.env, [1, self.SECOND_CHOICE_LINE, 1, 0]), self.fake_quest)
        self.assertEqual(self.quest.get_quest(self.env, [1, self.SECOND_CHOICE_LINE, 1, 2]), self.fake_quest)
        self.assertEqual(self.quest.get_quest(self.env, [1, self.SECOND_CHOICE_LINE, 2]), self.quest)
        self.assertRaises(QuestGeneratorException, self.quest.get_quest, self.env, [1, self.SECOND_CHOICE_LINE, 3])


    def test_serialization(self):
        data = self.quest.serialize()
        quest = JustQuest()
        quest.deserialize(data)
        self.assertEqual(self.quest, quest)
