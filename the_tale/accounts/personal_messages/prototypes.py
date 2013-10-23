# coding: utf-8

from dext.utils.decorators import nested_commit_on_success

from common.utils import bbcode
from common.utils.prototypes import BasePrototype
from common.utils.decorators import lazy_property

from accounts.prototypes import AccountPrototype
from accounts.personal_messages.models import Message



class MessagePrototype(BasePrototype):
    _model_class = Message
    _readonly = ('id', 'text', 'created_at', 'recipient_id', 'sender_id', 'hide_from_sender', 'hide_from_recipient')
    _bidirectional = ()
    _get_by = ('id',)

    @property
    def text_html(self): return bbcode.render(self._model.text)

    @lazy_property
    def recipient(self): return AccountPrototype(self._model.recipient)

    @lazy_property
    def sender(self): return AccountPrototype(self._model.sender)

    @classmethod
    @nested_commit_on_success
    def create(cls, sender, recipient, text):
        from post_service.prototypes import MessagePrototype as PostServiceMessagePrototype
        from post_service.message_handlers import PersonalMessageHandler

        model = Message.objects.create(recipient=recipient._model,
                                       sender=sender._model,
                                       text=text)
        recipient.increment_new_messages_number()

        prototype = cls(model=model)

        PostServiceMessagePrototype.create(PersonalMessageHandler(message_id=prototype.id))

        return prototype

    def hide_from(self, sender=False, recipient=False):
        if sender:
            self._model.hide_from_sender = True

        if recipient:
            self._model.hide_from_recipient = True

        self._model.save()

    @classmethod
    def hide_all(cls, account_id):
        cls._model_class.objects.filter(recipient=account_id).update(hide_from_recipient=True)
        cls._model_class.objects.filter(sender=account_id).update(hide_from_sender=True)
