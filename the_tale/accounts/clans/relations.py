# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum


class MEMBER_ROLE(DjangoEnum):
    priority = Column()
    _records = ( ('LEADER', 0, u'лидер', 0),
                 ('MEMBER', 1, u'рядовой', 1) )



class ORDER_BY(DjangoEnum):
    order_field = Column()

    _records = ( ('NAME', 0, u'имени', 'name'),
                 ('ABBR', 1, u'аббревиатуре', 'abbr'),
                 ('MEMBERS_NUMBER', 2, u'количеству героев', 'members_number'),
                 ('CREATED_AT', 3, u'дате создания', 'created_at'),)


class MEMBERSHIP_REQUEST_TYPE(DjangoEnum):
    _records = ( ('FROM_CLAN', 0, u'от гильдии'),
                 ('FROM_ACCOUNT', 1, u'от аккаунта') )



class PAGE_ID(DjangoEnum):
    _records = ( ('INDEX', 0, u'индексная страница'),
                 ('NEW', 1, u'создание гильдии'),
                 ('SHOW', 2, u'страница гильдии'),
                 ('EDIT', 3, u'редактирование гильдии'),
                 ('FOR_CLAN', 4, u'заявки в гильдию'),
                 ('FOR_ACCOUNT', 5, u'предложения вступить в гильдию') )
