# coding: utf-8
import time
import collections

from the_tale.common.utils import testcase

from the_tale.game.prototypes import TimePrototype

from the_tale.game.heroes import messages


class MessagesContainerTest(testcase.TestCase):

    def setUp(self):
        super(MessagesContainerTest, self).setUp()
        self.messages = messages.JournalContainer()

    def create_message(self, message, turn_delta=0, time_delta=0, position=u'some position info'):
        return messages.MessageSurrogate(turn_number=TimePrototype.get_current_turn_number() + turn_delta,
                                         timestamp=time.time() + time_delta,
                                         key=None,
                                         externals=None,
                                         message=message,
                                         position=position)

    def test_create(self):
        self.assertEqual(self.messages.messages, collections.deque())
        self.assertFalse(self.messages.updated)

    def test_serialize(self):
        self.messages.push_message(self.create_message('1'))
        self.messages.push_message(self.create_message('2'))

        self.assertEqual(self.messages.serialize(), messages.JournalContainer.deserialize(self.messages.serialize()).serialize())

    def test_clear(self):
        self.messages.push_message(self.create_message('1'))

        self.messages.updated = False

        self.messages.clear()

        self.assertTrue(self.messages.updated)
        self.assertEqual(self.messages.messages, collections.deque())

        self.messages.updated = False

        self.messages.clear()

        self.assertFalse(self.messages.updated)
        self.assertEqual(self.messages.messages, collections.deque())


    def test_push_message(self):
        current_time = TimePrototype.get_current_time()

        self.messages.push_message(self.create_message('1'))
        self.messages.push_message(self.create_message('2'))

        current_time.increment_turn()

        self.messages.push_message(self.create_message('3'))

        self.assertEqual([msg.message for msg in self.messages.messages], ['1', '2', '3'])

    def test_push_message__next_turn(self):
        current_time = TimePrototype.get_current_time()

        self.messages.push_message(self.create_message('1'))
        self.messages.push_message(self.create_message('2', turn_delta=2))

        current_time.increment_turn()

        self.messages.push_message(self.create_message('3'))

        self.assertEqual([msg.message for msg in self.messages.messages], ['1', '3', '2'])
        self.assertEqual([msg[2] for msg in self.messages.ui_info()], ['1', '3'])

        current_time.increment_turn()

        self.assertEqual([msg.message for msg in self.messages.messages], ['1', '3', '2'])
        self.assertEqual([msg[2] for msg in self.messages.ui_info()], ['1', '3', '2'])

    def test_push_message__sort_by_time(self):
        self.messages.push_message(self.create_message(u'1'))
        self.messages.push_message(self.create_message(u'2', time_delta=-10))
        self.assertEqual([msg.message for msg in self.messages.messages], ['2', '1'])
