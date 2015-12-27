# coding: utf-8

from . import relations

from the_tale.game.balance import constants as c


class Attributes(object):
    __slots__ = tuple([record.name.lower() for record in relations.ATTRIBUTES.records])

    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

        for attribute in relations.ATTRIBUTES.records:
            if not hasattr(self, attribute.name.lower()):
                setattr(self, attribute.name.lower(), attribute.default())

    def serialize(self):
        return {name: getattr(self, name) for name in self.__slots__}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    def reset(self):
        for attribute in relations.ATTRIBUTES.records:
            setattr(self, attribute.name.lower(), attribute.default())

    def sync_size(self, hours):

        self.goods += hours * self.production
        self.keepers_goods -= self.get_next_keepers_goods_spend_amount()

        if self.goods >= c.PLACE_GOODS_TO_LEVEL:
            self.size += 1
            if self.size <= c.PLACE_MAX_SIZE:
                self.goods = int(c.PLACE_GOODS_TO_LEVEL * c.PLACE_GOODS_AFTER_LEVEL_UP)
            else:
                self.size = c.PLACE_MAX_SIZE
                self.goods = c.PLACE_GOODS_TO_LEVEL
        elif self.goods <= 0:
            self.size -= 1
            if self.size > 0:
                self.goods = int(c.PLACE_GOODS_TO_LEVEL * c.PLACE_GOODS_AFTER_LEVEL_DOWN)
            else:
                self.size = 1
                self.goods = 0

    def get_next_keepers_goods_spend_amount(self):
        return min(self.keepers_goods, max(int(self.keepers_goods * c.PLACE_KEEPERS_GOODS_SPENDING), c.PLACE_GOODS_BONUS))
