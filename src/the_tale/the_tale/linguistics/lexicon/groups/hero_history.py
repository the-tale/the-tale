
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('HERO_HISTORY_BIRTH', 660000, 'Часть 1: Описание происхождения героя', relations.LEXICON_GROUP.HERO_HISTORY,
         'Описание происхождения героя — первая часть истории героя.',
         [V.HERO], None),

        ('HERO_HISTORY_CHILDHOOD', 660001, 'Часть 2: Описание детства героя', relations.LEXICON_GROUP.HERO_HISTORY,
         'Описание детства героя — вторая часть истории героя.',
         [V.HERO], None),

        ('HERO_HISTORY_DEATH', 660002, 'Часть 3: Описание смерти героя', relations.LEXICON_GROUP.HERO_HISTORY,
         'Описание смерти героя — третья часть истории героя.',
         [V.HERO], None),
        ]
