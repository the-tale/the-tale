# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

# hero -> companion_owner
# mob -> attacker


KEYS = [(u'COMPANIONS_RECEIVED', 580000, u'Дневник: появился спутник', LEXICON_GROUP.COMPANIONS,
        u'Описание того, как появился спутник.',
        [V.COMPANION_OWNER, V.COMPANION]),

        (u'COMPANIONS_KILLED', 580001, u'Дневник: спутник убит', LEXICON_GROUP.COMPANIONS,
        u'Описание смерти спутника.',
        [V.COMPANION_OWNER, V.COMPANION, V.ATTACKER]),

        (u'COMPANIONS_LEFT', 580002, u'Дневник: спутник ушёл', LEXICON_GROUP.COMPANIONS,
        u'Описание расстования со спутником (не смерти), например из-за того, что герой меняет спутника на другого.',
        [V.COMPANION_OWNER, V.COMPANION]),

        (u'COMPANIONS_BLOCK', 580003, u'Журнал: спутник защитил своего владельца от удара', LEXICON_GROUP.COMPANIONS,
        u'Спутник защищает своего владельца от удара и не получает урон.',
        [V.COMPANION_OWNER, V.COMPANION, V.ATTACKER]),

        (u'COMPANIONS_WOUND', 580004, u'Журнал: спутник защитил своего владельца от удара, но получил рану', LEXICON_GROUP.COMPANIONS,
        u'Спутник защитил своего владельца от удара, но получил рану.',
        [V.COMPANION_OWNER, V.COMPANION, V.ATTACKER]),
        ]
