# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_HEAL_COMPANION_DESCRIPTION', 600000, 'Описание', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        'Краткая декларация того, что делает герой.',
        [V.DATE, V.HERO, V.COMPANION], None),

        ('ACTION_HEAL_COMPANION_HEALING', 600001, 'Журнал: уход за спутником', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        'Герой ухаживает за спутником.',
        [V.DATE, V.HERO, V.COMPANION], None),

        ('ACTION_HEAL_COMPANION_START', 600002, 'Журнал: Начало', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        'Герой начинает ухаживать за спутником.',
        [V.DATE, V.HERO, V.COMPANION], None),

        ('ACTION_HEAL_COMPANION_FINISH', 600003, 'Журнал: окончание', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        'Герой заканчивает ухаживать за спутником и восстанавливает ему немного здоровья.',
        [V.DATE, V.HERO, V.COMPANION, V.HEALTH], 'companion#N +health#HP'),

        ('ACTION_HEAL_COMPANION_FINISH_WITHOUT_HEALING', 600004, 'Журнал: окончание без лечения', LEXICON_GROUP.ACTION_HEAL_COMPANION,
        'Герой заканчивает ухаживать за спутником, но у того и так полное здоровье.',
        [V.DATE, V.HERO, V.COMPANION], None),
        ]
