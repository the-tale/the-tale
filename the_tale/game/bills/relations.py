# coding: utf-8

import datetime

import rels
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c

class BILL_STATE(DjangoEnum):
    records = ( ('VOTING', 1, u'на голосовании'),
                ('ACCEPTED', 2, u'принят'),
                ('REJECTED', 3, u'отклонён'),
                ('REMOVED', 4, u'удалён'),
                ('STOPPED', 5, u'потерял смысл'))


class BILL_TYPE(DjangoEnum):
    stability = rels.Column(unique=False, single_type=False)
    enabled = rels.Column(unique=False)

    records = ( ('PLACE_RENAMING', 0, u'переименование города',                  1.5 * c.PLACE_STABILITY_UNIT, True),
                ('PERSON_REMOVE', 1, u'исключить горожанина из Совета',          None, False),
                ('PLACE_DESCRIPTION', 2, u'изменить описание города',            0.4 * c.PLACE_STABILITY_UNIT, True),
                ('PLACE_CHANGE_MODIFIER', 3, u'изменить специализацию города',   0.4 * c.PLACE_STABILITY_UNIT, True),
                ('BUILDING_CREATE', 4, u'возвести постройку',                    0.4 * c.PLACE_STABILITY_UNIT, True),
                ('BUILDING_DESTROY', 5, u'разрушить постройку',                  1.0 * c.PLACE_STABILITY_UNIT, True),
                ('BUILDING_RENAMING', 6, u'переименовать постройку',             0.2 * c.PLACE_STABILITY_UNIT, True),
                ('PLACE_RESOURCE_EXCHANGE', 7, u'обмен ресурсами',               0.8 * c.PLACE_STABILITY_UNIT, True),
                ('BILL_DECLINE', 8, u'отмена закона',                            0.4 * c.PLACE_STABILITY_UNIT, True),
                ('PLACE_RESOURCE_CONVERSION', 9, u'изменение параметров города', 0.8 * c.PLACE_STABILITY_UNIT, True),
                ('PERSON_CHRONICLE', 10, u'запись в летописи о Мастере'  ,       0.2 * c.PLACE_STABILITY_UNIT, True),
                ('PLACE_CHRONICLE', 11, u'запись в летописи о городе',           0.2 * c.PLACE_STABILITY_UNIT, True),
                ('PERSON_MOVE', 12, u'переезд Мастера',                          2.0 * c.PLACE_STABILITY_UNIT, True),
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


class POWER_BONUS_CHANGES(DjangoEnum):
    bonus = rels.Column()

    BONUS = c.HERO_POWER_PER_DAY*4*4*4 # like 4-th grade power card

    records = ( ('DOWN', 0, u'уменьшить на %d' % BONUS, -BONUS),
                ('NOT_CHANGE', 1, u'не изменять', 0),
                ('UP', 2, u'увеличить на %d' % BONUS, BONUS) )
