# coding: utf-8

from rels.django_staff import DjangoEnum


class ABILITY_TYPE(DjangoEnum):
    _records = ( ('BATTLE', 0, u'боевая'),
                 ('NONBATTLE', 1, u'небоевая'),)


class ABILITY_ACTIVATION_TYPE(DjangoEnum):
    _records = ( ('ACTIVE', 0, u'активная'),
                 ('PASSIVE', 1, u'пассивная'), )


class ABILITY_LOGIC_TYPE(DjangoEnum):
    _records = ( ('WITHOUT_CONTACT', 0, u'безконтактная'),
                 ('WITH_CONTACT', 1, u'контактная'), )


class ABILITY_AVAILABILITY(DjangoEnum):
   _records = ( ('FOR_PLAYERS', 0b0001, u'только для игроков'),
                ('FOR_MONSTERS', 0b0010, u'только для монстров'),
                ('FOR_ALL', 0b0011, u'для всех') )


class DAMAGE_TYPE(DjangoEnum):
   _records = ( ('PHYSICAL', 0b0001, u'физический'),
                ('MAGICAL', 0b0010, u'магический'),
                ('MIXED', 0b0011, u'смешанный') )
