# coding: utf-8

from common.utils import testcase


from post_service.prototypes import MessagePrototype
from post_service.message_handlers import TestHandler
from post_service.relations import MESSAGE_STATE


class MessagePrototypeTests(testcase.TestCase):

    def setUp(self):
        super(MessagePrototypeTests, self).setUp()


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
