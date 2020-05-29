
import datetime

from tt_web import s11n
from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_protocol.protocol import data_protector_pb2
from tt_protocol.protocol import personal_messages_pb2

from . import protobuf
from . import relations
from . import operations


@handlers.api(personal_messages_pb2.NewMessagesNumberRequest)
async def new_messages_number(message, **kwargs):
    number = await operations.new_messages_number(account_id=message.account_id)
    return personal_messages_pb2.NewMessagesNumberResponse(number=number)


@handlers.api(personal_messages_pb2.ReadMessagesRequest)
async def read_messages(message, **kwargs):
    await operations.read_messages(account_id=message.account_id)
    return personal_messages_pb2.ReadMessagesResponse()


@handlers.api(personal_messages_pb2.SendMessageRequest)
async def send_message(message, **kwargs):
    message_id = await operations.send_message(sender_id=message.sender_id, recipients_ids=list(message.recipients_ids), body=message.body)
    return personal_messages_pb2.SendMessageResponse(message_id=message_id)


@handlers.api(personal_messages_pb2.HideMessageRequest)
async def hide_message(message, **kwargs):
    await operations.hide_message(account_id=message.account_id, message_id=message.message_id)
    return personal_messages_pb2.HideMessageResponse()


@handlers.api(personal_messages_pb2.HideAllMessagesRequest)
async def hide_all_messages(message, **kwargs):
    await operations.hide_all_messages(account_id=message.account_id)
    return personal_messages_pb2.HideAllMessagesResponse()


@handlers.api(personal_messages_pb2.HideConversationRequest)
async def hide_conversation(message, **kwargs):
    await operations.hide_conversation(account_id=message.account_id, partner_id=message.partner_id)
    return personal_messages_pb2.HideConversationResponse()


@handlers.api(personal_messages_pb2.RemoveOldMessagesRequest)
async def remove_old_messages(message, **kwargs):
    messages_ids = await operations.old_messages_ids(accounts_ids=list(message.accounts_ids),
                                                     barrier=datetime.datetime.fromtimestamp(message.barrier))
    await operations.remove_messages(messages_ids)

    return personal_messages_pb2.RemoveOldMessagesResponse()


@handlers.api(personal_messages_pb2.GetMessagesRequest)
async def get_messages(message, **kwargs):
    total, messages = await operations.load_messages(account_id=message.account_id,
                                                     type=relations.OWNER_TYPE.index_protocol_value[message.type],
                                                     text=message.text if message.text else None,
                                                     offset=message.offset,
                                                     limit=message.limit if message.limit else None)
    return personal_messages_pb2.GetMessagesResponse(total=total,
                                                     messages=[protobuf.from_message(message) for message in messages])


@handlers.api(personal_messages_pb2.GetConversationRequest)
async def get_conversation(message, **kwargs):
    total, messages = await operations.load_conversation(account_id=message.account_id,
                                                         partner_id=message.partner_id,
                                                         text=message.text if message.text else None,
                                                         offset=message.offset,
                                                         limit=message.limit if message.limit else None)
    return personal_messages_pb2.GetConversationResponse(total=total,
                                                         messages=[protobuf.from_message(message) for message in messages])


@handlers.api(personal_messages_pb2.GetMessageRequest)
async def get_message(message, **kwargs):
    message = await operations.load_message(account_id=message.account_id,
                                            message_id=message.message_id)
    if message is None:
        return personal_messages_pb2.GetMessageResponse()

    return personal_messages_pb2.GetMessageResponse(message=protobuf.from_message(message))


@handlers.api(personal_messages_pb2.GetContactsRequest)
async def get_contacts(message, **kwargs):
    contacts_ids = await operations.get_contacts(account_id=message.account_id)
    return personal_messages_pb2.GetContactsResponse(accounts_ids=contacts_ids)


@handlers.api(data_protector_pb2.PluginReportRequest, raw=True)
async def data_protection_collect_data(message, config, **kwargs):

    if config['custom']['data_protector']['secret'] != message.secret:
        raise tt_exceptions.ApiError(code='personal_messages.data_protection_collect_data.wrong_secret',
                                     message='wrong secret code')

    report = await operations.get_data_report(account_id=int(message.account_id))

    return data_protector_pb2.PluginReportResponse(result=data_protector_pb2.PluginReportResponse.ResultType.SUCCESS,
                                                   data=s11n.to_json(report))


@handlers.api(data_protector_pb2.PluginDeletionRequest, raw=True)
async def data_protection_delete_data(message, config, **kwargs):
    if config['custom']['data_protector']['secret'] != message.secret:
        raise tt_exceptions.ApiError(code='personal_messages.data_protection_delete_data.wrong_secret',
                                     message='wrong secret code')

    await operations.hide_all_messages(account_id=int(message.account_id))

    return data_protector_pb2.PluginDeletionResponse(result=data_protector_pb2.PluginDeletionResponse.ResultType.SUCCESS)


@handlers.api(personal_messages_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_messages()
    return personal_messages_pb2.DebugClearServiceResponse()
