# coding: utf-8

from rels.django import DjangoEnum


class ABILITY_TYPE(DjangoEnum):
    records = ( ('BATTLE', 0, u'боевая'),
                ('NONBATTLE', 1, u'мирная'),
                ('COMPANION', 2, u'для спутника'))


class ABILITY_ACTIVATION_TYPE(DjangoEnum):
    records = ( ('ACTIVE', 0, u'активная'),
                ('PASSIVE', 1, u'пассивная'), )


class ABILITY_LOGIC_TYPE(DjangoEnum):
    records = ( ('WITHOUT_CONTACT', 0, u'безконтактная'),
                ('WITH_CONTACT', 1, u'контактная'), )


class ABILITY_AVAILABILITY(DjangoEnum):
   records = ( ('FOR_PLAYERS', 0b0001, u'только для игроков'),
               ('FOR_MONSTERS', 0b0010, u'только для монстров'),
               ('FOR_ALL', 0b0011, u'для всех') )
