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


class RANDOM_PREMIUM_REQUEST_STATE(DjangoEnum):
    records = ( ('WAITING', 0, u'ожидает обработки'),
                ('PROCESSED',  1, u'обработана') )


class MIGHT_AMOUNT(DjangoEnum):
    amount = Column(unique=False, single_type=False)
    award = Column(unique=False, single_type=False)

    records = ( ('FOR_FORUM_POST', 0, u'за сообщение на форуме', 0.3, None),
                ('FOR_FORUM_THREAD', 2, u'со обсуждение на форуме', 3, None),
                ('FOR_BILL_VOTE', 3, u'за отданый голос', 1, None),
                ('FOR_BILL_ACCEPTED', 4, u'за принятый закон', 33, None),
                ('FOR_GOOD_FOLCLOR_POST', 5, u'за фольклорное произведение', 100, None),
                ('FOR_ADDED_WORD', 6, u'за слово в лингвистике', 5, None),
                ('FOR_ADDED_TEMPLATE', 7, u'за фразу в лингвистике', 15, None),
                ('AWARD_BUG_MINOR', 8, u'за небольшую ошибку', 111, AWARD_TYPE.BUG_MINOR),
                ('AWARD_BUG_NORMAL', 9, u'за среднюю ошибку', 222, AWARD_TYPE.BUG_NORMAL),
                ('AWARD_BUG_MAJOR', 10, u'за существенную ошибку', 333, AWARD_TYPE.BUG_MAJOR),
                ('AWARD_CONTEST_1_PLACE', 11, u'за 1-ое место в конкурсе', 1000, AWARD_TYPE.CONTEST_1_PLACE),
                ('AWARD_CONTEST_2_PLACE', 12, u'за 2-ое место в конкурсе', 666, AWARD_TYPE.CONTEST_2_PLACE),
                ('AWARD_CONTEST_3_PLACE', 13, u'за 3-е место в конкурсе', 333, AWARD_TYPE.CONTEST_3_PLACE),
                ('AWARD_STANDARD_MINOR', 14, u'обычная маленька награда', 333, AWARD_TYPE.STANDARD_MINOR),
                ('AWARD_STANDARD_NORMAL', 15, u'обычная средняя награда', 666, AWARD_TYPE.STANDARD_NORMAL),
                ('AWARD_STANDARD_MAJOR', 16, u'обычная большая награда', 1000, AWARD_TYPE.STANDARD_MAJOR) )
