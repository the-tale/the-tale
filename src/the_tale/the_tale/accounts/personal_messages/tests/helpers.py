
import contextlib

from .. import logic


class Mixin(object):

    @contextlib.contextmanager
    def check_new_message(self, recipient_id, senders_ids=(), number=1):
        old_new_messages = logic.new_messages_number(recipient_id)
        yield
        self.assertEqual(logic.new_messages_number(recipient_id) - old_new_messages, number)

        total, personal_message = logic.get_received_messages(recipient_id)
        self.assertIn(recipient_id, personal_message[0].recipients_ids)

        self.assertEqual([personal_message[i].sender_id for i in range(len(senders_ids))], list(senders_ids))


    @contextlib.contextmanager
    def check_no_messages(self, recipient_id):
        old_new_messages = logic.new_messages_number(recipient_id)
        yield
        self.assertEqual(logic.new_messages_number(recipient_id), old_new_messages)
