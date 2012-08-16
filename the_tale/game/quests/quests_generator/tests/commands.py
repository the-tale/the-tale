# coding: utf-8

from django.test import TestCase


from game.quests.quests_generator import commands


class MessageTest(TestCase):

    def test_serialization(self):
        cmd = commands.Message(event='event_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class MoveTest(TestCase):

    def test_serialization(self):
        cmd = commands.Move(event='event_1', place='place_1', break_at=0.3)
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class MoveNearTest(TestCase):

    def test_serialization(self):
        cmd = commands.MoveNear(event='event_1', place='place_1', back=True)
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))



class GetItemTest(TestCase):

    def test_serialization(self):
        cmd = commands.GetItem(event='event_1', item='item_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class GiveItemTest(TestCase):

    def test_serialization(self):
        cmd = commands.GiveItem(event='event_1', item='item_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class GetRewardTest(TestCase):

    def test_serialization(self):
        cmd = commands.GetReward(event='event_1', person='person_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class GivePowerTest(TestCase):

    def test_serialization(self):
        cmd = commands.GivePower(event='event_1', person='person_1', power=2, multiply=3, depends_on='person_2')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class ChooseTest(TestCase):

    def test_serialization(self):
        cmd = commands.Choose(event='event_1',
                              id='choice_point_1',
                              default='choice_1',
                              choices={'choice_1': [commands.GetReward(event='event_1', person='person_1')],
                                       'choice_2': [commands.GetItem(event='event_1', item='item_1')] },
                              choice='choice_marker')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class QuestTest(TestCase):

    def test_serialization(self):
        cmd = commands.Quest(event='event_1', quest='quest_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class BattleTest(TestCase):

    def test_serialization(self):
        cmd = commands.Battle(event='event_1', number=13)
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))
