

class Operation(object):
    __slots__ = ('account_id', 'currency', 'amount', 'type', 'description')

    def __init__(self, account_id, amount, currency, type, description):
        self.account_id = account_id
        self.currency = currency
        self.amount = amount
        self.type = type
        self.description = description

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.account_id == other.account_id and
                self.currency == other.currency and
                self.amount == other.amount and
                self.type == other.type and
                self.description == other.description)

    def __ne__(self, other):
        return not self.__eq__(other)


class HistoryRecord(object):
    __slots__ = ('created_at', 'currency', 'amount', 'description')

    def __init__(self, created_at, currency, amount, description):
        self.created_at = created_at
        self.currency = currency
        self.amount = amount
        self.description = description
