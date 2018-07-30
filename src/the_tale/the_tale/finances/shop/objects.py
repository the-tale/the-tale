

class ItemTypeSummary:
    __slots__ = ('type', 'full_type', 'sell_number', 'min_sell_price', 'max_sell_price', 'name', 'owner_sell_number')

    def __init__(self, full_type, sell_number, min_sell_price, max_sell_price, name=None, type=None, owner_sell_number=0):
        self.full_type = full_type
        self.type = type
        self.name = name
        self.sell_number = sell_number
        self.min_sell_price = min_sell_price
        self.max_sell_price = max_sell_price
        self.owner_sell_number = owner_sell_number

    def ui_info(self):
        return {'full_type': self.full_type,
                'type': self.type,
                'name': self.name,
                'sell_number': self.sell_number,
                'min_sell_price': self.min_sell_price,
                'max_sell_price': self.max_sell_price,
                'owner_sell_number': self.owner_sell_number}

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.full_type == other.full_type and
                self.type == other.type and
                self.name == other.name and
                self.sell_number == other.sell_number and
                self.min_sell_price == other.min_sell_price and
                self.max_sell_price == other.max_sell_price and
                self.owner_sell_number == other.owner_sell_number)

    def __ne__(self, other):
        return not self.__eq__(other)


class Lot:
    __slots__ = ('owner_id', 'full_type', 'item_id', 'price', 'created_at')

    def __init__(self, owner_id, full_type, item_id, price, created_at=None):
        self.owner_id = owner_id
        self.full_type = full_type
        self.item_id = item_id
        self.price = price
        self.created_at = created_at

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.owner_id == other.owner_id and
                self.full_type == other.full_type and
                self.item_id == other.item_id and
                self.price == other.price and
                self.created_at == other.created_at)


class LogRecord:
    __slots__ = ('item_type', 'created_at', 'price')

    def __init__(self, item_type, created_at, price):
        self.item_type = item_type
        self.created_at = created_at
        self.price = price
