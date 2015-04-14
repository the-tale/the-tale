# coding: utf-8

from dext.common.utils import views as dext_views
from dext.common.utils.urls import UrlBuilder, url

from the_tale import amqp_environment


from the_tale.common.postponed_tasks import PostponedTaskPrototype
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils import list_filter
from the_tale.common.utils import views as utils_views

from the_tale.accounts import prototypes as accounts_prototypes
from the_tale.accounts import views as accounts_views
from the_tale.accounts import models as accounts_models
from the_tale.accounts import logic as accounts_logic

from the_tale.accounts.personal_messages import models
from the_tale.accounts.personal_messages import prototypes
from the_tale.accounts.personal_messages import forms
from the_tale.accounts.personal_messages import conf
from the_tale.accounts.personal_messages import postponed_tasks

########################################
# processors definition
########################################

class MessageProcessor(dext_views.ArgumentProcessor):

    def parse(self, context, raw_value):
        try:
            message_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format(context=context)

        message = prototypes.MessagePrototype.get_by_id(message_id)

        if not message:
            self.raise_wrong_value(context=context)

        return message

# # TODO: sync semantics of CompanionProcessor and CompanionProcessor.handler
# message_processor = MessageProcessor.handler(error_message=u'Сообщение не найдено', url_name='message', context_name='message')


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='personal_messages')
resource.add_processor(accounts_views.current_account_processor)
resource.add_processor(utils_views.fake_resource_processor)
resource.add_processor(accounts_views.login_required_processor)
resource.add_processor(accounts_views.full_account_processor)

########################################
# views
########################################

