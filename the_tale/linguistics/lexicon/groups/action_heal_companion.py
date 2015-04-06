# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'ACTION_HEAL_COMPANION_DESCRIPTION', 600000, u'Описание', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        u'Краткая декларация того, что делает герой.',
        [V.HERO, V.COMPANION]),

        (u'ACTION_HEAL_COMPANION_HEALING', 600001, u'Журнал: уход за спутником', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        u'Герой ухаживает за спутником.',
        [V.HERO, V.COMPANION]),

        (u'ACTION_HEAL_COMPANION_START', 600002, u'Журнал: Начало', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        u'Герой начинает ухаживать за спутником.',
        [V.HERO, V.COMPANION]),

        (u'ACTION_HEAL_COMPANION_FINISH', 600003, u'Журнал: окончание', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        u'Герой заканчивает ухаживать за спутником и восстанавливает ему немного здоровья.',
        [V.HERO, V.COMPANION, V.HEALTH]),

        (u'ACTION_HEAL_COMPANION_FINISH_WITHOUT_HEALING', 600004, u'Журнал: окончание без лечения', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        u'Герой заканчивает ухаживать за спутником, но у того и так полное здоровье.',
        [V.HERO, V.COMPANION]),
        ]
