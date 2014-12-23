# coding: utf-8

from the_tale.game.cards import relations


class Card(object):

    __slots__ = ('uid', 'type', 'available_for_auction')

    def __init__(self, type, available_for_auction=False, uid=None):
        self.uid = uid
        self.type = type
        self.available_for_auction = available_for_auction


    def serialize(self):
        return {'uid': self.uid,
                'type': self.type.value,
                'auction': self.available_for_auction}

    @classmethod
    def deserialize(cls, data):
        return cls(uid=data['uid'], type=relations.CARD_TYPE(data['type']), available_for_auction=data['auction'])
