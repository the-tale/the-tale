# coding: utf-8

import postmarkup

from dext.utils.decorators import nested_commit_on_success

from accounts.prototypes import AccountPrototype
from accounts.personal_messages.models import Message



class MessagePrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(Message.objects.get(id=id_))
        except:
            return None

    @property
    def id(self): return self.model.id

    @property
    def text(self): return self.model.text

    @property
    def text_html(self): return postmarkup.render_bbcode(self.model.text)

    @property
    def created_at(self): return self.model.created_at

    @property
    def recipient_id(self): return self.model.recipient_id

    @property
    def sender_id(self): return self.model.sender_id

    @property
    def recipient(self): return AccountPrototype(self.model.recipient)

    @property
    def sender(self): return AccountPrototype(self.model.sender)

    @property
    def hide_from_sender(self): return self.model.hide_from_sender

    @property
    def hide_from_recipient(self): return self.model.hide_from_recipient


    @classmethod
    @nested_commit_on_success
    def create(cls, sender, recipient, text):

        model = Message.objects.create(recipient=recipient.model,
                                       sender=sender.model,
                                       text=text)
        recipient.increment_new_messages_number()

        return cls(model)

    def hide_from(self, sender=False, recipient=False):
        if sender:
            self.model.hide_from_sender = True

        if recipient:
            self.model.hide_from_recipient = True

        self.model.save()
