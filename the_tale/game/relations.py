# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from pynames.relations import GENDER as PYNAMES_GENDER

from the_tale.game.balance import enums as e


class GENDER(DjangoEnum):
    text_id = Column()
    pynames_id = Column(unique=False)

    records = ( ('MASCULINE', 0, u'мужчина', u'мр', PYNAMES_GENDER.MALE),
                 ('FEMININE', 1, u'женщина', u'жр', PYNAMES_GENDER.FEMALE),
                 ('NEUTER', 2, u'оно', u'ср', PYNAMES_GENDER.MALE) )



class RACE(DjangoEnum):
    multiple_text = Column()
    energy_regeneration = Column()

    records = ( ('HUMAN', 0, u'человек', u'люди', e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY),
                 ('ELF', 1, u'эльф', u'эльфы', e.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE),
                 ('ORC', 2, u'орк',  u'орки', e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE),
                 ('GOBLIN', 3, u'гоблин', u'гоблины', e.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION),
                 ('DWARF', 4, u'дварф', u'дварфы', e.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS) )
