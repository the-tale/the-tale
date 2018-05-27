
from django.conf import settings as project_settings

from the_tale.common.utils import exceptions as utils_exceptions

from tt_protocol.protocol import bank_pb2

from the_tale.common.utils import tt_api

from . import conf
from . import exceptions


ENERGY_CURRENCY_ID = 0


def energy_balance(account_id):
    answer = tt_api.sync_request(url=conf.game_settings.TT_ENERGY_BALANCE,
                                 data=bank_pb2.AccountBalanceRequest(account_id=account_id),
                                 AnswerType=bank_pb2.AccountBalanceResponse)

    return answer.balance.get(ENERGY_CURRENCY_ID, 0)


def change_energy_balance(account_id, type, energy, async=False, autocommit=False):

    if async and not autocommit:
        raise exceptions.AutocommitRequiredForAsyncTransaction()

    operations = [bank_pb2.Operation(account_id=account_id,
                                     currency=ENERGY_CURRENCY_ID,
                                     amount=energy,
                                     type=type)]

    if not async:
        try:
            answer = tt_api.sync_request(url=conf.game_settings.TT_ENERGY_START_TRANSACTION,
                                         data=bank_pb2.StartTransactionRequest(lifetime=conf.game_settings.ENERGY_TRANSACTION_LIFETIME,
                                                                               operations=operations,
                                                                               autocommit=autocommit),
                                         AnswerType=bank_pb2.StartTransactionResponse)
        except utils_exceptions.TTAPIUnexpectedAPIStatus:
            return False, None

        return True, answer.transaction_id

    tt_api.async_request(url=conf.game_settings.TT_ENERGY_START_TRANSACTION,
                         data=bank_pb2.StartTransactionRequest(lifetime=conf.game_settings.ENERGY_TRANSACTION_LIFETIME,
                                                               operations=operations,
                                                               autocommit=autocommit))

    return True, None


def commit_transaction(transaction_id):
    tt_api.async_request(url=conf.game_settings.TT_ENERGY_COMMIT_TRANSACTION,
                         data=bank_pb2.CommitTransactionRequest(transaction_id=transaction_id))


def debug_clear_service():
    if not project_settings.TESTS_RUNNING:
        return

    tt_api.sync_request(url=conf.game_settings.TT_ENERGY_DEBUG_CLEAR_SERVICE_URL,
                        data=bank_pb2.DebugClearServiceRequest(),
                        AnswerType=bank_pb2.DebugClearServiceResponse)
