
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('PVP_MISS_ABILITY', 340000, 'Журнал: Неудачное использование способности', relations.LEXICON_GROUP.PVP,
         'Хранитель пытается применить способность и терпит неудачу.',
         [V.DATE, V.TIME, V.DUELIST_1, V.DUELIST_2], None),

        ('PVP_SAY', 340001, 'Журнал: Сообщение', relations.LEXICON_GROUP.PVP,
         'Один из участвующих Хранителей что-то сказал.',
         [V.DATE, V.TIME, V.TEXT], None),

        ('PVP_USE_ABILITY_BLOOD', 340002, 'Журнал: Использование способности крови', relations.LEXICON_GROUP.PVP,
         'Хранитель применяет способность крови.',
         [V.DATE, V.TIME, V.EFFECTIVENESS, V.DUELIST_1, V.DUELIST_2], 'duelist_1#N +effectiveness#EF'),

        ('PVP_USE_ABILITY_FLAME', 340003, 'Журнал: Использование способности пламени', relations.LEXICON_GROUP.PVP,
         'Хранитель применяет способность пламени.',
         [V.DATE, V.TIME, V.DUELIST_1, V.DUELIST_2], None),

        ('PVP_USE_ABILITY_ICE', 340004, 'Журнал: Использование способности льда', relations.LEXICON_GROUP.PVP,
         'Хранитель применяет способность льда.',
         [V.DATE, V.TIME, V.DUELIST_1, V.DUELIST_2], None),

        ]
