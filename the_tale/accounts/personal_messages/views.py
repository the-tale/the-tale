# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.decorators import login_required

from accounts.prototypes import AccountPrototype
from accounts.logic import get_system_user

from accounts.personal_messages.models import Message
from accounts.personal_messages.prototypes import MessagePrototype
from accounts.personal_messages.forms import NewMessageForm
from accounts.personal_messages.conf import personal_messages_settings


def get_accounts_list_by_ids(ids_string):
    ids = [int(id.strip()) for id in ids_string.split(',')]
    accounts = AccountPrototype.get_list_by_id(ids)

    if len(ids) != len(accounts): return None
    return accounts

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

        if incoming:
            url_builder = UrlBuilder(reverse('accounts:messages:'), arguments={'page': page})
        else:
            url_builder = UrlBuilder(reverse('accounts:messages:sent'), arguments={'page': page})

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

    @validate_argument('recipients', get_accounts_list_by_ids, 'personal_messages', u'Неверные идентификаторы получателей')
    @validate_argument('answer_to', MessagePrototype.get_by_id, 'personal_messages', u'Неверный идентификатор сообщения')
    @handler('new', method='get')
    def new(self, recipients=[], answer_to=None):

        text = u''

        if answer_to is not None:
            if answer_to.recipient_id != self.account.id:
                return self.auto_error('personal_messages.new.not_permissions_to_answer_to', u'Вы пытаетесь ответить на чужое сообщение, а-та-та')

            if answer_to:
                text = u'[quote]\n%s\n[/quote]\n' % answer_to.text

        system_user = get_system_user()
        for recipient in recipients:
            if recipient.id == system_user.id:
                return self.auto_error('personal_messages.create.can_not_sent_message_to_system_user',
                                       u'Нельзя отправить сообщение системному пользователю')

        form = NewMessageForm(initial={'text': text})

        return self.template('personal_messages/new.html',
                             {'recipients': recipients,
                              'recipients_url_string': ','.join([str(recipient.id) for recipient in recipients]),
                              'form': form})

    @validate_argument('recipients', get_accounts_list_by_ids, 'personal_messages', u'Неверный идентификатор получателя')
    @handler('create', method='post')
    def create(self, recipients=[]):

        form = NewMessageForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('personal_messages.create.form_errors', form.errors)

        system_user = get_system_user()
        for recipient in recipients:
            if recipient.id == system_user.id:
                return self.json_error('personal_messages.create.can_not_sent_message_to_system_user',
                                       u'Нельзя отправить сообщение системному пользователю')

        for recipient in recipients:
            MessagePrototype.create(self.account, recipient, form.c.text)

        return self.json_ok()



    @handler('#message_id', 'delete', method='post')
    def delete(self):

        if self.account.id not in (self.message.sender_id, self.message.recipient_id):
            return self.auto_error('personal_messages.delete.no_permissions', u'Вы не можете влиять на это сообщение')

        self.message.hide_from(sender=(self.account.id == self.message.sender_id),
                               recipient=(self.account.id == self.message.recipient_id))

        return self.json_ok()
