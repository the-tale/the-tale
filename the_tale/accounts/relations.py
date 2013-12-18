# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class AWARD_TYPE(DjangoEnum):

    records = ( ('BUG_MINOR', 0, u'найдена ошибка: небольшая'),
                 ('BUG_NORMAL', 1, u'найдена ошибка: обычная'),
                 ('BUG_MAJOR', 2, u'найдена ошибка: существенная'),
                 ('CONTEST_1_PLACE', 3, u'конкурс: 1-ое место'),
                 ('CONTEST_2_PLACE', 4, u'конкурс: 2-ое место'),
                 ('CONTEST_3_PLACE', 5, u'конкурс: 3-е место'),
                 ('STANDARD_MINOR', 6, u'стандартная награда: небольшая'),
                 ('STANDARD_NORMAL', 7, u'стандартная награда: обычная'),
                 ('STANDARD_MAJOR', 8, u'стандартная награда: существенная') )

class CHANGE_CREDENTIALS_TASK_STATE(DjangoEnum):
    records = ( ('WAITING', 0, u'ожидает обработки'),
                 ('EMAIL_SENT', 1, u'отослано письмо'),
                 ('PROCESSED', 2, u'обработана'),
                 ('UNPROCESSED', 3, u'не обработана'),
                 ('ERROR', 4, u'ошибка'),
                 ('TIMEOUT', 5, u'таймаут'),
                 ('CHANGING', 6, u'применяются изменения'))


class BAN_TYPE(DjangoEnum):
    records = ( ('FORUM', 0, u'запрет общения'),
                 ('GAME',  1, u'запрет игры'),
                 ('TOTAL', 2, u'запрет всего'),)

class BAN_TIME(DjangoEnum):
    days = Column()

    records = ( ('1_DAY', 0, u'1 день', 1),
                ('2_DAYS', 1, u'2 дня', 2),
                ('3_DAYS', 2, u'3 дня', 3),
                ('WEEK', 3, u'неделя', 7),
                ('MONTH', 4, u'месяц', 30),
                ('HALF_YEAR', 5, u'полгода', 180),
                ('TOTAL', 6, u'пожизненно', 365*666))
