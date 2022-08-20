
import smart_imports

smart_imports.all()


def notify_post_service(answer, recipients_ids):
    for recipient_id in recipients_ids:
        post_service_prototypes.MessagePrototype.create(post_service_message_handlers.PersonalMessageHandler(message_id=answer.message_id, account_id=recipient_id))


def new_messages_number_url():
    arguments = {'api_version': conf.settings.NEW_MESSAGES_NUMBER_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return utils_urls.url('accounts:messages:api-new-messages-number', **arguments)


def send_message(sender_id, recipients_ids, body, asynchronous=False):

    def callback(answer):
        notify_post_service(answer=answer,
                            recipients_ids=recipients_ids)

    return tt_services.personal_messages.cmd_send_message(sender_id=sender_id,
                                                          recipients_ids=recipients_ids,
                                                          body=body,
                                                          asynchronous=asynchronous,
                                                          callback=callback)
