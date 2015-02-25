# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class LOT_STATE(DjangoEnum):
    records = ( ('RESERVED', 0, u'Лот зарезервирован'),
                ('ACTIVE', 1, u'Лот активен'),
                ('CLOSED_BY_SELLER', 2, u'Лот закрыт продавцом'),
                ('CLOSED_BY_TIMEOUT', 3, u'Лот закрыт по таймауту'),
                ('CLOSED_BY_BUYER', 4, u'Лот закрыт покупателем'),
                ('FROZEN', 5, u'Лот заморожен'),
                ('CLOSED_BY_ERROR', 6, u'Лот закрыт из-за ошибки в задаче создания'), )


class INDEX_ORDER_BY(DjangoEnum):
    db_order = Column()

    records = ( ('COST_UP', 0, u'по цене ↑', 'price'),
                ('NAME_UP', 1, u'по имени ↑', 'name'),
                ('DATE_UP', 2, u'по окончанию ↑', 'created_at'),
                ('COST_DOWN', 3, u'по цене ↓', '-price'),
                ('NAME_DOWN', 4, u'по имени ↓', '-name'),
                ('DATE_DOWN', 5, u'по окончанию ↓', '-created_at') )



class INDEX_MODE(DjangoEnum):
    page = Column()

    records = ( ('ALL', 0, u'все товары', 'index'),
                ('OWN', 1, u'товары игрока', 'own-lots'),
                ('HISTORY', 2, u'история', 'history') )
