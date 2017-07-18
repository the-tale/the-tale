

from django.conf import settings as project_settings

from dext.common.utils.urls import url

from . import conf


def notify_post_service(answer, recipients_ids):
    from the_tale.post_service.prototypes import MessagePrototype
    from the_tale.post_service.message_handlers import PersonalMessageHandler

    for recipient_id in recipients_ids:
        MessagePrototype.create(PersonalMessageHandler(message_id=answer.message_id, account_id=recipient_id))



def new_messages_number_url():
    arguments = {'api_version': conf.settings.NEW_MESSAGES_NUMNER_API_VERSION,
                 'api_client': project_settings.API_CLIENT}

    return url('accounts:messages:api-new-messages-number', **arguments)
