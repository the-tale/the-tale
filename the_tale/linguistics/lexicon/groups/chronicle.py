# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'CHRONICLE_PERSON_ARRIVED_TO_PLACE', 260013, u'Член Совета: в совет вошёл новый житель', LEXICON_GROUP.CHRONICLE,
        u'Новый житель вошёл в совет города.',
        [V.PERSON, V.PLACE], None),

        (u'CHRONICLE_PLACE_CHANGE_RACE', 260030, u'Раса города: изменение', LEXICON_GROUP.CHRONICLE,
        u'Изменилась доминирующая раса города.',
        [V.OLD_RACE, V.NEW_RACE, V.PLACE], None)
        ]
