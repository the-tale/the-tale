# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class LOT_STATE(DjangoEnum):
    records = ( ('RESERVED', 0, 'Лот зарезервирован'),
                ('ACTIVE', 1, 'Лот активен'),
                ('CLOSED_BY_SELLER', 2, 'Лот закрыт продавцом'),
                ('CLOSED_BY_TIMEOUT', 3, 'Лот закрыт по таймауту'),
                ('CLOSED_BY_BUYER', 4, 'Лот закрыт покупателем'),
                ('FROZEN', 5, 'Лот заморожен'),
                ('CLOSED_BY_ERROR', 6, 'Лот закрыт из-за ошибки в задаче создания'), )


class INDEX_ORDER_BY(DjangoEnum):
    db_order = Column()

    records = ( ('COST_UP', 0, 'по цене ↑', 'price'),
                ('NAME_UP', 1, 'по имени ↑', 'name'),
                ('DATE_UP', 2, 'по окончанию ↑', 'closed_at'),
                ('COST_DOWN', 3, 'по цене ↓', '-price'),
                ('NAME_DOWN', 4, 'по имени ↓', '-name'),
                ('DATE_DOWN', 5, 'по окончанию ↓', '-closed_at') )



class INDEX_MODE(DjangoEnum):
    page = Column()

    records = ( ('ALL', 0, 'все товары', 'index'),
                ('OWN', 1, 'товары игрока', 'own-lots'),
                ('HISTORY', 2, 'история', 'market-history') )
