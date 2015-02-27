# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument
from dext.common.utils.urls import UrlBuilder

from the_tale import amqp_environment

from the_tale.common.postponed_tasks import PostponedTaskPrototype
from the_tale.common.utils.resources import Resource
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils.decorators import login_required

from the_tale.accounts import prototypes as accounts_prototypes
from the_tale.accounts import views as accounts_views
from the_tale.accounts import models as accounts_models
from the_tale.accounts import logic as accounts_logic

from the_tale.accounts.personal_messages import models
from the_tale.accounts.personal_messages import prototypes
from the_tale.accounts.personal_messages import forms
from the_tale.accounts.personal_messages import conf
from the_tale.accounts.personal_messages import postponed_tasks



class MessageResource(Resource):

    @login_required
    @accounts_views.validate_fast_account()
    def initialize(self, message_id=None, *args, **kwargs):
        super(MessageResource, self).initialize(*args, **kwargs)

        self.message_id = message_id

    @property
    def message(self):
        if not hasattr(self, '_message'):
            self._message = prototypes.MessagePrototype.get_by_id(self.message_id)
        return self._message

    def show_messages(self, query, page, incoming):

        if incoming:
            url_builder = UrlBuilder(reverse('accounts:messages:'), arguments={'page': page})
        else:
            url_builder = UrlBuilder(reverse('accounts:messages:sent'), arguments={'page': page})

        messages_count = query.count()

        page = int(page) - 1

        paginator = Paginator(page, messages_count, conf.settings.MESSAGES_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        message_from, message_to = paginator.page_borders(page)

        messages = [ prototypes.MessagePrototype(message_model) for message_model in query.order_by('-created_at')[message_from:message_to]]

        return self.template('personal_messages/index.html',
                             {'messages': messages,
                              'paginator': paginator,
                              'incoming': incoming})


    @handler('', method='get')
    def index(self, page=1):
        self.account.reset_new_messages_number()
        return self.show_messages(models.Message.objects.filter(recipient_id=self.account.id, hide_from_recipient=False),
                                  page,
                                  True)

    @handler('sent', method='get')
    def sent(self, page=1):
        return self.show_messages(models.Message.objects.filter(sender_id=self.account.id, hide_from_sender=False),
                                  page,
                                  False)

    def check_recipients(self, recipients_form):
        system_user = accounts_logic.get_system_user()

        if system_user.id in recipients_form.c.recipients:
            return self.auto_error('personal_messages.new.system_user', u'Нельзя отправить сообщение системному пользователю')

        if accounts_models.Account.objects.filter(is_fast=True, id__in=recipients_form.c.recipients).exists():
            return self.auto_error('personal_messages.new.fast_account', u'Нельзя отправить сообщение пользователю, не завершившему регистрацию')

        if accounts_models.Account.objects.filter(id__in=recipients_form.c.recipients).count() != len(recipients_form.c.recipients):
            return self.auto_error('personal_messages.new.unexisted_account', u'Вы пытаетесь отправить сообщение несуществующему пользователю')

        return None


    @accounts_views.validate_ban_forum()
    @validate_argument('answer_to', prototypes.MessagePrototype.get_by_id, 'personal_messages', u'Неверный идентификатор сообщения')
    @handler('new', method='post')
    def new(self, answer_to=None):
        text = u''

        if answer_to is not None:
            if answer_to.recipient_id != self.account.id:
                return self.auto_error('personal_messages.new.not_permissions_to_answer_to', u'Вы пытаетесь ответить на чужое сообщение')

            if answer_to:
                text = u'[quote]\n%s\n[/quote]\n' % answer_to.text

        recipients_form = forms.RecipientsForm(self.request.POST)

        if not recipients_form.is_valid():
            return self.auto_error('personal_messages.new.form_errors', u'Ошибка в запросе')

        check_result = self.check_recipients(recipients_form)
        if check_result:
            return check_result

        form = forms.NewMessageForm(initial={'text': text,
                                             'recipients': ','.join(str(recipient_id) for recipient_id in recipients_form.c.recipients)})

        return self.template('personal_messages/new.html',
                             {'recipients': accounts_prototypes.AccountPrototype.get_list_by_id(recipients_form.c.recipients),
                              'form': form})


    @accounts_views.validate_ban_forum()
    @handler('create', method='post')
    def create(self):
        form = forms.NewMessageForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('personal_messages.create.form_errors', form.errors)

        check_result = self.check_recipients(form)
        if check_result:
            return check_result

        logic_task = postponed_tasks.SendMessagesTask(account_id=self.account.id,
                                                      recipients=form.c.recipients,
                                                      message=form.c.text)

        task = PostponedTaskPrototype.create(logic_task)

        amqp_environment.environment.workers.accounts_manager.cmd_task(task.id)

        return self.json_processing(status_url=task.status_url)


    @handler('#message_id', 'delete', method='post')
    def delete(self):

        if self.account.id not in (self.message.sender_id, self.message.recipient_id):
            return self.auto_error('personal_messages.delete.no_permissions', u'Вы не можете влиять на это сообщение')

        self.message.hide_from(sender=(self.account.id == self.message.sender_id),
                               recipient=(self.account.id == self.message.recipient_id))

        return self.json_ok()


    @handler('delete-all', method='post')
    def delete_all(self):
        prototypes.MessagePrototype.hide_all(account_id=self.account.id)
        return self.json_ok()
