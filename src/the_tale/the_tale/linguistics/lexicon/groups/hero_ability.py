
from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('HERO_ABILITY_FIREBALL', 280000, 'Журнал: Пиромания', LEXICON_GROUP.HERO_ABILITY,
        'Нанесение урона способностью «Пиромания».',
        [V.DATE, V.TIME, V.ATTACKER, V.DAMAGE, V.DEFENDER], 'defender#N -damage#HP'),

        ('HERO_ABILITY_FIREBALL_MISS', 280001, 'Журнал: Пиромания (промах)', LEXICON_GROUP.HERO_ABILITY,
        'Атакующий промахнулся при использовании способности «Пиромания»',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ('HERO_ABILITY_FREEZING', 280002, 'Журнал: Контроль', LEXICON_GROUP.HERO_ABILITY,
        'Применение способности «Контроль».',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ('HERO_ABILITY_HIT', 280003, 'Журнал: Удар', LEXICON_GROUP.HERO_ABILITY,
        'Нанесение урона способностью «Удар».',
        [V.DATE, V.TIME, V.ATTACKER, V.DAMAGE, V.DEFENDER], 'defender#N -damage#HP'),

        ('HERO_ABILITY_HIT_MISS', 280004, 'Журнал: Удар (Промах)', LEXICON_GROUP.HERO_ABILITY,
        'Атакующий промахнулся при использовании способности «Удар»',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ('HERO_ABILITY_LAST_CHANCE', 280005, 'Журнал: Последний шанс', LEXICON_GROUP.HERO_ABILITY,
        'Фразы при срабатывании способности «последний шанс»',
        [V.DATE, V.TIME, V.ACTOR], None),

        ('HERO_ABILITY_MAGICMUSHROOM', 280006, 'Журнал: Ярость', LEXICON_GROUP.HERO_ABILITY,
        'Использование способности «Ярость»',
        [V.DATE, V.TIME, V.ACTOR], None),

        ('HERO_ABILITY_POISON_CLOUD', 280007, 'Журнал: Ядовитость', LEXICON_GROUP.HERO_ABILITY,
        'Применение способности «Ядовитость».',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ('HERO_ABILITY_REGENERATION', 280008, 'Журнал: Регенерация', LEXICON_GROUP.HERO_ABILITY,
        'Герой использует способность и восстанавливает здоровье.',
        [V.DATE, V.TIME, V.HEALTH, V.ACTOR], 'actor#N +health#HP'),

        ('HERO_ABILITY_RUNUPPUSH', 280009, 'Журнал: Ошеломление', LEXICON_GROUP.HERO_ABILITY,
        'Использование способности «Ошеломление»',
        [V.DATE, V.TIME, V.ATTACKER, V.DAMAGE, V.DEFENDER], 'defender#N -damage#HP'),

        ('HERO_ABILITY_RUNUPPUSH_MISS', 280010, 'Журнал: Ошеломление (промах)', LEXICON_GROUP.HERO_ABILITY,
        'Промах при использовании способности «Ошеломление».',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ('HERO_ABILITY_SIDESTEP', 280011, 'Журнал: Дезориентация', LEXICON_GROUP.HERO_ABILITY,
        'Использование способности «Дезориентация»',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ('HERO_ABILITY_SPEEDUP', 280012, 'Журнал: Ускорение', LEXICON_GROUP.HERO_ABILITY,
        'Применение способности «Ускорение».',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ('HERO_ABILITY_STRONG_HIT', 280013, 'Журнал: Сильный удар', LEXICON_GROUP.HERO_ABILITY,
        'Нанесение урона способностью «Сильный удар».',
        [V.DATE, V.TIME, V.ATTACKER, V.DAMAGE, V.DEFENDER], 'defender#N -damage#HP'),

        ('HERO_ABILITY_STRONG_HIT_MISS', 280014, 'Журнал: Сильный удар (промах)', LEXICON_GROUP.HERO_ABILITY,
        'Атакующий промахнулся при использовании способности «Сильный удар»',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ('HERO_ABILITY_VAMPIRE_STRIKE', 280015, 'Журнал: Вампиризм', LEXICON_GROUP.HERO_ABILITY,
        'Нанесение урона способностью «Вампиризм».',
        [V.DATE, V.TIME, V.ATTACKER, V.HEALTH, V.DAMAGE, V.DEFENDER], 'attacker#N +health#HP defender#N -damage#HP'),

        ('HERO_ABILITY_VAMPIRE_STRIKE_MISS', 280016, 'Журнал: Вампиризм (промах)', LEXICON_GROUP.HERO_ABILITY,
        'Атакующий промахнулся при использовании способности «Вампиризм»',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ('HERO_ABILITY_COMPANION_HEALING', 280017, 'Журнал: Герой лечит спутника', LEXICON_GROUP.HERO_ABILITY,
        'Герой восстановил спутнику немного здоровья',
        [V.DATE, V.TIME, V.ACTOR, V.COMPANION, V.HEALTH], 'companion#N +health#HP'),

        ('HERO_ABILITY_INSANE_STRIKE', 280018, 'Журнал: Безрассудная атака', LEXICON_GROUP.HERO_ABILITY,
        'Герой проводит беззрассудную атаку, наносит противнику большой урон, но и сам получает ранения',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER, V.DAMAGE, V.ATTACKER_DAMAGE], 'attacker#N -attacker_damage#HP defender#N -damage#HP'),

        ('HERO_ABILITY_INSANE_STRIKE_MISS', 280019, 'Журнал: Безрассудная атака (промах)', LEXICON_GROUP.HERO_ABILITY,
        'Атакующий промахнулся при использовании способности «Безрассудная атака»',
        [V.DATE, V.TIME, V.ATTACKER, V.DEFENDER], None),

        ]
