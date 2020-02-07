
import smart_imports

smart_imports.all()


class BILL_STATE(rels_django.DjangoEnum):
    break_dependent_bills = rels.Column(unique=False)

    records = (('VOTING', 1, 'на голосовании', False),
               ('ACCEPTED', 2, 'принята', False),
               ('REJECTED', 3, 'отклонена', True),
               ('REMOVED', 4, 'удалена', True),
               ('STOPPED', 5, 'потеряла смысл', True))


class BILL_TYPE(rels_django.DjangoEnum):
    stability = rels.Column(unique=False, single_type=False)
    enabled = rels.Column(unique=False)

    records = (('PLACE_RENAMING', 0, 'переименование города', 1.5 * c.PLACE_STABILITY_UNIT, True),
               ('PERSON_REMOVE', 1, 'исключить горожанина из Совета', None, False),
               ('PLACE_DESCRIPTION', 2, 'изменить описание города', 0.4 * c.PLACE_STABILITY_UNIT, True),
               ('PLACE_CHANGE_MODIFIER', 3, 'изменить специализацию города', 0.4 * c.PLACE_STABILITY_UNIT, True),
               ('BUILDING_CREATE', 4, 'возвести постройку', 0.4 * c.PLACE_STABILITY_UNIT, True),
               ('BUILDING_DESTROY', 5, 'разрушить постройку', 1.0 * c.PLACE_STABILITY_UNIT, True),
               ('BUILDING_RENAMING', 6, 'переименовать постройку', 0.2 * c.PLACE_STABILITY_UNIT, True),
               ('PLACE_RESOURCE_EXCHANGE', 7, 'обмен ресурсами', 0.8 * c.PLACE_STABILITY_UNIT, True),
               ('BILL_DECLINE', 8, 'отмена записи в Книге Судеб', 0.4 * c.PLACE_STABILITY_UNIT, True),
               ('PLACE_RESOURCE_CONVERSION', 9, 'изменение параметров города', 0.8 * c.PLACE_STABILITY_UNIT, True),
               ('PERSON_CHRONICLE', 10, 'запись в летописи о Мастере', 0, True),
               ('PLACE_CHRONICLE', 11, 'запись в летописи о городе', 0, True),
               ('PERSON_MOVE', 12, 'переезд Мастера', 2.0 * c.PLACE_STABILITY_UNIT, True),
               ('PLACE_CHANGE_RACE', 13, 'изменить расу города', 0.4 * c.PLACE_STABILITY_UNIT, True),
               ('PERSON_ADD_SOCIAL_CONNECTION', 14, 'добавить социальную связь', 0.6 * c.PLACE_STABILITY_UNIT, True),
               ('PERSON_REMOVE_SOCIAL_CONNECTION', 15, 'удалить социальную связь', 0.6 * c.PLACE_STABILITY_UNIT, True),
               ('ROAD_CREATE', 16, 'проложить дорогу', 3.0 * c.PLACE_STABILITY_UNIT, True),
               ('ROAD_DESTROY', 17, 'разрушить дорогу', 4.0 * c.PLACE_STABILITY_UNIT, True),
               ('ROAD_CHANGE', 18, 'изменить дорогу', 2.0 * c.PLACE_STABILITY_UNIT, True),
               ('EMISSARY_CHRONICLE', 19, 'запись в летописи об эмиссаре', 0, True),)


class VOTE_TYPE(rels_django.DjangoEnum):
    records = (('REFRAINED', 0, 'воздержался'),
               ('FOR', 1, '«за»'),
               ('AGAINST', 2, '«против»'))


class VOTED_TYPE(rels_django.DjangoEnum):
    vote_type = rels.Column(unique=False, single_type=False)

    records = (('NO', 'no', 'не голосовал', None),
               ('YES', 'yes', 'проголосовал', None),
               ('FOR', 'for', '«за»', VOTE_TYPE.FOR),
               ('AGAINST', 'against', '«против»', VOTE_TYPE.AGAINST),
               ('REFRAINED', 'refrained', '«воздержался»', VOTE_TYPE.REFRAINED))


def days_from_game_months(months):
    delta = datetime.timedelta(seconds=months * c.TURNS_IN_GAME_MONTH * c.TURN_DELTA)
    return delta.total_seconds() / (60 * 60 * 24.0)


class POWER_BONUS_CHANGES(rels_django.DjangoEnum):
    bonus = rels.Column()

    BONUS = c.HERO_POWER_PER_DAY * 4 * 4 * 4  # like 4-th grade power card

    records = (('DOWN', 0, 'уменьшить на %d' % BONUS, -BONUS),
               ('NOT_CHANGE', 1, 'не изменять', 0),
               ('UP', 2, 'увеличить на %d' % BONUS, BONUS))
