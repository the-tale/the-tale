# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum


class MEMBER_ROLE(DjangoEnum):
    _records = ( ('LEADER', 0, u'лидер'),
                 ('DEPUTY', 1, u'заместитель'),
                 ('MEMBER', 2, u'рядовой') )


class ORDER_BY(DjangoEnum):
    order_field = Column()

    _records = ( ('NAME', 0, u'имени', 'name'),
                 ('ABBR', 1, u'аббревиатуре', 'abbr'),
                 ('MEMBERS_NUMBER', 2, u'количеству героев', 'members_number'),
                 ('CREATED_AT', 3, u'дате создания', 'created_at'),)
