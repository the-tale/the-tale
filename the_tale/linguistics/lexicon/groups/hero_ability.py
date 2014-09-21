# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'HERO_ABILITY_FIREBALL', 280000, u'Шар огня', LEXICON_GROUP.HERO_ABILITY,
        u'Нанесение урона способностью «Шар огня».',
        [V.ATTACKER, V.DAMAGE, V.DEFENDER]),

        (u'HERO_ABILITY_FIREBALL_MISS', 280001, u'Шар огня (промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Атакующий промахнулся при использовании способности «Шар огня»',
        [V.ATTACKER, V.DEFENDER]),

        (u'HERO_ABILITY_FREEZING', 280002, u'Заморозка', LEXICON_GROUP.HERO_ABILITY,
        u'Применение способности «Заморозка».',
        [V.ATTACKER, V.DEFENDER]),

        (u'HERO_ABILITY_HIT', 280003, u'Удар', LEXICON_GROUP.HERO_ABILITY,
        u'Нанесение урона способностью «Удар».',
        [V.ATTACKER, V.DAMAGE, V.DEFENDER]),

        (u'HERO_ABILITY_HIT_MISS', 280004, u'Удар (Промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Атакующий промахнулся при использовании способности «Удар»',
        [V.ATTACKER, V.DEFENDER]),

        (u'HERO_ABILITY_LAST_CHANCE', 280005, u'Последний шанс', LEXICON_GROUP.HERO_ABILITY,
        u'Фразы при срабатывании способности «последний шанс»',
        [V.ACTOR]),

        (u'HERO_ABILITY_MAGICMUSHROOM', 280006, u'Волшебный гриб', LEXICON_GROUP.HERO_ABILITY,
        u'Использование способности «Волшебный гриб»',
        [V.ACTOR]),

        (u'HERO_ABILITY_POISON_CLOUD', 280007, u'Ядовитое облако', LEXICON_GROUP.HERO_ABILITY,
        u'Применение способности «Ядовитое облако».',
        [V.ATTACKER, V.DEFENDER]),

        (u'HERO_ABILITY_REGENERATION', 280008, u'Регенерация', LEXICON_GROUP.HERO_ABILITY,
        u'Герой использует способность и восстанавливает здоровье.',
        [V.HEALTH, V.ACTOR]),

        (u'HERO_ABILITY_RUNUPPUSH', 280009, u'Разбег-толчок', LEXICON_GROUP.HERO_ABILITY,
        u'Использование способности «Разбег-толчок»',
        [V.ATTACKER, V.DAMAGE, V.DEFENDER]),

        (u'HERO_ABILITY_RUNUPPUSH_MISS', 280010, u'Разбег-толчок (промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Промах при использовании способности «Разбег—толчок»',
        [V.ATTACKER, V.DAMAGE, V.DEFENDER]),

        (u'HERO_ABILITY_SIDESTEP', 280011, u'Шаг в сторону', LEXICON_GROUP.HERO_ABILITY,
        u'Использование способности «Шаг в сторону»',
        [V.ATTACKER, V.DEFENDER]),

        (u'HERO_ABILITY_SPEEDUP', 280012, u'Ускорение', LEXICON_GROUP.HERO_ABILITY,
        u'Применение способности «Ускорение».',
        [V.ATTACKER, V.DEFENDER]),

        (u'HERO_ABILITY_STRONG_HIT', 280013, u'Сильный удар', LEXICON_GROUP.HERO_ABILITY,
        u'Нанесение урона способностью «Сильный удар».',
        [V.ATTACKER, V.DAMAGE, V.DEFENDER]),

        (u'HERO_ABILITY_STRONG_HIT_MISS', 280014, u'Сильный удар (промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Атакующий промахнулся при использовании способности «Сильный удар»',
        [V.ATTACKER, V.DEFENDER]),

        (u'HERO_ABILITY_VAMPIRE_STRIKE', 280015, u'Удар вампира', LEXICON_GROUP.HERO_ABILITY,
        u'Нанесение урона способностью «Удар вампира».',
        [V.ATTACKER, V.HEALTH, V.DAMAGE, V.DEFENDER]),

        (u'HERO_ABILITY_VAMPIRE_STRIKE_MISS', 280016, u'Удар вампира (промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Атакующий промахнулся при использовании способности «Удар вампира»',
        [V.ATTACKER, V.DEFENDER]),

        ]
        