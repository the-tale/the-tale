

class Lot:
    __slots__ = ('type', 'item_type', 'item_id', 'owner_id', 'price', 'created_at')

    def __init__(self, type, item_type, item_id, owner_id, price, created_at):
        self.type = type
        self.item_type = item_type
        self.item_id = item_id
        self.owner_id = owner_id
        self.price = price
        self.created_at = created_at


    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.type == other.type and
                self.item_type == other.item_type and
                self.item_id == other.item_id and
                self.owner_id == other.owner_id and
                self.price == other.price and
                self.created_at == other.created_at)

    def __ne__(self, other):
        return not self.__eq__(other)


class ItemTypeSummary:
    __slots__ = ('item_type', 'sell_number', 'min_sell_price', 'max_sell_price', 'owner_sell_number')

    def __init__(self, item_type, sell_number, min_sell_price, max_sell_price, owner_sell_number):
        self.item_type = item_type
        self.sell_number = sell_number
        self.min_sell_price = min_sell_price
        self.max_sell_price = max_sell_price
        self.owner_sell_number = owner_sell_number

    def __eq__(self, other):
        return (self.item_type == other.item_type and
                self.sell_number == other.sell_number and
                self.min_sell_price == other.min_sell_price and
                self.max_sell_price == other.max_sell_price and
                self.owner_sell_number == other.owner_sell_number)

    def __ne__(self, other):
        return not self.__eq__(other)


class LogRecord:
    __slots__ = ('item_type', 'price', 'created_at')

    def __init__(self, item_type, price, created_at):
        self.item_type = item_type
        self.price = price
        self.created_at = created_at

    def __eq__(self, other):
        return (self.item_type == other.item_type and
                self.price == other.price and
                self.created_at == other.created_at)
