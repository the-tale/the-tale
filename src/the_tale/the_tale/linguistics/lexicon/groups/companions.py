# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('COMPANIONS_RECEIVED', 580000, 'Дневник: появился спутник', LEXICON_GROUP.COMPANIONS,
        'Описание того, как появился спутник.',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION], None),

        ('COMPANIONS_KILLED', 580001, 'Дневник: спутник убит', LEXICON_GROUP.COMPANIONS,
        'Описание смерти спутника.',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION, V.ATTACKER], None),

        ('COMPANIONS_LEFT', 580002, 'Дневник: спутник ушёл', LEXICON_GROUP.COMPANIONS,
        'Описание расставания со спутником (не смерти), например из-за того, что герой меняет спутника на другого.',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION], None),

        ('COMPANIONS_BLOCK', 580003, 'Журнал: спутник защитил своего владельца от удара', LEXICON_GROUP.COMPANIONS,
        'Спутник защищает своего владельца от удара и не получает урон.',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION, V.ATTACKER], None),

        ('COMPANIONS_WOUND', 580004, 'Журнал: спутник защитил своего владельца от удара, но получил рану', LEXICON_GROUP.COMPANIONS,
        'Спутник защитил своего владельца от удара, но получил рану.',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION, V.ATTACKER, V.DAMAGE], 'companion#N -damage#HP'),

        ('COMPANIONS_BROKE_TO_SPARE_PARTS', 580005, 'Дневник: после смерти спутника удалось выгодно продать его запчасти (способность «дорогой»)', LEXICON_GROUP.COMPANIONS,
        'После смерти спутника удалось выгодно продать его запчасти',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION, V.COINS], 'hero#N +coins#HP'),

        ('COMPANIONS_SAY_WISDOM', 580006, 'Журнал: спутник говорит мудрость (способность «мудрый»)', LEXICON_GROUP.COMPANIONS,
        'Спутник изрекает мудрость, герой получает немного опыта',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION, V.EXPERIENCE], 'companion_owner#N +experience#EXP'),

        ('COMPANIONS_EAT_CORPSE', 580007, 'Журнал: спутник ест труп (способность «пожиратель»)', LEXICON_GROUP.COMPANIONS,
        'Спутник пожирает труп монстра и восстанавливает здоровье',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION, V.HEALTH, V.MOB], 'companion#N +health#HP'),

        ('COMPANIONS_REGENERATE', 580008, 'Журнал: спутник восстанавливает здоровье (способность «регенерация»)', LEXICON_GROUP.COMPANIONS,
        'Спутник восстанавливает здоровье, когда герой заканчивает «ухаживать» за ним',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION, V.HEALTH], 'companion#N +health#HP'),

        ('COMPANIONS_FLY', 580009, 'Журнал: полёт (способность «ездовой летун»)', LEXICON_GROUP.COMPANIONS,
        'Спутник переносит героя по воздуху на небольшое расстояние (способность «ездовой летун»)',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION], None),

        ('COMPANIONS_TELEPORT', 580010, 'Журнал: телепорт (способность «телепортатор»)', LEXICON_GROUP.COMPANIONS,
        'Спутник телепортирует героя в следующий по движению город или точку задания (способность «телепортатор»), учитывайте, что телепорт может перенести не в точку назначения, а в точку выполнения задания (например, к ограблению каравана).',
        [V.DATE, V.COMPANION_OWNER, V.COMPANION, V.DESTINATION], None),
        ]
