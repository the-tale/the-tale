import smart_imports

smart_imports.all()


class Client(client.Client):
    __slots__ = ('transaction_lifetime',)

    def __init__(self, transaction_lifetime, **kwargs):
        super().__init__(**kwargs)
        self.transaction_lifetime = transaction_lifetime

    def cmd_balance(self, account_id, currency=0):
        answer = operations.sync_request(url=self.url('accounts/balance'),
                                         data=tt_protocol_bank_pb2.AccountBalanceRequest(account_id=account_id),
                                         AnswerType=tt_protocol_bank_pb2.AccountBalanceResponse)

        return answer.balance.get(currency, 0)

    def cmd_change_balance(self, account_id, type, energy, async=False, autocommit=False, currency=0):

        if async and not autocommit:
            raise exceptions.AutocommitRequiredForAsyncTransaction

        applied_operations = [tt_protocol_bank_pb2.Operation(account_id=account_id,
                                                             currency=currency,
                                                             amount=energy,
                                                             type=type)]

        if not async:
            try:
                answer = operations.sync_request(url=self.url('transactions/start'),
                                                 data=tt_protocol_bank_pb2.StartTransactionRequest(lifetime=self.transaction_lifetime,
                                                                                                   operations=applied_operations,
                                                                                                   autocommit=autocommit),
                                                 AnswerType=tt_protocol_bank_pb2.StartTransactionResponse)
            except exceptions.TTAPIUnexpectedAPIStatus:
                return False, None

            return True, answer.transaction_id

        operations.async_request(url=self.url('transactions/start'),
                                 data=tt_protocol_bank_pb2.StartTransactionRequest(lifetime=self.transaction_lifetime,
                                                                                   operations=applied_operations,
                                                                                   autocommit=autocommit))

        return True, None

    def cmd_commit_transaction(self, transaction_id):
        operations.async_request(url=self.url('transactions/commit'),
                                 data=tt_protocol_bank_pb2.CommitTransactionRequest(transaction_id=transaction_id))

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_bank_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_bank_pb2.DebugClearServiceResponse)
