
import json

from django.core.management.base import BaseCommand

from the_tale.accounts.personal_messages import models


class ConversationKey(object):
    __slots__ = ('id_min', 'id_max')

    def __init__(self, id_min, id_max):
        self.id_min = min(id_min, id_max)
        self.id_max = max(id_min, id_max)


    def value(self):
        return (self.id_min << 32) + self.id_max


    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.id_min == other.id_min and
                self.id_max == other.id_max)


    def __ne__(self, other):
        return not self.__eq__(other)



class Command(BaseCommand):

    help = 'dump old table to json'

    requires_model_validation = False

    def handle(self, *args, **options):
        messages = []
        accounts = {}
        conversations = []
        visibilities = []

        for message in models.Message.objects.all().order_by('created_at').iterator():
            if message.sender_id == message.recipient_id:
                continue

            if message.recipient_id not in accounts:
                accounts[message.recipient_id] = {'id': message.recipient_id,
                                                  'created_at': message.created_at.timestamp(),
                                                  'contacts_ids': set()}

            if message.sender_id not in accounts:
                accounts[message.sender_id] = {'id': message.sender_id,
                                               'created_at': message.created_at.timestamp(),
                                               'contacts_ids': set()}

            messages.append({'body': message.text,
                             'created_at': message.created_at.timestamp(),
                             'sender_id': message.sender_id,
                             'recipients_ids': []})

            message_id = len(messages) - 1

            messages[message_id]['recipients_ids'].append(message.recipient_id)

            accounts[message.sender_id]['contacts_ids'].add(message.recipient_id)
            accounts[message.recipient_id]['contacts_ids'].add(message.sender_id)

            visibilities.append({'message_id': message_id+1,
                                 'account_id': message.sender_id,
                                 'created_at': message.created_at.timestamp(),
                                 'visible': not message.hide_from_sender})

            visibilities.append({'message_id': message_id+1,
                                 'account_id': message.recipient_id,
                                 'created_at': message.created_at.timestamp(),
                                 'visible': not message.hide_from_recipient})

            conversations.append({'message_id': message_id+1,
                                  'account_1': min(message.sender_id, message.recipient_id),
                                  'account_2': max(message.sender_id, message.recipient_id),
                                  'created_at': message.created_at.timestamp()})

        for account in accounts.values():
            account['contacts_ids'] = list(account['contacts_ids'])

        print(json.dumps({'accounts': accounts,
                          'messages': messages,
                          'visibilities': visibilities,
                          'conversations': conversations}, ensure_ascii=False))
