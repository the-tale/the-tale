# coding: utf-8

from the_tale.market import goods_types


class CardGoodType(goods_types.BaseGoodType):
    pass


CardGoodType(uid='card',
             name=u'Карты Судьбы',
             description='Карты Судьбы').register()
