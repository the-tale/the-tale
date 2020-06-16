
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
    enabled = rels.Column(unique=False)

    records = (('PLACE_RENAMING', 0, 'переименование города', True),
               ('PERSON_REMOVE', 1, 'исключить горожанина из Совета', False),
               ('PLACE_DESCRIPTION', 2, 'изменить описание города', True),
               ('PLACE_CHANGE_MODIFIER', 3, 'изменить специализацию города', True),
               ('BUILDING_CREATE', 4, 'возвести постройку', True),
               ('BUILDING_DESTROY', 5, 'разрушить постройку', True),
               ('BUILDING_RENAMING', 6, 'переименовать постройку', True),
               ('PLACE_RESOURCE_EXCHANGE', 7, 'обмен ресурсами', True),
               ('BILL_DECLINE', 8, 'отмена записи в Книге Судеб', True),
               ('PLACE_RESOURCE_CONVERSION', 9, 'изменение параметров города', True),
               ('PERSON_CHRONICLE', 10, 'запись в летописи о Мастере', True),
               ('PLACE_CHRONICLE', 11, 'запись в летописи о городе', True),
               ('PERSON_MOVE', 12, 'переезд Мастера', True),
               ('PLACE_CHANGE_RACE', 13, 'изменить расу города', True),
               ('PERSON_ADD_SOCIAL_CONNECTION', 14, 'добавить социальную связь', True),
               ('PERSON_REMOVE_SOCIAL_CONNECTION', 15, 'удалить социальную связь', True),
               ('ROAD_CREATE', 16, 'проложить дорогу', True),
               ('ROAD_DESTROY', 17, 'разрушить дорогу', True),
               ('ROAD_CHANGE', 18, 'изменить дорогу', True),
               ('EMISSARY_CHRONICLE', 19, 'запись в летописи об эмиссаре', True),
               ('PLACE_CHANGE_TAX_SIZE_BORDER', 20, 'установить поддерживаемый размер города', True),)


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
    records = (('DOWN', 0, 'уменьшить'),
               ('NOT_CHANGE', 1, 'не изменять'),
               ('UP', 2, 'увеличить'))