@utils_views.page_number_processor.handler()
@accounts_views.AccountProcessor.handler(error_message=u'Отправитель не найден', get_name='sender', context_name='sender', default_value=None)
@dext_views.ArgumentProcessor.handler(get_name='filter', context_name='filter', default_value=None)
@resource.handler('')
def index(context):
    context.account.reset_new_messages_number()
    query = models.Message.objects.filter(recipient_id=context.account.id, hide_from_recipient=False)

    senders_ids = list(set(query.values_list('sender_id', flat=True).order_by('sender').distinct()))
    senders = sorted(accounts_prototypes.AccountPrototype.get_list_by_id(senders_ids), key=lambda account: account.nick)

    if context.sender is not None:
        query = query.filter(sender_id=context.sender.id)

    if context.filter is not None:
        query = query.filter(text__icontains=context.filter)

    class Filter(list_filter.ListFilter):
        ELEMENTS = [list_filter.reset_element(),
                    list_filter.filter_element(u'поиск:', attribute='filter', default_value=None),
                    list_filter.choice_element(u'отправитель:', attribute='sender', choices=[(None, u'все')] + [(account.id, account.nick) for account in senders] ),
                    list_filter.static_element(u'количество:', attribute='count', default_value=0) ]

    url_builder = UrlBuilder(url('accounts:messages:'), arguments={'page': context.page, 'sender': context.sender.id if context.sender is not None else None})

    messages_count = query.count()

    index_filter = Filter(url_builder=url_builder, values={'sender': context.sender.id if context.sender is not None else None,
                                                           'filter': context.filter,
                                                           'count': messages_count})

    # page = int(context.page) - 1

    paginator = Paginator(context.page, messages_count, conf.settings.MESSAGES_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return dext_views.Redirect(paginator.last_page_url, permanent=False)

    message_from, message_to = paginator.page_borders(context.page)

    messages = [ prototypes.MessagePrototype(message_model) for message_model in query.order_by('-created_at')[message_from:message_to]]

    return dext_views.Page('personal_messages/index.html',
                           content= {'messages': messages,
                                     'paginator': paginator,
                                     'incoming': True,
                                     'index_filter': index_filter,
                                     'resource': context.resource})


@utils_views.page_number_processor.handler()
@accounts_views.AccountProcessor.handler(error_message=u'Получатель не найден', get_name='recipient', context_name='recipient', default_value=None)
@dext_views.ArgumentProcessor.handler(get_name='filter', context_name='filter', default_value=None)
@resource.handler('sent')
def sent(context):
    query = models.Message.objects.filter(sender_id=context.account.id, hide_from_sender=False)

    recipients_ids = list(set(query.values_list('recipient_id', flat=True).order_by('recipient').distinct()))
    recipients = sorted(accounts_prototypes.AccountPrototype.get_list_by_id(recipients_ids), key=lambda account: account.nick)

    if context.recipient is not None:
        query = query.filter(recipient_id=context.recipient.id)

    if context.filter is not None:
        query = query.filter(text__icontains=context.filter)

    class Filter(list_filter.ListFilter):
        ELEMENTS = [list_filter.reset_element(),
                    list_filter.filter_element(u'поиск:', attribute='filter', default_value=None),
                    list_filter.choice_element(u'получатель:', attribute='recipient', choices=[(None, u'все')] + [(account.id, account.nick) for account in recipients] ),
                    list_filter.static_element(u'количество:', attribute='count', default_value=0) ]

    url_builder=UrlBuilder(url('accounts:messages:sent'), arguments={'page': context.page, 'recipient': context.recipient.id if context.recipient is not None else None})

    messages_count = query.count()

    index_filter = Filter(url_builder=url_builder, values={'recipient': context.recipient.id if context.recipient is not None else None,
                                                           'filter': filter,
                                                           'count': messages_count})

    # page = int(page) - 1

    paginator = Paginator(context.page, messages_count, conf.settings.MESSAGES_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return dext_views.Redirect(paginator.last_page_url, permanent=False)

    message_from, message_to = paginator.page_borders(context.page)

    messages = [ prototypes.MessagePrototype(message_model) for message_model in query.order_by('-created_at')[message_from:message_to]]

    return dext_views.Page('personal_messages/index.html',
                           content={'messages': messages,
                                    'paginator': paginator,
                                    'incoming': False,
                                    'index_filter': index_filter,
                                    'resource': context.resource})


def check_recipients(recipients_form):
    system_user = accounts_logic.get_system_user()

    if system_user.id in recipients_form.c.recipients:
        raise dext_views.ViewError(code='personal_messages.new.system_user', message=u'Нельзя отправить сообщение системному пользователю')

    if accounts_models.Account.objects.filter(is_fast=True, id__in=recipients_form.c.recipients).exists():
        raise dext_views.ViewError(code='personal_messages.new.fast_account', message=u'Нельзя отправить сообщение пользователю, не завершившему регистрацию')

    if accounts_models.Account.objects.filter(id__in=recipients_form.c.recipients).count() != len(recipients_form.c.recipients):
        raise dext_views.ViewError(code='personal_messages.new.unexisted_account', message=u'Вы пытаетесь отправить сообщение несуществующему пользователю')


@accounts_views.ban_forum_processor.handler()
@dext_views.FormProcessor.handler(form_class=forms.RecipientsForm)
@MessageProcessor.handler(error_message=u'Сообщение не найдено', get_name='answer_to', context_name='answer_to', default_value=None)
@resource.handler('new', method='POST')
def new(context):
    text = u''

    if context.answer_to:
        if context.answer_to.recipient_id != context.account.id:
            raise dext_views.ViewError(code='personal_messages.new.not_permissions_to_answer_to', message=u'Вы пытаетесь ответить на чужое сообщение')

        text = u'[quote]\n%s\n[/quote]\n' % context.answer_to.text

    check_recipients(context.form)

    form = forms.NewMessageForm(initial={'text': text,
                                         'recipients': ','.join(str(recipient_id) for recipient_id in context.form.c.recipients)})

    return dext_views.Page('personal_messages/new.html',
                           content={'recipients': accounts_prototypes.AccountPrototype.get_list_by_id(context.form.c.recipients),
                                    'form': form,
                                    'resource': context.resource})


@accounts_views.ban_forum_processor.handler()
@dext_views.FormProcessor.handler(form_class=forms.NewMessageForm)
@resource.handler('create', method='POST')
def create(context):
    check_recipients(context.form)

    logic_task = postponed_tasks.SendMessagesTask(account_id=context.account.id,
                                                  recipients=context.form.c.recipients,
                                                  message=context.form.c.text)

    task = PostponedTaskPrototype.create(logic_task)

    amqp_environment.environment.workers.accounts_manager.cmd_task(task.id)

    return dext_views.AjaxProcessing(status_url=task.status_url)


@MessageProcessor.handler(error_message=u'Сообщение не найдено', url_name='message_id', context_name='message')
@resource.handler('#message_id', 'delete', method='POST')
def delete(context):

    if context.account.id not in (context.message.sender_id, context.message.recipient_id):
        raise dext_views.ViewError(code='personal_messages.delete.no_permissions', message=u'Вы не можете влиять на это сообщение')

    context.message.hide_from(sender=(context.account.id == context.message.sender_id),
                              recipient=(context.account.id == context.message.recipient_id))

    return dext_views.AjaxOk()


@resource.handler('delete-all', method='POST')
def delete_all(context):
    prototypes.MessagePrototype.hide_all(account_id=context.account.id)
    return dext_views.AjaxOk()
