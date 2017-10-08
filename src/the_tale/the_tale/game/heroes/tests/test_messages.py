
import time
import collections

from the_tale.common.utils import testcase

from the_tale.game import turn

from the_tale.game.heroes import messages


class MessagesContainerTest(testcase.TestCase):

    def setUp(self):
        super(MessagesContainerTest, self).setUp()
        self.messages = messages.JournalContainer()

    def create_message(self, message, turn_delta=0, time_delta=0, position='some position info'):
        return messages.MessageSurrogate(turn_number=turn.number() + turn_delta,
                                         timestamp=time.time() + time_delta,
                                         key=None,
                                         externals=None,
                                         message=message,
                                         position=position)

    def test_create(self):
        self.assertEqual(self.messages.messages, collections.deque())

    def test_serialize(self):
        self.messages.push_message(self.create_message('1'))
        self.messages.push_message(self.create_message('2'))

        self.assertEqual(self.messages.serialize(), messages.JournalContainer.deserialize(self.messages.serialize()).serialize())

    def test_clear(self):
        self.messages.push_message(self.create_message('1'))

        self.messages.clear()

        self.assertEqual(self.messages.messages, collections.deque())

        self.messages.clear()

        self.assertEqual(self.messages.messages, collections.deque())


    def test_push_message(self):
        self.messages.push_message(self.create_message('1'))
        self.messages.push_message(self.create_message('2'))

        turn.increment()

        self.messages.push_message(self.create_message('3'))

        self.assertEqual([msg.message for msg in self.messages.messages], ['1', '2', '3'])

    def test_push_message__next_turn(self):
        self.messages.push_message(self.create_message('1'))
        self.messages.push_message(self.create_message('2', turn_delta=2))

        turn.increment()

        self.messages.push_message(self.create_message('3'))

        self.assertEqual([msg.message for msg in self.messages.messages], ['1', '3', '2'])
        self.assertEqual([msg[2] for msg in self.messages.ui_info()], ['1', '3'])

        turn.increment()

        self.assertEqual([msg.message for msg in self.messages.messages], ['1', '3', '2'])
        self.assertEqual([msg[2] for msg in self.messages.ui_info()], ['1', '3', '2'])

    def test_push_message__sort_by_time(self):
        self.messages.push_message(self.create_message('1'))
        self.messages.push_message(self.create_message('2', time_delta=-10))
        self.assertEqual([msg.message for msg in self.messages.messages], ['2', '1'])
