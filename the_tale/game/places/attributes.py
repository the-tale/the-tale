# coding: utf-8
import math

from . import relations

from the_tale.game.balance import constants as c
from the_tale.game import attributes

from . import modifiers
from . import relations


class Attributes(attributes.create_attributes_class(relations.ATTRIBUTE)):
    __slots__ = ()

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

        self.goods = int(self.goods)

    def sync(self):
        self.modifier_multiplier = (math.log(self.size, 2) + 1) / 1.7


    def set_power_economic(self, value):
        self.power_economic = value

    def get_next_keepers_goods_spend_amount(self):
        return min(self.keepers_goods, max(int(self.keepers_goods * c.PLACE_KEEPERS_GOODS_SPENDING), c.PLACE_GOODS_BONUS))

    def ui_specializations(self):
        specializations = [record
                           for record in modifiers.CITY_MODIFIERS.records
                           if not record.is_NONE]

        sorted_specializations = [(specialization, getattr(self, specialization.points_attribute.name.lower()))
                                  for specialization in specializations]

        sorted_specializations.sort(key=lambda x: -x[1])

        return sorted_specializations
