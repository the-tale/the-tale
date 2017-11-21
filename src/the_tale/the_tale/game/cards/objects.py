

from . import cards


class Card(object):

    __slots__ = ('uid', 'type', 'available_for_auction', 'data', 'in_storage')

    def __init__(self, type, available_for_auction=False, uid=None, data=None, in_storage=False):
        self.uid = uid
        self.type = type
        self.available_for_auction = available_for_auction
        self.data = data
        self.in_storage = in_storage

    @property
    def name(self):
        return self.effect.name_for_card(self)

    def serialize(self):
        return {'type': self.type.value,
                'auction': self.available_for_auction,
                'data': self.data}

    @classmethod
    def deserialize(cls, uid, data, in_storage=False):
        return cls(uid=uid,
                   type=cards.CARD(data['type']),
                   available_for_auction=data['auction'],
                   data=data.get('data'),
                   in_storage=in_storage)

    @property
    def effect(self):
        return self.type.effect

    def activate(self, hero, data):
        return self.effect.activate(hero, card=self, data=data)

    def ui_info(self):
        return {'name': self.name,
                'type': self.type.value,
                'full_type': self.item_full_type,
                'rarity': self.type.rarity.value,
                'uid': self.uid.hex,
                'in_storage': self.in_storage,
                'auction': self.available_for_auction}

    @property
    def item_base_type(self):
        return '{}'.format(self.type.value)

    @property
    def item_full_type(self):
        return self.effect.item_full_type(self)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.uid == other.uid and
                self.type == other.type and
                self.available_for_auction == other.available_for_auction and
                self.data == other.data)

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_same_effect(self, other):
        return (self.type == other.type and
                self.data == other.data)

    def get_form(self, hero, data=None):
        return self.effect.get_form(card=self, hero=hero, data=data)

    def get_dialog_info(self, hero):
        return self.effect.get_dialog_info(card=self, hero=hero)
