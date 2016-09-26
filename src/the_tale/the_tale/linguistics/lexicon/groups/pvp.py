# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('PVP_MISS_ABILITY', 340000, 'Журнал: Неудачное использование способности', LEXICON_GROUP.PVP,
         'Хранитель пытается применить способность и терпит неудачу.',
         [V.DUELIST_1, V.DUELIST_2], None),

        ('PVP_SAY', 340001, 'Журнал: Сообщение', LEXICON_GROUP.PVP,
         'Один из участвующих Хранителей что-то сказал.',
         [V.TEXT], None),

        ('PVP_USE_ABILITY_BLOOD', 340002, 'Журнал: Использование способности крови', LEXICON_GROUP.PVP,
         'Хранитель применяет способность крови.',
         [V.EFFECTIVENESS, V.DUELIST_1, V.DUELIST_2], 'duelist_1#N +effectiveness#EF'),

        ('PVP_USE_ABILITY_FLAME', 340003, 'Журнал: Использование способности пламени', LEXICON_GROUP.PVP,
         'Хранитель применяет способность пламени.',
         [V.DUELIST_1, V.DUELIST_2], None),

        ('PVP_USE_ABILITY_ICE', 340004, 'Журнал: Использование способности льда', LEXICON_GROUP.PVP,
         'Хранитель применяет способность льда.',
         [V.DUELIST_1, V.DUELIST_2], None),

       ]
