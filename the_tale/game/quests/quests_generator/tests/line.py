# coding: utf-8

from django.test import TestCase

from game.quests.quests_generator.quest_line import Line
from game.quests.quests_generator import commands as cmd
from game.quests.quests_generator.environment import BaseEnvironment, LocalEnvironment
from game.quests.quests_generator.quests_source import BaseQuestsSource
from game.quests.quests_generator.knowlege_base import KnowlegeBase
from game.quests.quests_generator.exceptions import QuestGeneratorException
from game.quests.quests_generator.tests.helpers import FakeQuest

quests_source = BaseQuestsSource()
writers_constructor = lambda hero, quest_type, env, quest_env_local: 0


class LineTest(TestCase):

    def setUp(self):
        self.knowlege_base = KnowlegeBase()

        self.env = BaseEnvironment(quests_source=quests_source, writers_constructor=writers_constructor, knowlege_base=self.knowlege_base)
        self.env.quests['quest_1'] = FakeQuest(commands_number=13)

        self.env_local = LocalEnvironment()
        self.env_local.register('quest_1', 'quest_1')

        self.empty_line = Line(sequence=[])
        self.linear_line = Line(sequence=[cmd.Move(event='event_1_1', place='place_1'),
                                          cmd.MoveNear(event='event_1_2', place='place_1', back=False),
                                          cmd.MoveNear(event='event_1_3', place='place_1', back=True),
                                          cmd.GetItem(event='event_1_4', item='item_1'),
                                          cmd.GiveItem(event='event_1_5', item='item_1'),
                                          cmd.Battle(event='event_1_6', number=13),
                                          cmd.GetReward(event='event_1_7', person='person_1'),
                                          cmd.GivePower(event='event_1_8', person='person_1', power=2, multiply=3, depends_on='person_2')  ])
        self.linear_line.available = True

        self.quest_line = Line(sequence=[cmd.Move(event='event_2_1', place='place_2'),
                                          cmd.Quest(event='event_2_2', quest=self.env_local.quest_1),
                                          cmd.GetReward(event='event_2_3', person='person_2')  ])
        self.quest_line.available = True

        self.choice_line = Line(sequence=[cmd.Move(event='event_3_1', place='place_3'),
                                          cmd.Choose(id='choose_1',
                                                     default='choice_1',
                                                     choices={'choice_1': self.env.new_line(self.linear_line),
                                                              'choice_2': self.env.new_line(self.quest_line) },
                                                     event='event_3_2',
                                                     choice='choice_id_1'),
                                          cmd.Battle(event='event_3_3', number=13),                                            ])
        self.choice_line.available = True

    def test_start_pointer(self):
        self.assertEqual(self.empty_line.get_start_pointer(), [0])
        self.assertEqual(self.linear_line.get_start_pointer(), [0])


    def test_get_commands_number(self):
        self.assertEqual(self.linear_line.get_commands_number(self.env), 8)
        self.assertEqual(self.linear_line.get_commands_number(self.env, pointer=[1]), 1)
        self.assertEqual(self.linear_line.get_commands_number(self.env, pointer=[7]), 7)
        self.assertRaises(QuestGeneratorException, self.linear_line.get_commands_number, self.env, pointer=[9])

        self.assertEqual(self.quest_line.get_commands_number(self.env), 16)
        self.assertEqual(self.quest_line.get_commands_number(self.env, pointer=[1]), 1)
        self.assertEqual(self.quest_line.get_commands_number(self.env, [1, 0]), 2)
        self.assertEqual(self.quest_line.get_commands_number(self.env, [1, 5]), 7)
        self.assertEqual(self.quest_line.get_commands_number(self.env, [1, 12]), 14)
        self.assertEqual(self.quest_line.get_commands_number(self.env, pointer=[2]), 15)
        self.assertRaises(QuestGeneratorException, self.quest_line.get_commands_number, self.env, pointer=[9])

        self.assertEqual(self.choice_line.get_commands_number(self.env), 19)
        self.assertEqual(self.choice_line.get_commands_number(self.env, pointer=[1]), 1)
        self.assertEqual(self.choice_line.get_commands_number(self.env, [1, 'line_1', 0]), 2)
        self.assertEqual(self.choice_line.get_commands_number(self.env, [1, 'line_1', 7]), 9)
        self.assertEqual(self.choice_line.get_commands_number(self.env, [1, 'line_2', 0]), 2)
        self.assertEqual(self.choice_line.get_commands_number(self.env, [1, 'line_2', 2]), 17)
        self.assertEqual(self.choice_line.get_commands_number(self.env, pointer=[2]), 18)
        self.assertRaises(QuestGeneratorException, self.choice_line.get_commands_number, self.env, pointer=[9])


    def test_increment_pointer(self):
        self.assertEqual(self.linear_line.increment_pointer(self.env, [0], {}), [1])
        self.assertEqual(self.linear_line.increment_pointer(self.env, [5], {}), [6])
        self.assertEqual(self.linear_line.increment_pointer(self.env, [7], {}), None)
        self.assertRaises(QuestGeneratorException, self.linear_line.increment_pointer, self.env, [8], {})

        self.assertEqual(self.quest_line.increment_pointer(self.env, [0], {}), [1])
        self.assertEqual(self.quest_line.increment_pointer(self.env, [1], {}), [1, 0])
        self.assertEqual(self.quest_line.increment_pointer(self.env, [1, 0], {}), [1, 1])
        self.assertEqual(self.quest_line.increment_pointer(self.env, [1, 5], {}), [1, 6])
        self.assertEqual(self.quest_line.increment_pointer(self.env, [1, 12], {}), [2])
        self.assertEqual(self.quest_line.increment_pointer(self.env, [2], {}), None)
        self.assertRaises(QuestGeneratorException, self.quest_line.increment_pointer, self.env, [8], {})

        self.assertEqual(self.choice_line.increment_pointer(self.env, [0], {}), [1])

        # check choice availability
        self.linear_line.available = False
        self.quest_line.available = False
        self.assertRaises(QuestGeneratorException, self.choice_line.increment_pointer, self.env, [1], {})
        self.linear_line.available = True
        self.quest_line.available = False
        self.assertRaises(QuestGeneratorException, self.choice_line.increment_pointer, self.env, [1], {'choose_1': 'choice_2'})
        self.linear_line.available = False
        self.quest_line.available = True
        self.assertEqual(self.choice_line.increment_pointer(self.env, [1, 'line_2', 0], {'choose_1': 'choice_2'}), [1, 'line_2', 1])
        self.linear_line.available = True
        self.quest_line.available = True

        # continue checking increment
        self.assertTrue(self.choice_line.increment_pointer(self.env, [1], {}) in ([1, 'line_1', 0], [1, 'line_2', 0]))
        self.assertEqual(self.choice_line.increment_pointer(self.env, [1, 'line_1', 0], {}), [1, 'line_1', 1])
        self.assertEqual(self.choice_line.increment_pointer(self.env, [1, 'line_1', 7], {}), [2])
        self.assertEqual(self.choice_line.increment_pointer(self.env, [1], {'choose_1': 'choice_2'}), [1, 'line_2', 0])
        self.assertEqual(self.choice_line.increment_pointer(self.env, [1, 'line_2', 0], {'choose_1': 'choice_2'}), [1, 'line_2', 1])
        self.assertEqual(self.choice_line.increment_pointer(self.env, [1, 'line_2', 2], {'choose_1': 'choice_2'}), [2])
        self.assertEqual(self.choice_line.increment_pointer(self.env, [2], {}), None)
        self.assertRaises(QuestGeneratorException, self.choice_line.increment_pointer, self.env, [3], {})


    def test_get_quest_command(self):

        cmd_linear_move = cmd.Move(event='event_1_1', place='place_1')
        cmd_linear_battle = cmd.Battle(event='event_1_6', number=13)
        cmd_linear_give_power = cmd.GivePower(event='event_1_8', person='person_1', power=2, multiply=3, depends_on='person_2')

        self.assertEqual(self.linear_line.get_quest_command(self.env, [0]), (cmd_linear_move, [], []))
        self.assertEqual(self.linear_line.get_quest_command(self.env, [5]), (cmd_linear_battle, [], []))
        self.assertRaises(QuestGeneratorException, self.linear_line.get_quest_command, self.env, [8], [])

        cmd_quest_move = cmd.Move(event='event_2_1', place='place_2')
        cmd_quest_quest = cmd.Quest(event='event_2_2', quest=self.env_local.quest_1)
        cmd_quest_get_reward = cmd.GetReward(event='event_2_3', person='person_2')

        self.assertEqual(self.quest_line.get_quest_command(self.env, [0]), (cmd_quest_move, [], []))
        self.assertEqual(self.quest_line.get_quest_command(self.env, [1]), (cmd_quest_quest, [], []))
        self.assertEqual(self.quest_line.get_quest_command(self.env, [1, 0]), (cmd_quest_quest, [], [0]))
        self.assertEqual(self.quest_line.get_quest_command(self.env, [1, 3]), (cmd_quest_quest, [], [3]))
        self.assertEqual(self.quest_line.get_quest_command(self.env, [2]), (cmd_quest_get_reward, [], []))
        self.assertRaises(QuestGeneratorException, self.quest_line.get_quest_command, self.env, [3])

        cmd_move = cmd.Move(event='event_3_1', place='place_3')
        cmd_choose = cmd.Choose(id='choose_1',
                                default='choice_1',
                                choices={'choice_1': 'line_1',
                                         'choice_2': 'line_2' },
                                event='event_3_2',
                                choice='choice_id_1')

        self.assertEqual(self.choice_line.get_quest_command(self.env, [0]), (cmd_move, [], []))
        self.assertEqual(self.choice_line.get_quest_command(self.env, [1]), (cmd_choose, [], []))
        self.assertEqual(self.choice_line.get_quest_command(self.env, [1, 'line_1', 0]), (cmd_linear_move, [('choice_id_1', 'choice_1')], []))
        self.assertEqual(self.choice_line.get_quest_command(self.env, [1, 'line_1', 7]), (cmd_linear_give_power, [('choice_id_1', 'choice_1')], []))
        self.assertEqual(self.choice_line.get_quest_command(self.env, [1, 'line_1', 7, 8]), (cmd_linear_give_power, [('choice_id_1', 'choice_1')], [8]))
        self.assertRaises(QuestGeneratorException, self.choice_line.get_quest_command, self.env, [1, 'line_1', 8])
        self.assertEqual(self.choice_line.get_quest_command(self.env, [1, 'line_2', 0]), (cmd_quest_move, [('choice_id_1', 'choice_2')], []))
        self.assertEqual(self.choice_line.get_quest_command(self.env, [1, 'line_2', 1]), (cmd_quest_quest, [('choice_id_1', 'choice_2')], []))
        self.assertEqual(self.choice_line.get_quest_command(self.env, [1, 'line_2', 1, 0]), (cmd_quest_quest, [('choice_id_1', 'choice_2')], [0]))
        self.assertEqual(self.choice_line.get_quest_command(self.env, [1, 'line_2', 1, 2]), (cmd_quest_quest, [('choice_id_1', 'choice_2')], [2]))
        self.assertEqual(self.choice_line.get_quest_command(self.env, [1, 'line_2', 2]), (cmd_quest_get_reward, [('choice_id_1', 'choice_2')], []))
        self.assertRaises(QuestGeneratorException, self.choice_line.get_quest_command, self.env, [1, 'line_2', 3])


    def test_serialization(self):
        data = self.linear_line.serialize()
        line = Line()
        line.deserialize(data)
        self.assertEqual(self.linear_line, line)

        data = self.quest_line.serialize()
        line = Line()
        line.deserialize(data)
        self.assertEqual(self.quest_line, line)

        data = self.choice_line.serialize()
        line = Line()
        line.deserialize(data)
        self.assertEqual(self.choice_line, line)
