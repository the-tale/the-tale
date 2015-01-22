# coding: utf-8

from the_tale.game.cards import relations


class Card(object):

    __slots__ = ('uid', 'type', 'available_for_auction', 'data')

    def __init__(self, type, available_for_auction=False, uid=None, data=None):
        self.uid = uid
        self.type = type
        self.available_for_auction = available_for_auction
        self.data = data

    @property
    def name(self):
        return self.effect.name_for_card(self)

    def serialize(self):
        return {'uid': self.uid,
                'type': self.type.value,
                'auction': self.available_for_auction,
                'data': self.data}

    @classmethod
    def deserialize(cls, data):
        return cls(uid=data['uid'],
                   type=relations.CARD_TYPE(data['type']),
                   available_for_auction=data['auction'],
                   data=data.get('data'))

    @property
    def effect(self):
        from the_tale.game.cards import effects
        return effects.EFFECTS[self.type]

    def activate(self, hero, data):
        return self.effect.activate(hero, card_uid=self.uid, data=data)

    def ui_info(self):
        return {'name': self.name,
                'description': self.effect.DESCRIPTION,
                'rarity': self.type.rarity.value,
                'uid': self.uid,
                'auction': self.available_for_auction}


    def __eq__(self, other):
        return (self.uid == other.uid and
                self.type == other.type and
                self.available_for_auction == other.available_for_auction)


    def __ne__(self, other):
        return not self.__eq__(other)
