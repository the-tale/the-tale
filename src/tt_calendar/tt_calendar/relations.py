
import datetime

import rels


class MONTH(rels.EnumWithText):
    date_text = rels.Column()

    records = (('DRY',   0, 'сухой месяц',    'сухого месяца'),
               ('HOT',   1, 'жаркий месяц',   'жаркого месяца'),
               ('CRUDE', 2, 'сырой месяц',    'сырого месяца'),
               ('COLD',  3, 'холодный месяц', 'холодного месяца'))


class QUINT(rels.EnumWithText):
    date_text = rels.Column()

    records = (('YOUNG',  0, 'юный квинт',     'юного квинта'),
               ('MATURE', 1, 'зрелый квинт',   'зрелого квинта'),
               ('ADULT',  2, 'взрослый квинт', 'взрослого квинта'),
               ('WISE',   3, 'мудрый квинт',   'мудрого квинта'),
               ('OLD',    4, 'старый квинт',   'старого квинта'),
               ('DEAD',   5, 'мёртвый квинт',  'мёртвого квинта'),)


class QUINT_DAY(rels.EnumWithText):
    date_text = rels.Column()

    records = (('DAY_1',   0,  '1',      '1'),
               ('DAY_2',   1,  '2',      '2'),
               ('DAY_3',   2,  '3',      '3'),
               ('DAY_4',   3,  '4',      '4'),
               ('DAY_5',   4,  '5',      '5'),
               ('DAY_6',   5,  '6',      '6'),
               ('DAY_7',   6,  '7',      '7'),
               ('DAY_8',   7,  '8',      '8'),
               ('DAY_9',   8,  '9',      '9'),
               ('DAY_10',  9,  '10',     '10'),
               ('DAY_11',  10, '11',     '11'),
               ('DAY_12',  11, '12',     '12'),
               ('DAY_13',  12, '13',     '13'),
               ('DAY_14',  13, '14',     '14'),
               ('DAY_15',  14, '15',     '15'))


class REAL_FEAST(rels.EnumWithText):
    intervals = rels.Column(no_index=True, unique=False)

    records = (('JESTER_DAYS', 0, 'Дни шута (с 31-ого марта по 2-ого апреля)',
                [(datetime.datetime(year=datetime.MINYEAR, month=3, day=31), datetime.datetime(year=datetime.MINYEAR, month=4, day=2))]),
               ('GREAT_EXALTATION', 1, 'Великосвершенье (с 30-ого декабря по 2-ого января)',
                [(datetime.datetime(year=datetime.MINYEAR, month=12, day=30), datetime.datetime(year=datetime.MINYEAR, month=12, day=31)),
                 (datetime.datetime(year=datetime.MINYEAR, month=1, day=1), datetime.datetime(year=datetime.MINYEAR, month=1, day=2))]),)


class DATE(rels.EnumWithText):
    intervals = rels.Column(no_index=True, unique=False)

    records = (('NEW_YEAR', 0, 'Новый год',
                [((0, 0), (0, 0))]),
               ('KEEPERS_DAY', 1, 'Хранимый День',
                [((0, 59), (0, 59))]),
               ('HEROES_DAY', 2, 'Героев День',
                [((1, 31), (1, 31))]),
               ('HARVEST_FESTIVAL', 3, 'Праздник урожая',
                [((2, 19), (2, 19))]),
               ('PRECONVERGENCE', 4, 'Предсхождение',
                [((2, 59), (2, 59))]),
               ('CONVERGENCE', 5, 'Схождение',
                [((2, 60), (2, 88))]),
               ('DEAD_NIGHT', 6, 'Мёртвая ночь',
                [((3, 53), (3, 54))]),
               ('REMEMBRANCE_OF_THE_FIRST', 7, 'Помин Первых',
                [((3, 88), (3, 88))]))


class PHYSICS_DATE(rels.EnumWithText):
    intervals = rels.Column(no_index=True, unique=False)

    records = (('FULL_MOON', 0, 'Полнолуние',
                [((0, 42), (0, 47)),
                 ((1, 42), (1, 47)),
                 ((2, 42), (2, 47)),
                 ((3, 42), (3, 47))]),
               ('NEW_MOON', 1, 'Новолуние',
                [((0, 88), (1, 1)),
                 ((1, 88), (2, 1)),
                 ((2, 88), (3, 1)),
                 ((3, 88), (3, 89)),
                 ((1, 0), (1, 1))]),
               ('EQUINOX', 2, 'Равноденствие',
                [((0, 45), (0, 45)),
                 ((2, 45), (2, 45))]),
               ('SOLSTICE', 3, 'Солнцестояние',
                [((1, 45), (1, 45)),
                 ((3, 45), (3, 45))]))


class DAY_TIME(rels.EnumWithText):
    records = (('DARK_TIME', 0, 'тёмное время'),
               ('LIGHT_TIME', 1, 'светлое время'),
               ('NIGHT', 2, 'ночь'),
               ('MORNING', 3, 'утро'),
               ('DAY', 4, 'день'),
               ('EVENING', 5, 'вечер'),
               ('DAWN', 6, 'рассвет'),
               ('SUNSET', 7, 'закат'))


class DAY_TYPE(rels.EnumWithText):
    records = (('WEEKDAY', 0, 'будний день'),
               ('DAY_OFF', 1, 'выходной день'))
