# coding: utf-8
import datetime

from django.db import transaction

from the_tale.common.utils import bbcode
from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.accounts.logic import get_system_user

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.personal_messages.models import Message
from the_tale.accounts.personal_messages import conf


class MessagePrototype(BasePrototype):
    _model_class = Message
    _readonly = ('id', 'text', 'created_at', 'recipient_id', 'sender_id', 'hide_from_sender', 'hide_from_recipient')
    _bidirectional = ()
    _get_by = ('id',)

    @property
    def text_html(self): return bbcode.render(self._model.text)

    @property
    def text_safe_html(self): return bbcode.safe_render(self._model.text)

    @lazy_property
    def recipient(self): return AccountPrototype(self._model.recipient)

    @lazy_property
    def sender(self): return AccountPrototype(self._model.sender)

    @classmethod
    @transaction.atomic
    def create(cls, sender, recipient, text):
        from the_tale.post_service.prototypes import MessagePrototype as PostServiceMessagePrototype
        from the_tale.post_service.message_handlers import PersonalMessageHandler

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


    @classmethod
    def remove_old_messages(cls):
        cls._db_filter(hide_from_sender=True, hide_from_recipient=True).delete()

        system_user = get_system_user()

        cls._db_filter(recipient=system_user.id, created_at__lt=datetime.datetime.now() - conf.settings.SYSTEM_MESSAGES_LEAVE_TIME).delete()
        cls._db_filter(sender=system_user.id, created_at__lt=datetime.datetime.now() - conf.settings.SYSTEM_MESSAGES_LEAVE_TIME).delete()
