# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP


KEYS = [(u'RECEIVED', 290000, u'Дневник: появился спутник', LEXICON_GROUP.COMPANIONS,
        u'Описание того, как появился спутник.',
        [V.HERO, V.COMPANION]),

        (u'KILLED', 290001, u'Дневник: спутник убит', LEXICON_GROUP.COMPANIONS,
        u'Описание смерти спутника.',
        [V.HERO, V.COMPANION]),

        (u'LEFT', 290002, u'Дневник: спутник ушёл', LEXICON_GROUP.COMPANIONS,
        u'Описание расстования со спутником (не смерти), например из-за того, что герой меняет спутника на другого.',
        [V.HERO, V.COMPANION]),
        ]
