# coding: utf-8

import datetime

import rels
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c

class BILL_STATE(DjangoEnum):
    records = ( ('VOTING', 1, u'на голосовании'),
                 ('ACCEPTED', 2, u'принят'),
                 ('REJECTED', 3, u'отклонён'),
                 ('REMOVED', 4, u'удалён'))


class BILL_TYPE(DjangoEnum):
    stability = rels.Column(unique=False)

    records = ( ('PLACE_RENAMING', 0, u'переименование города',                  0.15),
                ('PERSON_REMOVE', 1, u'исключить горожанина из Совета',          0.10),
                ('PLACE_DESCRIPTION', 2, u'изменить описание города',            0.04),
                ('PLACE_MODIFIER', 3, u'изменить специализацию города',          0.04),
                ('BUILDING_CREATE', 4, u'возвести постройку',                    0.04),
                ('BUILDING_DESTROY', 5, u'разрушить постройку',                  0.10),
                ('BUILDING_RENAMING', 6, u'переименовать постройку',             0.02),
                ('PLACE_RESOURCE_EXCHANGE', 7, u'обмен ресурсами',               0.10),
                ('BILL_DECLINE', 8, u'отмена закона',                            0.10),
                ('PLACE_RESOURCE_CONVERSION', 9, u'изменение параметров города', 0.10),
                ('PERSON_CHRONICLE', 10, u'запись в летописи о советнике',       0.02),
                ('PLACE_CHRONICLE', 11, u'запись в летописи о городе',           0.02),
                )


class VOTE_TYPE(DjangoEnum):
    records = (('REFRAINED', 0, u'воздержался'),
               ('FOR', 1, u'«за»'),
               ('AGAINST', 2, u'«против»'))

class VOTED_TYPE(DjangoEnum):
    vote_type = rels.Column(unique=False, single_type=False)

    records = (('NO', 'no', u'не голосовал', None),
               ('YES', 'yes', u'проголосовал', None),
               ('FOR', 'for', u'«за»', VOTE_TYPE.FOR),
               ('AGAINST', 'against', u'«против»', VOTE_TYPE.AGAINST),
               ('REFRAINED', 'refrained', u'«воздержался»', VOTE_TYPE.REFRAINED) )


def days_from_game_months(months):
    delta = datetime.timedelta(seconds=months * c.TURNS_IN_GAME_MONTH * c.TURN_DELTA)
    return delta.total_seconds() / (60*60*24.0)

class BILL_DURATION(DjangoEnum):
    game_months = rels.Column()

    records = ( ('UNLIMITED', 0, u'бесконечно', 0),
                ('MONTH',     1, u'1 месяц (реальных дней: %.1f)' % days_from_game_months(1), 1),
                ('MONTH_2',   2, u'2 месяца (реальных дней: %.1f)' % days_from_game_months(2), 2),
                ('MONTH_3',   3, u'3 месяца (реальных дней: %.1f)' % days_from_game_months(3), 3),
                ('YEAR',      4, u'1 год (реальных дней: %.1f)' % days_from_game_months(4), 4),
                ('YEAR_1_5',  5, u'1,5 года (реальных дней: %.1f)' % days_from_game_months(6), 6),
                ('YEAR_2',    6, u'2 года (реальных дней: %.1f)' % days_from_game_months(8), 8),
                ('YEAR_3',    7, u'3 года (реальных дней: %.1f)' % days_from_game_months(12), 12),
                ('YEAR_5',    8, u'5 лет (реальных дней: %.1f)' % days_from_game_months(20), 20),
                ('YEAR_10',   9, u'10 лет (реальных дней: %.1f)' % days_from_game_months(40), 40) )


class POWER_BONUS_CHANGES(DjangoEnum):
    bonus_delta = rels.Column()

    BONUS_MULTIPLIER = 50

    records = ( ('DOWN', 0, u'уменьшить на %.2f%%' % (c.HERO_POWER_BONUS*100*BONUS_MULTIPLIER), -c.HERO_POWER_BONUS*BONUS_MULTIPLIER),
                ('NOT_CHANGE', 1, u'не изменять', 0.0),
                ('UP', 2, u'увеличить на %.2f%%' % (c.HERO_POWER_BONUS*100*BONUS_MULTIPLIER), c.HERO_POWER_BONUS*BONUS_MULTIPLIER) )
