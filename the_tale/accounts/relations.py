# coding: utf-8

from rels.django_staff import DjangoEnum


class AWARD_TYPE(DjangoEnum):

    _records = ( ('BUG_MINOR', 0, u'найдена ошибка: небольшая'),
                 ('BUG_NORMAL', 1, u'найдена ошибка: обычная'),
                 ('BUG_MAJOR', 2, u'найдена ошибка: существенная'),
                 ('CONTEST_1_PLACE', 3, u'конкурс: 1-ое место'),
                 ('CONTEST_2_PLACE', 4, u'конкурс: 2-ое место'),
                 ('CONTEST_3_PLACE', 5, u'конкурс: 3-е место'),
                 ('STANDARD_MINOR', 6, u'стандартная награда: небольшая'),
                 ('STANDARD_NORMAL', 7, u'стандартная награда: обычная'),
                 ('STANDARD_MAJOR', 8, u'стандартная награда: существенная') )

class CHANGE_CREDENTIALS_TASK_STATE(DjangoEnum):
    _records = ( ('WAITING', 0, u'ожидает обработки'),
                 ('EMAIL_SENT', 1, u'отослано письмо'),
                 ('PROCESSED', 2, u'обработана'),
                 ('UNPROCESSED', 3, u'не обработана'),
                 ('ERROR', 4, u'ошибка'),
                 ('TIMEOUT', 5, u'таймаут'),
                 ('CHANGING', 6, u'применяются изменения'))
