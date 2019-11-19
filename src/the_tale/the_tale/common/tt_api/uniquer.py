import smart_imports

smart_imports.all()


class Client(client.Client):
    __slots__ = ('_cache',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache = {}

    def cmd_get_id(self, key):
        if key in self._cache:
            return self._cache[key]

        answer = operations.sync_request(url=self.url('get-id'),
                                         data=tt_protocol_uniquer_pb2.GetIdRequest(key=key),
                                         AnswerType=tt_protocol_uniquer_pb2.GetIdResponse)
        self._cache[key] = answer.unique_id
        return answer.unique_id

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_uniquer_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_uniquer_pb2.DebugClearServiceResponse)
