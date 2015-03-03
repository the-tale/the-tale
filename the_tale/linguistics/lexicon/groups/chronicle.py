# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'CHRONICLE_BUILDING_DESTROYED_BY_AMORTIZATION', 260009, u'Строение: разрушилось от старости', LEXICON_GROUP.CHRONICLE,
        u'Строение разрушилось т.к. его никто не ремонтировал.',
        [V.PERSON, V.PLACE]),

        (u'CHRONICLE_PERSON_ARRIVED_TO_PLACE', 260013, u'Член Совета: в совет вошёл новый житель', LEXICON_GROUP.CHRONICLE,
        u'Новый житель вошёл в совет города.',
        [V.PERSON, V.PLACE]),

        (u'CHRONICLE_PERSON_LEFT_PLACE', 260014, u'Член Совета: автоматически покинул Совет', LEXICON_GROUP.CHRONICLE,
        u'Член Совета потерял влияние и оставил свою должность.',
        [V.PERSON, V.PLACE]),

        (u'CHRONICLE_PLACE_CHANGE_RACE', 260030, u'Раса города: изменение', LEXICON_GROUP.CHRONICLE,
        u'Изменилась доминирующая раса города.',
        [V.OLD_RACE, V.NEW_RACE, V.PLACE]),

        (u'CHRONICLE_PLACE_LOSED_MODIFIER', 260031, u'Специализация города: автоматически сброшена', LEXICON_GROUP.CHRONICLE,
        u'Специализация сброшена из-за того, что её развитие стало меньше необходимого барьера',
        [V.PLACE, V.OLD_MODIFIER]),
        ]
