# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class AWARD_TYPE(DjangoEnum):

    records = ( ('BUG_MINOR', 0, 'найдена ошибка: небольшая'),
                ('BUG_NORMAL', 1, 'найдена ошибка: обычная'),
                ('BUG_MAJOR', 2, 'найдена ошибка: существенная'),
                ('CONTEST_1_PLACE', 3, 'конкурс: 1-ое место'),
                ('CONTEST_2_PLACE', 4, 'конкурс: 2-ое место'),
                ('CONTEST_3_PLACE', 5, 'конкурс: 3-е место'),
                ('STANDARD_MINOR', 6, 'стандартная награда: небольшая'),
                ('STANDARD_NORMAL', 7, 'стандартная награда: обычная'),
                ('STANDARD_MAJOR', 8, 'стандартная награда: существенная') )

class CHANGE_CREDENTIALS_TASK_STATE(DjangoEnum):
    records = ( ('WAITING', 0, 'ожидает обработки'),
                ('EMAIL_SENT', 1, 'отослано письмо'),
                ('PROCESSED', 2, 'обработана'),
                ('UNPROCESSED', 3, 'не обработана'),
                ('ERROR', 4, 'ошибка'),
                ('TIMEOUT', 5, 'таймаут'),
                ('CHANGING', 6, 'применяются изменения'))


class BAN_TYPE(DjangoEnum):
    records = ( ('FORUM', 0, 'запрет общения'),
                ('GAME',  1, 'запрет игры'),
                ('TOTAL', 2, 'запрет всего'),)

class BAN_TIME(DjangoEnum):
    days = Column()

    records = ( ('1_DAY', 0, '1 день', 1),
                ('2_DAYS', 1, '2 дня', 2),
                ('3_DAYS', 2, '3 дня', 3),
                ('WEEK', 3, 'неделя', 7),
                ('MONTH', 4, 'месяц', 30),
                ('HALF_YEAR', 5, 'полгода', 180),
                ('TOTAL', 6, 'пожизненно', 365*666))


class RANDOM_PREMIUM_REQUEST_STATE(DjangoEnum):
    records = ( ('WAITING', 0, 'ожидает обработки'),
                ('PROCESSED',  1, 'обработана') )


class MIGHT_AMOUNT(DjangoEnum):
    amount = Column(unique=False, single_type=False)
    award = Column(unique=False, single_type=False, no_index=False)

    records = ( ('FOR_FORUM_POST', 0, 'за сообщение на форуме', 0.3, None),
                ('FOR_FORUM_THREAD', 2, 'со обсуждение на форуме', 3, None),
                ('FOR_BILL_VOTE', 3, 'за отданый голос', 1, None),
                ('FOR_BILL_ACCEPTED', 4, 'за принятую запись в Книге Судеб', 33, None),
                ('FOR_MIN_FOLCLOR_POST', 5, 'за фольклорное произведение', 20, None),
                ('FOR_ADDED_WORD_FOR_PLAYER', 6, 'за слово в лингвистике для игрока', 5, None),
                ('FOR_ADDED_WORD_FOR_MODERATOR', 7, 'за слово в лингвистике для модератора', 5, None),
                ('FOR_ADDED_TEMPLATE_FOR_PLAYER', 8, 'за фразу в лингвистике для игрока', 15, None),
                ('FOR_ADDED_TEMPLATE_FOR_MODERATOR', 9, 'за фразу в лингвистике для модератора', 15, None),
                ('AWARD_BUG_MINOR', 10, 'за небольшую ошибку', 111, AWARD_TYPE.BUG_MINOR),
                ('AWARD_BUG_NORMAL', 11, 'за среднюю ошибку', 222, AWARD_TYPE.BUG_NORMAL),
                ('AWARD_BUG_MAJOR', 12, 'за существенную ошибку', 333, AWARD_TYPE.BUG_MAJOR),
                ('AWARD_CONTEST_1_PLACE', 13, 'за 1-ое место в конкурсе', 1000, AWARD_TYPE.CONTEST_1_PLACE),
                ('AWARD_CONTEST_2_PLACE', 14, 'за 2-ое место в конкурсе', 666, AWARD_TYPE.CONTEST_2_PLACE),
                ('AWARD_CONTEST_3_PLACE', 15, 'за 3-е место в конкурсе', 333, AWARD_TYPE.CONTEST_3_PLACE),
                ('AWARD_STANDARD_MINOR', 16, 'обычная маленька награда', 333, AWARD_TYPE.STANDARD_MINOR),
                ('AWARD_STANDARD_NORMAL', 17, 'обычная средняя награда', 666, AWARD_TYPE.STANDARD_NORMAL),
                ('AWARD_STANDARD_MAJOR', 18, 'обычная большая награда', 1000, AWARD_TYPE.STANDARD_MAJOR) )
