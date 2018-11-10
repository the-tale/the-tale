
import smart_imports

smart_imports.all()


class Client(client.Client):
    __slots__ = ()

    def message_to_protobuf(self, message):
        raise NotImplementedError

    def protobuf_to_message(self, pb_message):
        raise NotImplementedError

    def cmd_push_message(self, account_id, message, size):
        operations.async_request(url=self.url('push-message'),
                                 data=tt_protocol_diary_pb2.PushMessageRequest(account_id=account_id,
                                                                               message=self.message_to_protobuf(message),
                                                                               diary_size=size))

    def cmd_version(self, account_id):
        answer = operations.sync_request(url=self.url('version'),
                                         data=tt_protocol_diary_pb2.VersionRequest(account_id=account_id),
                                         AnswerType=tt_protocol_diary_pb2.VersionResponse)

        return answer.version

    def cmd_diary(self, account_id):
        answer = operations.sync_request(url=self.url('diary'),
                                         data=tt_protocol_diary_pb2.DiaryRequest(account_id=account_id),
                                         AnswerType=tt_protocol_diary_pb2.DiaryResponse)

        return {'version': answer.diary.version,
                'messages': [self.protobuf_to_message(pb_message) for pb_message in answer.diary.messages]}
