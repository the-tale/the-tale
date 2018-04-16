
from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP


KEYS = [('HERO_HISTORY_BIRTH', 660000, 'Часть 1: Описание происхождения героя', LEXICON_GROUP.HERO_HISTORY,
         'Описание происхождения героя — первая часть истории героя.',
         [V.HERO], None),

        ('HERO_HISTORY_CHILDHOOD', 660001, 'Часть 2: Описание детства героя', LEXICON_GROUP.HERO_HISTORY,
         'Описание дества героя — вторая часть истории героя.',
         [V.HERO], None),

        ('HERO_HISTORY_DEATH', 660002, 'Часть 3: Описание смерти героя', LEXICON_GROUP.HERO_HISTORY,
         'Описание смерти героя — третья часть истории героя.',
         [V.HERO], None),
        ]
