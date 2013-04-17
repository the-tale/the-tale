# coding: utf-8

from common.utils import testcase

from game.prototypes import TimePrototype

from game.heroes.messages import MessagesContainer


class MessagesContainerTest(testcase.TestCase):

    def setUp(self):
        super(MessagesContainerTest, self).setUp()
        self.messages = MessagesContainer()

    def test_create(self):
        self.assertEqual(self.messages.messages, [])
        self.assertFalse(self.messages.updated)

    def test_serialize(self):
        self.messages.push_message(MessagesContainer._prepair_message('1'))
        self.messages.push_message(MessagesContainer._prepair_message('2'))

        self.assertEqual(self.messages.serialize(), MessagesContainer.deserialize(self.messages.serialize()).serialize())

    def test_push_message(self):
        current_time = TimePrototype.get_current_time()

        self.messages.push_message(MessagesContainer._prepair_message('1'))
        self.messages.push_message(MessagesContainer._prepair_message('2'))

        current_time.increment_turn()

        self.messages.push_message(MessagesContainer._prepair_message('3'))

        self.assertEqual([msg[2] for msg in self.messages.messages], ['1', '2', '3'])

    def test_push_message__next_turn(self):
        current_time = TimePrototype.get_current_time()

        self.messages.push_message(MessagesContainer._prepair_message('1'))
        self.messages.push_message(MessagesContainer._prepair_message('2', turn_delta=2))

        current_time.increment_turn()

        self.messages.push_message(MessagesContainer._prepair_message('3'))

        self.assertEqual([msg[2] for msg in self.messages.messages], ['1', '3', '2'])
        self.assertEqual([msg[2] for msg in self.messages.ui_info()], ['1', '3'])

        current_time.increment_turn()

        self.assertEqual([msg[2] for msg in self.messages.messages], ['1', '3', '2'])
        self.assertEqual([msg[2] for msg in self.messages.ui_info()], ['1', '3', '2'])
