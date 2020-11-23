
import smart_imports

smart_imports.all()


@dataclasses.dataclass(frozen=True)
class AccountInfo:
    __slots__ = ('id', 'name', 'email')

    id: int
    name: str
    email: str


class Client(client.Client):
    __slots__ = ()

    def cmd_get_token(self, account, sandbox):
        info = tt_protocol_xsolla_pb2.AccountInfo(id=account.id,
                                                  name=account.nick_verbose,
                                                  email=account.email)

        request = tt_protocol_xsolla_pb2.GetTokenRequest(account_info=info,
                                                         mode='sandbox' if sandbox else 'normal')

        answer = operations.sync_request(url=self.url('get-token'),
                                         data=request,
                                         AnswerType=tt_protocol_xsolla_pb2.GetTokenResponse)
        return answer.token

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_xsolla_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_xsolla_pb2.DebugClearServiceResponse)
