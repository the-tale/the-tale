# coding: utf-8

from common.utils import testcase


from game.quests.quests_generator import commands


class MessageTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.Message(event='event_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class DoNothingTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.DoNothing(event='event_1', duration=13, messages_probability=0.3)
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class UpgradeEquipmentTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.UpgradeEquipment(event='event_1', equipment_slot='slot_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class MoveTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.Move(event='event_1', place='place_1', break_at=0.3)
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class MoveNearTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.MoveNear(event='event_1', place='place_1', back=True)
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))



class GetItemTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.GetItem(event='event_1', item='item_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class GiveItemTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.GiveItem(event='event_1', item='item_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class GetRewardTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.GetReward(event='event_1', person='person_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class QuestResultTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.QuestResult(event='event_1', result='success')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class GivePowerTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.GivePower(event='event_1', person='person_1', power=2)
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class ChooseTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.Choose(event='event_1',
                              id='choice_point_1',
                              default='choice_1',
                              choices={'choice_1': 'line_1',
                                       'choice_2': 'line_2' },
                              choice='choice_marker')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))

class SwitchTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.Switch(event='event_1',
                              choices=[ (('quest_1', 'result_1'), 'line_1'),
                                        (('quest_1', 'result_2'), 'line_2') ] )
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))

    # def test_no_default_choice(self):
    #     self.assertRaises(QuestGeneratorException,
    #                       commands.Switch,
    #                       event='event_1',
    #                       choices=[ (('quest_1', 'result_1'), 'line_1'),
    #                                 (('quest_1', 'result_2'), 'line_2') ] )

    # def test_default_choice_in_middle(self):
    #     self.assertRaises(QuestGeneratorException,
    #                       commands.Switch,
    #                       event='event_1',
    #                       choices=[ (('quest_1', 'result_1'), 'line_1'),
    #                                 (None, 'line_2'),
    #                                 (('quest_1', 'result_2'), 'line_3'),
    #                                 (None, 'line_4') ] )


class QuestTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.Quest(event='event_1', quest='quest_1')
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))


class BattleTest(testcase.TestCase):

    def test_serialization(self):
        cmd = commands.Battle(event='event_1', number=13)
        data = cmd.serialize()
        self.assertEqual(cmd, commands.deserialize_command(data))
