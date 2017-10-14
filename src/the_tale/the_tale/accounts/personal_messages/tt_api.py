
from django.conf import settings as project_settings

from tt_protocol.protocol import personal_messages_pb2

from the_tale.common.utils import tt_api

from the_tale.accounts import logic as accounts_logic

from . import conf
from . import logic


def read_messages(account_id, async=False):
    if async and not project_settings.TESTS_RUNNING:
        tt_api.async_request(url=conf.settings.TT_READ_MESSAGES_URL,
                             data=personal_messages_pb2.ReadMessagesRequest(account_id=account_id))
    else:
        tt_api.sync_request(url=conf.settings.TT_READ_MESSAGES_URL,
                            data=personal_messages_pb2.ReadMessagesRequest(account_id=account_id),
                            AnswerType=personal_messages_pb2.ReadMessagesResponse)


def new_messages_number(account_id):
    answer = tt_api.sync_request(url=conf.settings.TT_NEW_MESSAGES_NUMBER_URL,
                                 data=personal_messages_pb2.NewMessagesNumberRequest(account_id=account_id),
                                 AnswerType=personal_messages_pb2.NewMessagesNumberResponse)
    return answer.number


def remove_old_system_messages():
    tt_api.sync_request(url=conf.settings.TT_REMOVE_OLD_MESSAGES_URL,
                        data=personal_messages_pb2.RemoveOldMessagesRequest(accounts_ids=[accounts_logic.get_system_user_id()],
                                                                            barrier=conf.settings.SYSTEM_MESSAGES_LEAVE_TIME.total_seconds()),
                        AnswerType=personal_messages_pb2.RemoveOldMessagesResponse)


def get_contacts(account_id):
    answer = tt_api.sync_request(url=conf.settings.TT_GET_CONTACTS_URL,
                                 data=personal_messages_pb2.GetContactsRequest(account_id=account_id),
                                 AnswerType=personal_messages_pb2.GetContactsResponse)
    return answer.accounts_ids


def get_received_messages(account_id, text=None, offset=None, limit=None):
    data = personal_messages_pb2.GetMessagesRequest(account_id=account_id,
                                                    type=personal_messages_pb2.OwnerType.DESCRIPTOR.values_by_name['RECIPIENT'].number,
                                                    text=text,
                                                    offset=offset,
                                                    limit=limit)

    answer = tt_api.sync_request(url=conf.settings.TT_GET_MESSAGES_URL,
                                 data=data,
                                 AnswerType=personal_messages_pb2.GetMessagesResponse)

    return answer.total, answer.messages


def get_sent_messages(account_id, text=None, offset=None, limit=None):
    data = personal_messages_pb2.GetMessagesRequest(account_id=account_id,
                                                    type=personal_messages_pb2.OwnerType.DESCRIPTOR.values_by_name['SENDER'].number,
                                                    text=text,
                                                    offset=offset,
                                                    limit=limit)

    answer = tt_api.sync_request(url=conf.settings.TT_GET_MESSAGES_URL,
                                 data=data,
                                 AnswerType=personal_messages_pb2.GetMessagesResponse)

    return answer.total, answer.messages


def get_conversation(account_id, partner_id, text=None, offset=None, limit=None):
    data = personal_messages_pb2.GetConversationRequest(account_id=account_id,
                                                        partner_id=partner_id,
                                                        text=text,
                                                        offset=offset,
                                                        limit=limit)

    answer = tt_api.sync_request(url=conf.settings.TT_GET_CONVERSATION_URL,
                                 data=data,
                                 AnswerType=personal_messages_pb2.GetConversationResponse)

    return answer.total, answer.messages


def get_message(account_id, message_id):
    data = personal_messages_pb2.GetMessageRequest(account_id=account_id, message_id=message_id)

    answer = tt_api.sync_request(url=conf.settings.TT_GET_MESSAGE_URL,
                                 data=data,
                                 AnswerType=personal_messages_pb2.GetMessageResponse)

    if answer.HasField('message'):
        return answer.message

    return None


def send_message(sender_id, recipients_ids, body, async=False):
    data = personal_messages_pb2.SendMessageRequest(sender_id=sender_id,
                                                    recipients_ids=recipients_ids,
                                                    body=body)

    if async and not project_settings.TESTS_RUNNING:
        tt_api.async_request(url=conf.settings.TT_SEND_MESSAGE_URL,
                             data=data,
                             AnswerType=personal_messages_pb2.SendMessageResponse,
                             callback=lambda answer: logic.notify_post_service(answer=answer, recipients_ids=recipients_ids))
    else:
        answer = tt_api.sync_request(url=conf.settings.TT_SEND_MESSAGE_URL,
                                     data=data,
                                     AnswerType=personal_messages_pb2.SendMessageResponse)
        logic.notify_post_service(answer, recipients_ids)
        return answer.message_id


def hide_message(account_id, message_id):
    data = personal_messages_pb2.HideMessageRequest(account_id=account_id,
                                                    message_id=message_id)
    tt_api.sync_request(url=conf.settings.TT_HIDE_MESSAGE_URL, data=data)


def hide_all_messages(account_id):
    data = personal_messages_pb2.HideAllMessagesRequest(account_id=account_id)
    tt_api.sync_request(url=conf.settings.TT_HIDE_ALL_MESSAGES_URL, data=data)


def hide_conversation(account_id, partner_id):
    data = personal_messages_pb2.HideConversationRequest(account_id=account_id, partner_id=partner_id)
    tt_api.sync_request(url=conf.settings.TT_HIDE_CONVERSATION_URL, data=data)


def debug_clear_service():
    if project_settings.TESTS_RUNNING:
        tt_api.sync_request(url=conf.settings.TT_DEBUG_CLEAR_SERVICE_URL,
                            data=personal_messages_pb2.DebugClearServiceRequest(),
                            AnswerType=personal_messages_pb2.DebugClearServiceResponse)
