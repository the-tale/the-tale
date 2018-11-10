
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_MOVENEARPLACE_DESCRIPTION', 100000, 'Описание', relations.LEXICON_GROUP.ACTION_MOVENEARPLACE,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ('ACTION_MOVENEARPLACE_WALK', 100001, 'Журнал: Путешествие', relations.LEXICON_GROUP.ACTION_MOVENEARPLACE,
         'Герой путешествует.',
         [V.DATE, V.TIME, V.HERO, V.PLACE], None),

        ]
