import smart_imports

smart_imports.all()


class Client(client.Client):

    def cmd_read_messages(self, account_id, async=False):
        if async:
            operations.async_request(url=self.url('read-messages'),
                                     data=tt_protocol_personal_messages_pb2.ReadMessagesRequest(account_id=account_id))
        else:
            operations.sync_request(url=self.url('read-messages'),
                                    data=tt_protocol_personal_messages_pb2.ReadMessagesRequest(account_id=account_id),
                                    AnswerType=tt_protocol_personal_messages_pb2.ReadMessagesResponse)

    def cmd_new_messages_number(self, account_id):
        answer = operations.sync_request(url=self.url('new-messages-number'),
                                         data=tt_protocol_personal_messages_pb2.NewMessagesNumberRequest(account_id=account_id),
                                         AnswerType=tt_protocol_personal_messages_pb2.NewMessagesNumberResponse)
        return answer.number

    def cmd_remove_old_system_messages(self, account_id, leave_time):
        operations.sync_request(url=self.url('remove-old-messages'),
                                data=tt_protocol_personal_messages_pb2.RemoveOldMessagesRequest(accounts_ids=[account_id],
                                                                                                barrier=leave_time.total_seconds()),
                                AnswerType=tt_protocol_personal_messages_pb2.RemoveOldMessagesResponse)

    def cmd_get_contacts(self, account_id):
        answer = operations.sync_request(url=self.url('get-contacts'),
                                         data=tt_protocol_personal_messages_pb2.GetContactsRequest(account_id=account_id),
                                         AnswerType=tt_protocol_personal_messages_pb2.GetContactsResponse)
        return answer.accounts_ids

    def cmd_get_received_messages(self, account_id, text=None, offset=None, limit=None):
        data = tt_protocol_personal_messages_pb2.GetMessagesRequest(account_id=account_id,
                                                                    type=tt_protocol_personal_messages_pb2.OwnerType.DESCRIPTOR.values_by_name['RECIPIENT'].number,
                                                                    text=text,
                                                                    offset=offset,
                                                                    limit=limit)

        answer = operations.sync_request(url=self.url('get-messages'),
                                         data=data,
                                         AnswerType=tt_protocol_personal_messages_pb2.GetMessagesResponse)

        return answer.total, answer.messages

    def cmd_get_sent_messages(self, account_id, text=None, offset=None, limit=None):
        data = tt_protocol_personal_messages_pb2.GetMessagesRequest(account_id=account_id,
                                                                    type=tt_protocol_personal_messages_pb2.OwnerType.DESCRIPTOR.values_by_name['SENDER'].number,
                                                                    text=text,
                                                                    offset=offset,
                                                                    limit=limit)

        answer = operations.sync_request(url=self.url('get-messages'),
                                         data=data,
                                         AnswerType=tt_protocol_personal_messages_pb2.GetMessagesResponse)

        return answer.total, answer.messages

    def cmd_get_conversation(self, account_id, partner_id, text=None, offset=None, limit=None):
        data = tt_protocol_personal_messages_pb2.GetConversationRequest(account_id=account_id,
                                                                        partner_id=partner_id,
                                                                        text=text,
                                                                        offset=offset,
                                                                        limit=limit)

        answer = operations.sync_request(url=self.url('get-conversation'),
                                         data=data,
                                         AnswerType=tt_protocol_personal_messages_pb2.GetConversationResponse)

        return answer.total, answer.messages

    def cmd_get_message(self, account_id, message_id):
        data = tt_protocol_personal_messages_pb2.GetMessageRequest(account_id=account_id, message_id=message_id)

        answer = operations.sync_request(url=self.url('get-message'),
                                         data=data,
                                         AnswerType=tt_protocol_personal_messages_pb2.GetMessageResponse)

        if answer.HasField('message'):
            return answer.message

        return None

    def cmd_send_message(self, sender_id, recipients_ids, body, async=False, callback=lambda answer, recipients_ids: None):
        data = tt_protocol_personal_messages_pb2.SendMessageRequest(sender_id=sender_id,
                                                                    recipients_ids=recipients_ids,
                                                                    body=body)

        if async:
            operations.async_request(url=self.url('send-message'),
                                     data=data,
                                     AnswerType=tt_protocol_personal_messages_pb2.SendMessageResponse,
                                     callback=callback)
        else:
            answer = operations.sync_request(url=self.url('send-message'),
                                             data=data,
                                             AnswerType=tt_protocol_personal_messages_pb2.SendMessageResponse)
            callback(answer=answer)
            return answer.message_id

    def cmd_hide_message(self, account_id, message_id):
        data = tt_protocol_personal_messages_pb2.HideMessageRequest(account_id=account_id,
                                                                    message_id=message_id)
        operations.sync_request(url=self.url('hide-message'), data=data)

    def cmd_hide_all_messages(self, account_id):
        data = tt_protocol_personal_messages_pb2.HideAllMessagesRequest(account_id=account_id)
        operations.sync_request(url=self.url('hide-all-messages'), data=data)

    def cmd_hide_conversation(self, account_id, partner_id):
        data = tt_protocol_personal_messages_pb2.HideConversationRequest(account_id=account_id, partner_id=partner_id)
        operations.sync_request(url=self.url('hide-conversation'), data=data)

    def cmd_debug_clear_service(self):
        if django_settings.TESTS_RUNNING:
            operations.sync_request(url=self.url('debug-clear-service'),
                                    data=tt_protocol_personal_messages_pb2.DebugClearServiceRequest(),
                                    AnswerType=tt_protocol_personal_messages_pb2.DebugClearServiceResponse)
