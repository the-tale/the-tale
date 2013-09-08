# coding: utf-8
import datetime

import mock

from common.utils import testcase


from post_service.prototypes import MessagePrototype
from post_service.message_handlers import TestHandler
from post_service.relations import MESSAGE_STATE
from post_service.conf import post_service_settings


class MessagePrototypeTests(testcase.TestCase):

    def setUp(self):
        super(MessagePrototypeTests, self).setUp()

    def test_create_with_now(self):
        with mock.patch('post_service.workers.message_sender.Worker.cmd_send_now') as cmd_send_now:
            message = MessagePrototype.create(TestHandler(), now=True)
        self.assertEqual(cmd_send_now.call_args, mock.call(message.id))

    def test_create_without_now(self):
        with mock.patch('post_service.workers.message_sender.Worker.cmd_send_now') as cmd_send_now:
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

    def test_remove_old_messages(self):
        message_1 = MessagePrototype.create(handler=TestHandler())
        message_1._model.state = MESSAGE_STATE.PROCESSED
        message_1.save()

        message_2 = MessagePrototype.create(handler=TestHandler())
        message_2._model.created_at -= datetime.timedelta(seconds=post_service_settings.MESSAGE_LIVE_TIME)
        message_2._model.state = MESSAGE_STATE.PROCESSED
        message_2.save()

        message_3 = MessagePrototype.create(handler=TestHandler())
        message_3._model.created_at -= datetime.timedelta(seconds=post_service_settings.MESSAGE_LIVE_TIME)
        message_3.save()

        MessagePrototype.remove_old_messages()

        self.assertEqual(MessagePrototype._db_count(), 2)
        self.assertEqual(MessagePrototype._db_get_object(0).id, message_1.id)
        self.assertEqual(MessagePrototype._db_get_object(1).id, message_3.id)
