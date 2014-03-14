# coding: utf-8
import datetime

from the_tale.common.utils import testcase

from the_tale.game.prototypes import TimePrototype

from the_tale.game.heroes import messages


class MessagesContainerTest(testcase.TestCase):

    def setUp(self):
        super(MessagesContainerTest, self).setUp()
        self.messages = messages.JournalContainer()

    def test_create(self):
        self.assertEqual(self.messages.messages, [])
        self.assertFalse(self.messages.updated)

    def test_serialize(self):
        self.messages.push_message(messages.prepair_message('1'))
        self.messages.push_message(messages.prepair_message('2'))

        self.assertEqual(self.messages.serialize(), messages.JournalContainer.deserialize(None ,self.messages.serialize()).serialize())

    def test_clear(self):
        self.messages.push_message(messages.prepair_message('1'))

        self.messages.updated = False

        self.messages.clear()

        self.assertTrue(self.messages.updated)
        self.assertEqual(self.messages.messages, [])

        self.messages.updated = False

        self.messages.clear()

        self.assertFalse(self.messages.updated)
        self.assertEqual(self.messages.messages, [])


    def test_push_message(self):
        current_time = TimePrototype.get_current_time()

        self.messages.push_message(messages.prepair_message('1'))
        self.messages.push_message(messages.prepair_message('2'))

        current_time.increment_turn()

        self.messages.push_message(messages.prepair_message('3'))

        self.assertEqual([msg[2] for msg in self.messages.messages], ['1', '2', '3'])

    def test_push_message__next_turn(self):
        current_time = TimePrototype.get_current_time()

        self.messages.push_message(messages.prepair_message('1'))
        self.messages.push_message(messages.prepair_message('2', turn_delta=2))

        current_time.increment_turn()

        self.messages.push_message(messages.prepair_message('3'))

        self.assertEqual([msg[2] for msg in self.messages.messages], ['1', '3', '2'])
        self.assertEqual([msg[2] for msg in self.messages.ui_info()], ['1', '3'])

        current_time.increment_turn()

        self.assertEqual([msg[2] for msg in self.messages.messages], ['1', '3', '2'])
        self.assertEqual([msg[2] for msg in self.messages.ui_info()], ['1', '3', '2'])

    def test_push_message__sort_by_time(self):
        self.messages.push_message((0, datetime.datetime.now(), u'1'))
        self.messages.push_message((0, datetime.datetime.now()-datetime.timedelta(seconds=1), u'2'))
        self.assertEqual([msg[2] for msg in self.messages.messages], ['2', '1'])
