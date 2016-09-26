# coding: utf-8

from rels.django import DjangoEnum


class ABILITY_TYPE(DjangoEnum):
    records = ( ('BATTLE', 0, 'боевая'),
                ('NONBATTLE', 1, 'мирная'),
                ('COMPANION', 2, 'для спутника'))


class ABILITY_ACTIVATION_TYPE(DjangoEnum):
    records = ( ('ACTIVE', 0, 'активная'),
                ('PASSIVE', 1, 'пассивная'), )


class ABILITY_LOGIC_TYPE(DjangoEnum):
    records = ( ('WITHOUT_CONTACT', 0, 'безконтактная'),
                ('WITH_CONTACT', 1, 'контактная'), )


class ABILITY_AVAILABILITY(DjangoEnum):
   records = ( ('FOR_PLAYERS', 0b0001, 'только для игроков'),
               ('FOR_MONSTERS', 0b0010, 'только для монстров'),
               ('FOR_ALL', 0b0011, 'для всех') )
