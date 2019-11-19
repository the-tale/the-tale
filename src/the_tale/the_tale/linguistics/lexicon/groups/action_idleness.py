
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_IDLENESS_DESCRIPTION', 60000, 'Описание', relations.LEXICON_GROUP.ACTION_IDLENESS,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_IDLENESS_WAITING', 60001, 'Журнал: Ожидание', relations.LEXICON_GROUP.ACTION_IDLENESS,
         'Герой занимается каким-нибудь бесполезным делом.',
         [V.DATE, V.TIME, V.HERO], None),

        ('ACTION_IDLENESS_TASK_BOARD', 60002, 'Журнал: пропуск ожидания из-за действия доски заданий гильдии', relations.LEXICON_GROUP.ACTION_IDLENESS,
         'В городе организована доска заданий гильдии, поэтому герой не бездельничает между заданиями.',
         [V.DATE, V.TIME, V.HERO, V.CLAN], None),

        ]
