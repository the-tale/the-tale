# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum


class PREFERENCE_TYPE(DjangoEnum):
    level_required = Column()

    _records = ( ('MOB', 0, u'любимая добыча', 7),
                 ('PLACE', 1, u'родной город', 3),
                 ('FRIEND', 2, u'соратник', 11),
                 ('ENEMY', 3, u'враг', 16),
                 ('ENERGY_REGENERATION_TYPE', 4, u'религиозность', 1),
                 ('EQUIPMENT_SLOT', 5, u'экипировка', 21) )
