# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [(u'COMPANIONS_RECEIVED', 580000, u'Дневник: появился спутник', LEXICON_GROUP.COMPANIONS,
        u'Описание того, как появился спутник.',
        [V.COMPANION_OWNER, V.COMPANION]),

        (u'COMPANIONS_KILLED', 580001, u'Дневник: спутник убит', LEXICON_GROUP.COMPANIONS,
        u'Описание смерти спутника.',
        [V.COMPANION_OWNER, V.COMPANION, V.ATTACKER]),

        (u'COMPANIONS_LEFT', 580002, u'Дневник: спутник ушёл', LEXICON_GROUP.COMPANIONS,
        u'Описание расставания со спутником (не смерти), например из-за того, что герой меняет спутника на другого.',
        [V.COMPANION_OWNER, V.COMPANION]),

        (u'COMPANIONS_BLOCK', 580003, u'Журнал: спутник защитил своего владельца от удара', LEXICON_GROUP.COMPANIONS,
        u'Спутник защищает своего владельца от удара и не получает урон.',
        [V.COMPANION_OWNER, V.COMPANION, V.ATTACKER]),

        (u'COMPANIONS_WOUND', 580004, u'Журнал: спутник защитил своего владельца от удара, но получил рану', LEXICON_GROUP.COMPANIONS,
        u'Спутник защитил своего владельца от удара, но получил рану.',
        [V.COMPANION_OWNER, V.COMPANION, V.ATTACKER]),

        (u'COMPANIONS_BROKE_TO_SPARE_PARTS', 580005, u'Дневник: после смерти спутника удалось выгодно продать его запчасти (способность «дорогой»)', LEXICON_GROUP.COMPANIONS,
        u'После смерти спутника удалось выгодно продать его запчасти',
        [V.COMPANION_OWNER, V.COMPANION, V.COINS]),

        (u'COMPANIONS_SAY_WISDOM', 580006, u'Журнал: спутник говорит мудрость (способность «мудрый»)', LEXICON_GROUP.COMPANIONS,
        u'Спутник говорит мудрость, героя получает немного опыта',
        [V.COMPANION_OWNER, V.COMPANION, V.COINS, V.EXPERIENCE]),

        (u'COMPANIONS_EAT_CORPSE', 580007, u'Журнал: спутник есть труп (способность «пожиратель»)', LEXICON_GROUP.COMPANIONS,
        u'Спутник пожирает труп монстра и восстанавливает здоровье',
        [V.COMPANION_OWNER, V.COMPANION, V.HEALTH]),

        (u'COMPANIONS_REGENERATE', 580008, u'Журнал: спутник восстанавливает здоровье (способность «регенерация»)', LEXICON_GROUP.COMPANIONS,
        u'Спутник восстанавливает здоровье, когда героя заканчивает «ухаживать» за ним',
        [V.COMPANION_OWNER, V.COMPANION, V.HEALTH]),

        (u'COMPANIONS_FLY', 580009, u'Журнал: полёт (способность «ездовой летун»)', LEXICON_GROUP.COMPANIONS,
        u'Спутник переносит героя по воздуху на небольшое расстояние (способность «ездовой летун»)',
        [V.COMPANION_OWNER, V.COMPANION]),

        (u'COMPANIONS_TELEPORT', 580010, u'Журнал: телепорт (способность «телепортатор»)', LEXICON_GROUP.COMPANIONS,
        u'Спутник телепортирует героя в следующий по движению город или точку задания (способность «телепортатор»)',
        [V.COMPANION_OWNER, V.COMPANION]),
        ]
