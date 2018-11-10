
import smart_imports

smart_imports.all()


@mock.patch('the_tale.post_service.conf.settings.ENABLE_MESSAGE_SENDER', True)
class MessageSenderTests(utils_testcase.TestCase):

    def setUp(self):
        super(MessageSenderTests, self).setUp()
        self.message = prototypes.MessagePrototype.create(message_handlers.TestHandler())

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.worker = amqp_environment.environment.workers.message_sender

    def test_send_message_skipped(self):
        self.worker.send_message(self.message)
        self.assertTrue(self.message.state.is_SKIPPED)

    def test_send_message_processed(self):
        dext_settings.settings[conf.settings.SETTINGS_ALLOWED_KEY] = 'allowed'
        self.worker.send_message(self.message)
        self.assertTrue(self.message.state.is_PROCESSED)

    def test_send_message_forces_process(self):
        dext_settings.settings[conf.settings.SETTINGS_FORCE_ALLOWED_KEY] = message_handlers.TestHandler().settings_type_uid
        self.worker.send_message(self.message)
        self.assertTrue(self.message.state.is_PROCESSED)
