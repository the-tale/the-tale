# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class MEMBER_ROLE(DjangoEnum):
    priority = Column()
    records = ( ('LEADER', 0, 'лидер', 0),
                 ('MEMBER', 1, 'рядовой', 1) )



class ORDER_BY(DjangoEnum):
    order_field = Column()

    records = ( ('NAME', 0, 'имени', 'name'),
                 ('ABBR', 1, 'аббревиатуре', 'abbr'),
                 ('MEMBERS_NUMBER', 2, 'количеству героев', 'members_number'),
                 ('CREATED_AT', 3, 'дате создания', 'created_at'),)


class MEMBERSHIP_REQUEST_TYPE(DjangoEnum):
    records = ( ('FROM_CLAN', 0, 'от гильдии'),
                 ('FROM_ACCOUNT', 1, 'от аккаунта') )



class PAGE_ID(DjangoEnum):
    records = ( ('INDEX', 0, 'индексная страница'),
                 ('NEW', 1, 'создание гильдии'),
                 ('SHOW', 2, 'страница гильдии'),
                 ('EDIT', 3, 'редактирование гильдии'),
                 ('FOR_CLAN', 4, 'заявки в гильдию'),
                 ('FOR_ACCOUNT', 5, 'предложения вступить в гильдию') )
