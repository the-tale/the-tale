
import smart_imports

smart_imports.all()


class ABILITY_TYPE(rels_django.DjangoEnum):
    records = (('BATTLE', 0, 'боевая'),
               ('NONBATTLE', 1, 'мирная'),
               ('COMPANION', 2, 'для спутника'))


class ABILITY_ACTIVATION_TYPE(rels_django.DjangoEnum):
    records = (('ACTIVE', 0, 'активная'),
               ('PASSIVE', 1, 'пассивная'))


class ABILITY_LOGIC_TYPE(rels_django.DjangoEnum):
    records = (('WITHOUT_CONTACT', 0, 'безконтактная'),
               ('WITH_CONTACT', 1, 'контактная'))


class ABILITY_AVAILABILITY(rels_django.DjangoEnum):
    records = (('FOR_PLAYERS', 0b0001, 'только для игроков'),
               ('FOR_MONSTERS', 0b0010, 'только для монстров'),
               ('FOR_ALL', 0b0011, 'для всех'))
