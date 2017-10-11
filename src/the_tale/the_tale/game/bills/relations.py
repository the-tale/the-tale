# coding: utf-8

import datetime

import rels
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c


class BILL_STATE(DjangoEnum):
    records = (('VOTING', 1, 'на голосовании'),
               ('ACCEPTED', 2, 'принята'),
               ('REJECTED', 3, 'отклонёна'),
               ('REMOVED', 4, 'удалена'),
               ('STOPPED', 5, 'потеряла смысл'))


class BILL_TYPE(DjangoEnum):
    stability = rels.Column(unique=False, single_type=False)
    enabled = rels.Column(unique=False)

    records = ( ('PLACE_RENAMING', 0, 'переименование города',                      1.5 * c.PLACE_STABILITY_UNIT, True),
                ('PERSON_REMOVE', 1, 'исключить горожанина из Совета',              None, False),
                ('PLACE_DESCRIPTION', 2, 'изменить описание города',                0.4 * c.PLACE_STABILITY_UNIT, True),
                ('PLACE_CHANGE_MODIFIER', 3, 'изменить специализацию города',       0.4 * c.PLACE_STABILITY_UNIT, True),
                ('BUILDING_CREATE', 4, 'возвести постройку',                        0.4 * c.PLACE_STABILITY_UNIT, True),
                ('BUILDING_DESTROY', 5, 'разрушить постройку',                      1.0 * c.PLACE_STABILITY_UNIT, True),
                ('BUILDING_RENAMING', 6, 'переименовать постройку',                 0.2 * c.PLACE_STABILITY_UNIT, True),
                ('PLACE_RESOURCE_EXCHANGE', 7, 'обмен ресурсами',                   0.8 * c.PLACE_STABILITY_UNIT, True),
                ('BILL_DECLINE', 8, 'отмена записи в Книге Судеб',                  0.4 * c.PLACE_STABILITY_UNIT, True),
                ('PLACE_RESOURCE_CONVERSION', 9, 'изменение параметров города',     0.8 * c.PLACE_STABILITY_UNIT, True),
                ('PERSON_CHRONICLE', 10, 'запись в летописи о Мастере'  ,           0.2 * c.PLACE_STABILITY_UNIT, True),
                ('PLACE_CHRONICLE', 11, 'запись в летописи о городе',               0.2 * c.PLACE_STABILITY_UNIT, True),
                ('PERSON_MOVE', 12, 'переезд Мастера',                              2.0 * c.PLACE_STABILITY_UNIT, True),
                ('PLACE_CHANGE_RACE', 13, 'изменить расу города',                   0.4 * c.PLACE_STABILITY_UNIT, True),
                ('PERSON_ADD_SOCIAL_CONNECTION', 14, 'добавить социальную связь',   0.6 * c.PLACE_STABILITY_UNIT, True),
                ('PERSON_REMOVE_SOCIAL_CONNECTION', 15, 'удалить социальную связь', 0.6 * c.PLACE_STABILITY_UNIT, True) )


class VOTE_TYPE(DjangoEnum):
    records = (('REFRAINED', 0, 'воздержался'),
               ('FOR', 1, '«за»'),
               ('AGAINST', 2, '«против»'))

class VOTED_TYPE(DjangoEnum):
    vote_type = rels.Column(unique=False, single_type=False)

    records = (('NO', 'no', 'не голосовал', None),
               ('YES', 'yes', 'проголосовал', None),
               ('FOR', 'for', '«за»', VOTE_TYPE.FOR),
               ('AGAINST', 'against', '«против»', VOTE_TYPE.AGAINST),
               ('REFRAINED', 'refrained', '«воздержался»', VOTE_TYPE.REFRAINED) )


def days_from_game_months(months):
    delta = datetime.timedelta(seconds=months * c.TURNS_IN_GAME_MONTH * c.TURN_DELTA)
    return delta.total_seconds() / (60*60*24.0)


class POWER_BONUS_CHANGES(DjangoEnum):
    bonus = rels.Column()

    BONUS = c.HERO_POWER_PER_DAY*4*4*4 # like 4-th grade power card

    records = ( ('DOWN', 0, 'уменьшить на %d' % BONUS, -BONUS),
                ('NOT_CHANGE', 1, 'не изменять', 0),
                ('UP', 2, 'увеличить на %d' % BONUS, BONUS) )
