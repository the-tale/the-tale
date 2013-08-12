# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum


class PERMANENT_PURCHASE_TYPE(DjangoEnum):
    description = Column()
    _records = ( ('CLAN_OWNERSHIP_RIGHT', 0, u'Разрешение на владение гильдией', u'Если вам не хватает могущества для владения гильдией, Вы можете приобрести разрешение на владение ей за печеньки.'),
                 )
