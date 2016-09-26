# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

KEYS = [('ACTION_BATTLEPVE1X1_ARTIFACT_BROKEN', 0, 'Дневник: Артефакт сломался во время боя', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Запись в дневник о том, что герой сломал артефакт во время боя.',
         [V.MOB, V.HERO, V.ARTIFACT], None),

        ('ACTION_BATTLEPVE1X1_BATTLE_STUN', 1, 'Журнал: Стан', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой или монстр дезориентирован и пропускает ход.',
         [V.ACTOR], None),

        ('ACTION_BATTLEPVE1X1_DESCRIPTION', 2, 'Описание', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Краткая декларация того, что делает герой.',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_DIARY_HERO_KILLED', 3, 'Дневник: Герой убит', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой умирает.',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_EXP_FOR_KILL', 4, 'Дневник: Получить опыт за убийство монстра', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой получил немного опыта за убийство монстра (испытал новый приём или монстр «особенный» попался)',
         [V.MOB, V.HERO, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_BATTLEPVE1X1_JOURNAL_HERO_KILLED', 5, 'Журнал: Герой убит', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой умирает.',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_KILL_BEFORE_START', 6, 'Журнал: Убить до боя', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой заметил монстра до боя и убил его',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_LEAVE_BATTLE_IN_FEAR', 7, 'Журнал: Противник бежит в страхе', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой так напугал противника, что тот в ужасе убегает',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_MOB_KILLED', 8, 'Журнал: Монстр убит', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Монстр умирает.',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_NO_LOOT', 9, 'Журнал: Нет добычи', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой не получил добычу.',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_PEACEFULL_BATTLE', 10, 'Журнал: Мирно разойтись с разумным двуногим противником', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой договорился с разумным двуногим противником о том, чтобы драки не было',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_PERIODICAL_FIRE_DAMAGE', 11, 'Журнал: Периодический урон огнём', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой или монстр получает периодический урон огнём.',
         [V.DAMAGE, V.ACTOR], 'actor#N -damage#HP'),

        ('ACTION_BATTLEPVE1X1_PERIODICAL_POISON_DAMAGE', 12, 'Журнал: Периодический урон ядом', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой или монстр получает периодический урон ядом.',
         [V.DAMAGE, V.ACTOR], 'actor#N -damage#HP'),

        ('ACTION_BATTLEPVE1X1_PUT_LOOT', 13, 'Журнал: Герой забрал добычу', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой получил добычу с трупа противника и положил её в рюкзак.',
         [V.MOB, V.HERO, V.ARTIFACT], None),

        ('ACTION_BATTLEPVE1X1_PUT_LOOT_NO_SPACE', 14, 'Журнал: Нет места в рюкзаке', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой получил добычу, но в рюкзаке нет для неё места (добыча выкидывается).',
         [V.MOB, V.HERO, V.ARTIFACT], None),

        ('ACTION_BATTLEPVE1X1_START', 15, 'Журнал: Начало боя', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Встреча с противником.',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_COMPANION_DO_EXORCIMS', 16, 'Журнал: спутник героя изгоняет демона', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой встречает демона, после чего его спутник изгоняет демона, завершая бой',
         [V.MOB, V.HERO, V.COMPANION], None),

        ('ACTION_BATTLEPVE1X1_DIARY_HERO_AND_MOB_KILLED', 17, 'Дневник: Герой и враг убили друг друга', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой и враг убили друг друга.',
         [V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_JOURNAL_HERO_AND_MOB_KILLED', 18, 'Журнал: Герой и враг убили друг друга', LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой и враг убили друг друга.',
         [V.MOB, V.HERO], None),

       ]
