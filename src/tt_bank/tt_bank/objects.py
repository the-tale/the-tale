

class Operation:
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


class HistoryRecord:
    __slots__ = ('created_at', 'currency', 'amount', 'description')

    def __init__(self, created_at, currency, amount, description):
        self.created_at = created_at
        self.currency = currency
        self.amount = amount
        self.description = description


class Restrictions:
    __slots__ = ('hard_minimum', 'hard_maximum', 'soft_minimum', 'soft_maximum')

    def __init__(self, hard_minimum=0, hard_maximum=None, soft_minimum=None, soft_maximum=None):
        self.hard_minimum = hard_minimum
        self.hard_maximum = hard_maximum
        self.soft_minimum = soft_minimum
        self.soft_maximum = soft_maximum

    def serialize(self):
        return {'hard_minimum': self.hard_minimum,
                'hard_maximum': self.hard_maximum,
                'soft_minimum': self.soft_minimum,
                'soft_maximum': self.soft_maximum}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, field) == getattr(other, field) for field in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)
