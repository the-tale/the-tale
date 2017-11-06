# coding: utf-8

from dext.common.utils import views as dext_views
from dext.common.utils.urls import UrlBuilder, url

from the_tale import amqp_environment


from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils import list_filter
from the_tale.common.utils import views as utils_views
from the_tale.common.utils import api

from the_tale.accounts import prototypes as accounts_prototypes
from the_tale.accounts import views as accounts_views
from the_tale.accounts import models as accounts_models
from the_tale.accounts import logic as accounts_logic


from . import conf
from . import tt_api
from . import logic
from . import forms


########################################
# processors definition
########################################

class MessageProcessor(dext_views.ArgumentProcessor):
    def parse(self, context, raw_value):
        try:
            message_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        message = tt_api.get_message(context.account.id, message_id)

        if not message:
            self.raise_wrong_value()

        return message

########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='personal_messages')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(accounts_views.LoginRequiredProcessor())
resource.add_processor(accounts_views.FullAccountProcessor())

########################################
# views
########################################

@utils_views.PageNumberProcessor()
@utils_views.TextFilterProcessor(get_name='filter', context_name='filter', default_value=None)
@resource('')
def index(context):
    tt_api.read_messages(context.account.id)

    contacts_ids = tt_api.get_contacts(context.account.id)

    messages_count, messages = tt_api.get_received_messages(context.account.id,
                                                           text=context.filter,
                                                           offset=context.page*conf.settings.MESSAGES_ON_PAGE,
                                                           limit=conf.settings.MESSAGES_ON_PAGE)

    class Filter(list_filter.ListFilter):
        ELEMENTS = [list_filter.reset_element(),
                    list_filter.filter_element('поиск:', attribute='filter', default_value=None),
                    list_filter.static_element('количество:', attribute='count', default_value=0) ]

    url_builder = UrlBuilder(url('accounts:messages:'), arguments={'page': context.page,
                                                                   'filter': context.filter})

    index_filter = Filter(url_builder=url_builder, values={'filter': context.filter,
                                                           'count': messages_count})

    paginator = Paginator(context.page, messages_count, conf.settings.MESSAGES_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return dext_views.Redirect(paginator.last_page_url, permanent=False)

    accounts_ids = set(contacts_ids)

    for message in messages:
        accounts_ids.add(message.sender_id)
        accounts_ids.update(message.recipients_ids)

    accounts = {account.id: account for account in accounts_prototypes.AccountPrototype.get_list_by_id(list(accounts_ids))}

    contacts = [accounts[contact_id] for contact_id in contacts_ids]
    contacts.sort(key=lambda account: account.nick_verbose)

    return dext_views.Page('personal_messages/index.html',
                           content= {'messages': messages,
                                     'paginator': paginator,
                                     'page': 'incoming',
                                     'contacts': contacts,
                                     'accounts': accounts,
                                     'index_filter': index_filter,
                                     'master_account': context.account,
                                     'resource': context.resource})


@utils_views.PageNumberProcessor()
@utils_views.TextFilterProcessor(get_name='filter', context_name='filter', default_value=None)
@resource('sent')
def sent(context):

    contacts_ids = tt_api.get_contacts(context.account.id)

    messages_count, messages = tt_api.get_sent_messages(context.account.id,
                                                       text=context.filter,
                                                       offset=context.page*conf.settings.MESSAGES_ON_PAGE,
                                                       limit=conf.settings.MESSAGES_ON_PAGE)

    class Filter(list_filter.ListFilter):
        ELEMENTS = [list_filter.reset_element(),
                    list_filter.filter_element('поиск:', attribute='filter', default_value=None),
                    list_filter.static_element('количество:', attribute='count', default_value=0) ]

    url_builder=UrlBuilder(url('accounts:messages:sent'), arguments={'page': context.page,
                                                                     'filter': context.filter})

    index_filter = Filter(url_builder=url_builder, values={'filter': context.filter,
                                                           'count': messages_count})

    paginator = Paginator(context.page, messages_count, conf.settings.MESSAGES_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return dext_views.Redirect(paginator.last_page_url, permanent=False)

    accounts_ids = set(contacts_ids)

    for message in messages:
        accounts_ids.add(message.sender_id)
        accounts_ids.update(message.recipients_ids)

    accounts = {account.id: account for account in accounts_prototypes.AccountPrototype.get_list_by_id(list(accounts_ids))}

    contacts = [accounts[contact_id] for contact_id in contacts_ids]
    contacts.sort(key=lambda account: account.nick_verbose)

    return dext_views.Page('personal_messages/index.html',
                           content={'messages': messages,
                                    'paginator': paginator,
                                    'accounts': accounts,
                                    'contacts': contacts,
                                    'page': 'sent',
                                    'master_account': context.account,
                                    'index_filter': index_filter,
                                    'resource': context.resource})


@utils_views.PageNumberProcessor()
@accounts_views.AccountProcessor(error_message='Контакт не найден', get_name='contact', context_name='contact')
@utils_views.TextFilterProcessor(get_name='filter', context_name='filter', default_value=None)
@resource('conversation')
def conversation(context):

    contacts_ids = tt_api.get_contacts(context.account.id)

    messages_count, messages = tt_api.get_conversation(context.account.id,
                                                      context.contact.id,
                                                      text=context.filter,
                                                      offset=context.page*conf.settings.MESSAGES_ON_PAGE,
                                                      limit=conf.settings.MESSAGES_ON_PAGE)

    class Filter(list_filter.ListFilter):
        ELEMENTS = [list_filter.reset_element(),
                    list_filter.filter_element('поиск:', attribute='filter', default_value=None),
                    list_filter.static_element('количество:', attribute='count', default_value=0) ]

    url_builder = UrlBuilder(url('accounts:messages:conversation'), arguments={'page': context.page,
                                                                               'contact': context.contact.id,
                                                                               'filter': context.filter})

    index_filter = Filter(url_builder=url_builder, values={'contact': context.contact.id,
                                                           'filter': context.filter,
                                                           'count': messages_count})

    paginator = Paginator(context.page, messages_count, conf.settings.MESSAGES_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return dext_views.Redirect(paginator.last_page_url, permanent=False)

    accounts_ids = set(contacts_ids)

    for message in messages:
        accounts_ids.add(message.sender_id)
        accounts_ids.update(message.recipients_ids)

    accounts = {account.id: account for account in accounts_prototypes.AccountPrototype.get_list_by_id(list(accounts_ids))}

    contacts = [accounts[contact_id] for contact_id in contacts_ids]
    contacts.sort(key=lambda account: account.nick_verbose)

    return dext_views.Page('personal_messages/index.html',
                           content= {'messages': messages,
                                     'paginator': paginator,
                                     'page': 'contacts',
                                     'contacts': contacts,
                                     'accounts': accounts,
                                     'master_account': context.account,
                                     'index_filter': index_filter,
                                     'contact': context.contact,
                                     'resource': context.resource})



def check_recipients(recipients_form):
    system_user = accounts_logic.get_system_user()

    if system_user.id in recipients_form.c.recipients:
        raise dext_views.ViewError(code='system_user', message='Нельзя отправить сообщение системному пользователю')

    if accounts_models.Account.objects.filter(is_fast=True, id__in=recipients_form.c.recipients).exists():
        raise dext_views.ViewError(code='fast_account', message='Нельзя отправить сообщение пользователю, не завершившему регистрацию')

    if accounts_models.Account.objects.filter(id__in=recipients_form.c.recipients).count() != len(recipients_form.c.recipients):
        raise dext_views.ViewError(code='unexisted_account', message='Вы пытаетесь отправить сообщение несуществующему пользователю')


@accounts_views.BanForumProcessor()
@dext_views.FormProcessor(form_class=forms.RecipientsForm)
@MessageProcessor(error_message='Сообщение не найдено', get_name='answer_to', context_name='answer_to', default_value=None)
@resource('new', method='POST')
def new(context):
    text = ''

    if context.answer_to:
        text = '[quote]\n%s\n[/quote]\n' % context.answer_to.body

    check_recipients(context.form)

    form = forms.NewMessageForm(initial={'text': text,
                                         'recipients': ','.join(str(recipient_id) for recipient_id in context.form.c.recipients)})

    return dext_views.Page('personal_messages/new.html',
                           content={'recipients': accounts_prototypes.AccountPrototype.get_list_by_id(context.form.c.recipients),
                                    'form': form,
                                    'resource': context.resource})


@accounts_views.BanForumProcessor()
@dext_views.FormProcessor(form_class=forms.NewMessageForm)
@resource('create', method='POST')
def create(context):
    check_recipients(context.form)

    tt_api.send_message(sender_id=context.account.id,
                       recipients_ids=context.form.c.recipients,
                       body=context.form.c.text)

    return dext_views.AjaxOk()


@MessageProcessor(error_message='Сообщение не найдено', url_name='message_id', context_name='message')
@resource('#message_id', 'delete', method='POST')
def delete(context):
    owners_ids = [context.message.sender_id]
    owners_ids.extend(context.message.recipients_ids)

    if context.account.id not in owners_ids:
        raise dext_views.ViewError(code='no_permissions', message='Вы не можете влиять на это сообщение')

    tt_api.hide_message(account_id=context.account.id, message_id=context.message.id)

    return dext_views.AjaxOk()


@resource('delete-all', method='POST')
def delete_all(context):
    tt_api.hide_all_messages(account_id=context.account.id)
    return dext_views.AjaxOk()


@accounts_views.AccountProcessor(error_message='Контакт не найден', get_name='contact', context_name='contact')
@resource('delete-conversation', method='POST')
def delete_conversation(context):
    tt_api.hide_conversation(account_id=context.account.id, partner_id=context.contact.id)
    return dext_views.AjaxOk()


@api.Processor(versions=(conf.settings.NEW_MESSAGES_NUMNER_API_VERSION,))
@resource('api', 'new-messages-number', name='api-new-messages-number')
def api_new_messages(context):
    return dext_views.AjaxOk(content={'number': tt_api.new_messages_number(context.account.id)})
