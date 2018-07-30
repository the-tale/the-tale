
import smart_imports

smart_imports.all()


class MessagePrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(MessagePrototypeTests, self).setUp()

    def test_create_with_now(self):
        with mock.patch('the_tale.post_service.workers.message_sender.Worker.cmd_send_now') as cmd_send_now:
            message = prototypes.MessagePrototype.create(message_handlers.TestHandler(), now=True)
        self.assertEqual(cmd_send_now.call_args, mock.call(message.id))

    def test_create_without_now(self):
        with mock.patch('the_tale.post_service.workers.message_sender.Worker.cmd_send_now') as cmd_send_now:
            prototypes.MessagePrototype.create(message_handlers.TestHandler())
        self.assertEqual(cmd_send_now.call_count, 0)

    def test_get_priority_message_success(self):
        message_1 = prototypes.MessagePrototype.create(handler=message_handlers.TestHandler())
        message_2 = prototypes.MessagePrototype.create(handler=message_handlers.TestHandler())
        message_3 = prototypes.MessagePrototype.create(handler=message_handlers.TestHandler())
        prototypes.MessagePrototype.create(handler=message_handlers.TestHandler())

        message_1._model.state = relations.MESSAGE_STATE.PROCESSED
        message_1.save()

        message_2._model.state = relations.MESSAGE_STATE.ERROR
        message_2.save()

        self.assertEqual(prototypes.MessagePrototype.get_priority_message().id, message_3.id)

    def test_get_priority_message_no_messages(self):
        message_1 = prototypes.MessagePrototype.create(handler=message_handlers.TestHandler())
        message_2 = prototypes.MessagePrototype.create(handler=message_handlers.TestHandler())

        message_1._model.state = relations.MESSAGE_STATE.PROCESSED
        message_1.save()

        message_2._model.state = relations.MESSAGE_STATE.ERROR
        message_2.save()

        self.assertEqual(prototypes.MessagePrototype.get_priority_message(), None)

    def test_remove_old_messages(self):
        message_1 = prototypes.MessagePrototype.create(handler=message_handlers.TestHandler())
        message_1._model.state = relations.MESSAGE_STATE.PROCESSED
        message_1.save()

        message_2 = prototypes.MessagePrototype.create(handler=message_handlers.TestHandler())
        message_2._model.created_at -= datetime.timedelta(seconds=conf.settings.MESSAGE_LIVE_TIME)
        message_2._model.state = relations.MESSAGE_STATE.PROCESSED
        message_2.save()

        message_3 = prototypes.MessagePrototype.create(handler=message_handlers.TestHandler())
        message_3._model.created_at -= datetime.timedelta(seconds=conf.settings.MESSAGE_LIVE_TIME)
        message_3.save()

        prototypes.MessagePrototype.remove_old_messages()

        self.assertEqual(prototypes.MessagePrototype._db_count(), 2)
        self.assertEqual(prototypes.MessagePrototype._db_get_object(0).id, message_1.id)
        self.assertEqual(prototypes.MessagePrototype._db_get_object(1).id, message_3.id)
