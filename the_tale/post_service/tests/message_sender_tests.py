# coding: utf-8

from dext.settings import settings

from common.utils import testcase


from post_service.prototypes import MessagePrototype
from post_service.conf import post_service_settings
from post_service.message_handlers import TestHandler
from post_service.workers.environment import workers_environment as post_service_workers_environment


class MessageSenderTests(testcase.TestCase):

    def setUp(self):
        super(MessageSenderTests, self).setUp()
        self.message = MessagePrototype.create(TestHandler())

        post_service_workers_environment.deinitialize()
        post_service_workers_environment.initialize()

        self.worker = post_service_workers_environment.message_sender

    def test_send_message_skipped(self):
        self.worker.send_message(self.message)
        self.assertTrue(self.message.state._is_SKIPPED)

    def test_send_message_processed(self):
        settings[post_service_settings.SETTINGS_ALLOWED_KEY] = 'allowed'
        self.worker.send_message(self.message)
        self.assertTrue(self.message.state._is_PROCESSED)

    def test_send_message_forces_process(self):
        settings[post_service_settings.SETTINGS_FORCE_ALLOWED_KEY] = TestHandler().settings_type_uid
        self.worker.send_message(self.message)
        self.assertTrue(self.message.state._is_PROCESSED)
