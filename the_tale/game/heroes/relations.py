# coding: utf-8

from rels.django_staff import DjangoEnum


class PREFERENCE_TYPE(DjangoEnum):
    _records = ( ('MOB', 0, u'любимая добыча'),
                 ('PLACE', 1, u'родной город'),
                 ('FRIEND', 2, u'соратник'),
                 ('ENEMY', 3, u'враг'),
                 ('ENERGY_REGENERATION_TYPE', 4, u'религиозность'),
                 ('EQUIPMENT_SLOT', 5, u'экипировка') )
