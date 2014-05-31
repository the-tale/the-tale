# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from pynames.relations import GENDER as PYNAMES_GENDER

from the_tale.game.balance import enums as e
from the_tale.game.balance import constants as c


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


class GAME_STATE(DjangoEnum):

    records = ( ('STOPPED', 0, u'остановлена'),
                ('WORKING', 1, u'запущена')  )



class HABIT_INTERVAL(DjangoEnum):
    female_text = Column()
    neuter_text = Column()
    place_text = Column()
    left_border = Column()
    right_border = Column()


class HABIT_HONOR_INTERVAL(HABIT_INTERVAL):

    records = ( ('LEFT_3', 0, u'бесчестный', u'бесчестная', u'бесчестное', u'криминальная столица', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
                ('LEFT_2', 1, u'подлый', u'подлая', u'подлое', u'бандитская вотчина', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
                ('LEFT_1', 2, u'порочный', u'порочная', u'порочное', u'неблагополучный город', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
                ('NEUTRAL', 3, u'себе на уме', u'себе на уме', u'себе на уме', u'обычный город', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
                ('RIGHT_1', 4, u'порядочный', u'порядочная', u'порядочное', u'благополучное поселение', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
                ('RIGHT_2', 5, u'благородный', u'благородная', u'благородное', u'честный город', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
                ('RIGHT_3', 6, u'хозяин своего слова', u'хозяйка своего слова', u'хозяин своего слова', u'оплот благородства', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER) )


class HABIT_PEACEFULNESS_INTERVAL(HABIT_INTERVAL):
    records = ( ('LEFT_3', 0, u'скорый на расправу', u'скорая на расправу', u'скорое на расправу', u'территория вендетт', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
                ('LEFT_2', 1, u'вспыльчивый', u'вспыльчивая', u'вспыльчивое', u'пристанище горячих голов', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
                ('LEFT_1', 2, u'задира', u'задира', u'задира', u'беспокойной место', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
                ('NEUTRAL', 3, u'сдержанный', u'сдержанная', u'сдержаное', u'неприметное поселение', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
                ('RIGHT_1', 4, u'доброхот', u'доброхот', u'доброхот', u'спокойное место', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
                ('RIGHT_2', 5, u'миролюбивый', u'миролюбивая', u'миролюбивое', u'мирное поселение', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
                ('RIGHT_3', 6, u'гуманист', u'гуманист', u'гуманист', u'центр цивилизации', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER) )


class HABIT_TYPE(DjangoEnum):
    intervals = Column()

    records = ( ('HONOR', 0, u'честь', HABIT_HONOR_INTERVAL),
                ('PEACEFULNESS', 1, u'миролюбие', HABIT_PEACEFULNESS_INTERVAL) )
