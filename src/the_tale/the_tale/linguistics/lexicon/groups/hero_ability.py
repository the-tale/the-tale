# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'HERO_ABILITY_FIREBALL', 280000, u'Журнал: Пиромания', LEXICON_GROUP.HERO_ABILITY,
        u'Нанесение урона способностью «Пиромания».',
        [V.ATTACKER, V.DAMAGE, V.DEFENDER], u'defender#N -damage#HP'),

        (u'HERO_ABILITY_FIREBALL_MISS', 280001, u'Журнал: Пиромания (промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Атакующий промахнулся при использовании способности «Пиромания»',
        [V.ATTACKER, V.DEFENDER], None),

        (u'HERO_ABILITY_FREEZING', 280002, u'Журнал: Контроль', LEXICON_GROUP.HERO_ABILITY,
        u'Применение способности «Контроль».',
        [V.ATTACKER, V.DEFENDER], None),

        (u'HERO_ABILITY_HIT', 280003, u'Журнал: Удар', LEXICON_GROUP.HERO_ABILITY,
        u'Нанесение урона способностью «Удар».',
        [V.ATTACKER, V.DAMAGE, V.DEFENDER], u'defender#N -damage#HP'),

        (u'HERO_ABILITY_HIT_MISS', 280004, u'Журнал: Удар (Промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Атакующий промахнулся при использовании способности «Удар»',
        [V.ATTACKER, V.DEFENDER], None),

        (u'HERO_ABILITY_LAST_CHANCE', 280005, u'Журнал: Последний шанс', LEXICON_GROUP.HERO_ABILITY,
        u'Фразы при срабатывании способности «последний шанс»',
        [V.ACTOR], None),

        (u'HERO_ABILITY_MAGICMUSHROOM', 280006, u'Журнал: Ярость', LEXICON_GROUP.HERO_ABILITY,
        u'Использование способности «Ярость»',
        [V.ACTOR], None),

        (u'HERO_ABILITY_POISON_CLOUD', 280007, u'Журнал: Ядовитость', LEXICON_GROUP.HERO_ABILITY,
        u'Применение способности «Ядовитость».',
        [V.ATTACKER, V.DEFENDER], None),

        (u'HERO_ABILITY_REGENERATION', 280008, u'Журнал: Регенерация', LEXICON_GROUP.HERO_ABILITY,
        u'Герой использует способность и восстанавливает здоровье.',
        [V.HEALTH, V.ACTOR], u'actor#N +health#HP'),

        (u'HERO_ABILITY_RUNUPPUSH', 280009, u'Журнал: Ошеломление', LEXICON_GROUP.HERO_ABILITY,
        u'Использование способности «Ошеломление»',
        [V.ATTACKER, V.DAMAGE, V.DEFENDER], u'defender#N -damage#HP'),

        (u'HERO_ABILITY_RUNUPPUSH_MISS', 280010, u'Журнал: Ошеломление (промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Промах при использовании способности «Ошеломление».',
        [V.ATTACKER, V.DEFENDER], None),

        (u'HERO_ABILITY_SIDESTEP', 280011, u'Журнал: Дезориентация', LEXICON_GROUP.HERO_ABILITY,
        u'Использование способности «Дезориентация»',
        [V.ATTACKER, V.DEFENDER], None),

        (u'HERO_ABILITY_SPEEDUP', 280012, u'Журнал: Ускорение', LEXICON_GROUP.HERO_ABILITY,
        u'Применение способности «Ускорение».',
        [V.ATTACKER, V.DEFENDER], None),

        (u'HERO_ABILITY_STRONG_HIT', 280013, u'Журнал: Сильный удар', LEXICON_GROUP.HERO_ABILITY,
        u'Нанесение урона способностью «Сильный удар».',
        [V.ATTACKER, V.DAMAGE, V.DEFENDER], u'defender#N -damage#HP'),

        (u'HERO_ABILITY_STRONG_HIT_MISS', 280014, u'Журнал: Сильный удар (промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Атакующий промахнулся при использовании способности «Сильный удар»',
        [V.ATTACKER, V.DEFENDER], None),

        (u'HERO_ABILITY_VAMPIRE_STRIKE', 280015, u'Журнал: Вампиризм', LEXICON_GROUP.HERO_ABILITY,
        u'Нанесение урона способностью «Вампиризм».',
        [V.ATTACKER, V.HEALTH, V.DAMAGE, V.DEFENDER], u'attacker#N +health#HP defender#N -damage#HP'),

        (u'HERO_ABILITY_VAMPIRE_STRIKE_MISS', 280016, u'Журнал: Вампиризм (промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Атакующий промахнулся при использовании способности «Вампиризм»',
        [V.ATTACKER, V.DEFENDER], None),

        (u'HERO_ABILITY_COMPANION_HEALING', 280017, u'Журнал: Герой лечит спутника', LEXICON_GROUP.HERO_ABILITY,
        u'Герой восстановил спутнику немного здоровья',
        [V.ACTOR, V.COMPANION, V.HEALTH], u'companion#N +health#HP'),

        (u'HERO_ABILITY_INSANE_STRIKE', 280018, u'Журнал: Безрассудная атака', LEXICON_GROUP.HERO_ABILITY,
        u'Герой проводит беззрассудную атаку, наносит противнику большой урон, но и сам получает ранения',
        [V.ATTACKER, V.DEFENDER, V.DAMAGE, V.ATTACKER_DAMAGE], u'attacker#N -attacker_damage#HP defender#N -damage#HP'),

        (u'HERO_ABILITY_INSANE_STRIKE_MISS', 280019, u'Журнал: Безрассудная атака (промах)', LEXICON_GROUP.HERO_ABILITY,
        u'Атакующий промахнулся при использовании способности «Безрассудная атака»',
        [V.ATTACKER, V.DEFENDER], None),

        ]
