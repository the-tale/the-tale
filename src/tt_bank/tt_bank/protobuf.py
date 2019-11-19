import time


from tt_protocol.protocol import bank_pb2

from tt_web import s11n

from . import objects


def to_operation(pb_operation):
    return objects.Operation(account_id=pb_operation.account_id,
                             currency=pb_operation.currency,
                             amount=pb_operation.amount,
                             type=pb_operation.type,
                             description=pb_operation.description)


def to_restrictions(pb_restrictions):
    if not pb_restrictions:
        return objects.Restrictions()

    return objects.Restrictions(**s11n.from_json(pb_restrictions))


def from_history(history):
    return bank_pb2.HistoryRecord(created_at=time.mktime(history.created_at.timetuple()),
                                  currency=history.currency,
                                  amount=history.amount,
                                  description=history.description)


def from_balances(balances):
    return bank_pb2.Balances(amounts=balances)
