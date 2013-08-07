# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum


class MEMBER_ROLE(DjangoEnum):
    _records = ( ('LEADER', 0, u'лидер'),
                 ('MEMBER', 1, u'рядовой') )



class ORDER_BY(DjangoEnum):
    order_field = Column()

    _records = ( ('NAME', 0, u'имени', 'name'),
                 ('ABBR', 1, u'аббревиатуре', 'abbr'),
                 ('MEMBERS_NUMBER', 2, u'количеству героев', 'members_number'),
                 ('CREATED_AT', 3, u'дате создания', 'created_at'),)


class MEMBERSHIP_REQUEST_TYPE(DjangoEnum):
    _records = ( ('FROM_CLAN', 0, u'от клана'),
                 ('FROM_ACCOUNT', 1, u'от аккаунта') )



class PAGE_ID(DjangoEnum):
    _records = ( ('INDEX', 0, u'индексная страница'),
                 ('NEW', 1, u'создание клана'),
                 ('SHOW', 2, u'страница клана'),
                 ('EDIT', 3, u'редактирование клана'),
                 ('FOR_CLAN', 4, u'заявки в клан'),
                 ('FOR_ACCOUNT', 5, u'предложения вступить в клан'))
