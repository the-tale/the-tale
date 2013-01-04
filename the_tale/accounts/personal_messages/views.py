# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.decorators import login_required

from accounts.prototypes import AccountPrototype

from accounts.personal_messages.models import Message
from accounts.personal_messages.prototypes import MessagePrototype
from accounts.personal_messages.forms import NewMessageForm
from accounts.personal_messages.conf import personal_messages_settings


class MessageResource(Resource):

    @login_required
    def initialize(self, message_id=None, *args, **kwargs):
        super(MessageResource, self).initialize(*args, **kwargs)

        self.message_id = message_id

    @property
    def message(self):
        if not hasattr(self, '_message'):
            self._message = MessagePrototype.get_by_id(self.message_id)
        return self._message

    def show_messages(self, query, page, incoming):

        url_builder = UrlBuilder(reverse('accounts:messages:'), arguments={'page': page})

        messages_count = query.count()

        page = int(page) - 1

        paginator = Paginator(page, messages_count, personal_messages_settings.MESSAGES_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        message_from, message_to = paginator.page_borders(page)

        messages = [ MessagePrototype(message_model) for message_model in query.order_by('-created_at')[message_from:message_to]]

        return self.template('personal_messages/index.html',
                             {'messages': messages,
                              'paginator': paginator,
                              'incoming': incoming})


    @handler('', method='get')
    def index(self, page=1):
        self.account.reset_new_messages_number()
        return self.show_messages(Message.objects.filter(recipient_id=self.account.id, hide_from_recipient=False),
                                  page,
                                  True)

    @handler('sent', method='get')
    def sent(self, page=1):
        return self.show_messages(Message.objects.filter(sender_id=self.account.id, hide_from_sender=False),
                                  page,
                                  False)

    @handler('new', method='get')
    def new(self, recipient, answer_to=None):

        try:
            recipient = int(recipient)
        except ValueError:
            return self.auto_error('personal_messages.new.wrong_recipient_id', u'Неверный идентификатор получателя', status_code=404)

        recipient = AccountPrototype.get_by_id(int(recipient))

        if recipient is None:
            return self.auto_error('personal_messages.new.recipient_not_found', u'Получатель не найден', status_code=404)

        text = u''
        if answer_to is not None:
            try:
                answer_to = int(answer_to)
            except:
                return self.auto_error('personal_messages.new.wrong_answer_id', u'Неверный идентификатор сообщения', status_code=404)

            parent_message = MessagePrototype.get_by_id(int(answer_to))

            if parent_message is None:
                return self.auto_error('personal_messages.new.message_not_found', u'Сообщение не найдено', status_code=404)

            if parent_message.recipient_id != self.account.id:
                return self.auto_error('personal_messages.new.not_permissions_to_answer_to', u'Вы пытаетесь ответить на чужое сообщние, а-та-та')

            if parent_message:
                text = u'[quote]\n%s\n[/quote]\n' % parent_message.text

        form = NewMessageForm(initial={'text': text})

        return self.template('personal_messages/new.html',
                             {'recipient': recipient,
                              'form': form})

    @handler('create', method='post')
    def create(self, recipient):

        try:
            recipient = int(recipient)
        except ValueError:
            return self.auto_error('personal_messages.create.wrong_recipient_id', u'Неверный идентификатор получателя', status_code=404)


        recipient = AccountPrototype.get_by_id(int(recipient))

        if recipient is None:
            return self.auto_error('personal_messages.create.recipient_not_found', u'Получатель не найден', status_code=404)

        form = NewMessageForm(self.request.POST)

        if form.is_valid():
            MessagePrototype.create(self.account, recipient, form.c.text)
            return self.json_ok()

        return self.json_error('personal_messages.create.form_errors', form.errors)

    @handler('#message_id', 'delete', method='post')
    def delete(self):

        if self.account.id not in (self.message.sender_id, self.message.recipient_id):
            return self.auto_error('personal_messages.delete.no_permissions', u'Вы не можете влиять на это сообщение')

        self.message.hide_from(sender=(self.account.id == self.message.sender_id),
                               recipient=(self.account.id == self.message.recipient_id))

        return self.json_ok()
