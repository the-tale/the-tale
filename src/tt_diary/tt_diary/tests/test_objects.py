
import time
import unittest

from tt_diary import objects

from . import helpers


class MessageTests(unittest.TestCase):

    def setUp(self):
        super(MessageTests, self).setUp()

        self.message = objects.Message(timestamp=time.time(),
                                       turn_number=1,
                                       type=2,
                                       game_time='213',
                                       game_date='das',
                                       position='some position',
                                       message='bla-bla-message',
                                       variables={'x': 'y', 'z': 1})


    def test_serialization(self):
        self.assertEqual(self.message, objects.Message.deserialize(self.message.serialize()))



class DiaryTests(unittest.TestCase):

    def setUp(self):
        super(DiaryTests, self).setUp()

        self.diary = objects.Diary()


    def test_push_message(self):
        self.assertEqual(self.diary.version, 0)

        message = helpers.create_message()
        self.diary.push_message(message)

        self.assertEqual(self.diary.version, 1)

        self.assertEqual(list(self.diary.messages()), [message])


    def test_push_message__limit(self):
        for i in range(21):
            self.diary.push_message(helpers.create_message(turn_number=i), diary_size=20)

        self.assertEqual(self.diary.version, 21)

        self.assertEqual(set(message.turn_number for message in self.diary.messages()), set(range(1, 21)))


    def test_push_message__sort(self):

        self.diary.push_message(helpers.create_message(turn_number=10, timestamp=100, message='10_100'))
        self.diary.push_message(helpers.create_message(turn_number=7, timestamp=101, message='7_101'))
        self.diary.push_message(helpers.create_message(turn_number=9, timestamp=100, message='9_100'))
        self.diary.push_message(helpers.create_message(turn_number=8, timestamp=99, message='8_99'))
        self.diary.push_message(helpers.create_message(turn_number=1, timestamp=1, message='1_1'))

        self.assertEqual(list(message.message for message in self.diary.messages()),
                         ['1_1', '7_101', '8_99', '9_100', '10_100'])
