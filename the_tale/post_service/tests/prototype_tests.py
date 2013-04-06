# coding: utf-8
import mock

from common.utils import testcase


from post_service.prototypes import MessagePrototype
from post_service.message_handlers import TestHandler
from post_service.relations import MESSAGE_STATE


class MessagePrototypeTests(testcase.TestCase):

    def setUp(self):
        super(MessagePrototypeTests, self).setUp()

    def test_create_with_now(self):
        with mock.patch('post_service.workers.environment.workers_environment.message_sender.cmd_send_now') as cmd_send_now:
            message = MessagePrototype.create(TestHandler(), now=True)
        self.assertEqual(cmd_send_now.call_args, mock.call(message.id))

    def test_create_without_now(self):
        with mock.patch('post_service.workers.environment.workers_environment.message_sender.cmd_send_now') as cmd_send_now:
            MessagePrototype.create(TestHandler())
        self.assertEqual(cmd_send_now.call_count, 0)

    def test_get_priority_message_success(self):
        message_1 = MessagePrototype.create(handler=TestHandler())
        message_2 = MessagePrototype.create(handler=TestHandler())
        message_3 = MessagePrototype.create(handler=TestHandler())
        MessagePrototype.create(handler=TestHandler())

        message_1._model.state = MESSAGE_STATE.PROCESSED
        message_1.save()

        message_2._model.state = MESSAGE_STATE.ERROR
        message_2.save()

        self.assertEqual(MessagePrototype.get_priority_message().id, message_3.id)


    def test_get_priority_message_no_messages(self):
        message_1 = MessagePrototype.create(handler=TestHandler())
        message_2 = MessagePrototype.create(handler=TestHandler())

        message_1._model.state = MESSAGE_STATE.PROCESSED
        message_1.save()

        message_2._model.state = MESSAGE_STATE.ERROR
        message_2.save()

        self.assertEqual(MessagePrototype.get_priority_message(), None)
