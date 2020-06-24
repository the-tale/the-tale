
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_BATTLEPVE1X1_ARTIFACT_BROKEN', 0, 'Дневник: Артефакт сломался во время боя', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Запись в дневник о том, что герой сломал артефакт во время боя.',
         [V.DATE, V.TIME, V.MOB, V.HERO, V.ARTIFACT], None),

        ('ACTION_BATTLEPVE1X1_BATTLE_STUN', 1, 'Журнал: Стан', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой или монстр дезориентирован и пропускает ход.',
         [V.DATE, V.TIME, V.ACTOR], None),

        ('ACTION_BATTLEPVE1X1_DESCRIPTION', 2, 'Описание', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_DIARY_HERO_KILLED', 3, 'Дневник: Герой убит', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой умирает.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_EXP_FOR_KILL', 4, 'Дневник: Получить опыт за убийство монстра', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой получил немного опыта за убийство монстра (испытал новый приём или монстр «особенный» попался).',
         [V.DATE, V.TIME, V.MOB, V.HERO, V.EXPERIENCE], 'hero#N +experience#EXP'),

        ('ACTION_BATTLEPVE1X1_JOURNAL_HERO_KILLED', 5, 'Журнал: Герой убит', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой умирает.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_KILL_BEFORE_START', 6, 'Журнал: Убить до боя', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой заметил монстра до боя и убил его.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_LEAVE_BATTLE_IN_FEAR', 7, 'Журнал: Противник бежит в страхе', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой так напугал противника, что тот в ужасе убегает.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_MOB_KILLED', 8, 'Журнал: Монстр убит', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Монстр умирает.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_NO_LOOT', 9, 'Журнал: Нет добычи', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой не получил добычу.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_PEACEFULL_BATTLE', 10, 'Журнал: Мирно разойтись с разумным двуногим противником', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой договорился с разумным двуногим противником о том, чтобы драки не было.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_PERIODICAL_FIRE_DAMAGE', 11, 'Журнал: Периодический урон огнём', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой или монстр получает периодический урон огнём.',
         [V.DATE, V.TIME, V.DAMAGE, V.ACTOR], 'actor#N -damage#HP'),

        ('ACTION_BATTLEPVE1X1_PERIODICAL_POISON_DAMAGE', 12, 'Журнал: Периодический урон ядом', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой или монстр получает периодический урон ядом.',
         [V.DATE, V.TIME, V.DAMAGE, V.ACTOR], 'actor#N -damage#HP'),

        ('ACTION_BATTLEPVE1X1_PUT_LOOT', 13, 'Журнал: Герой забрал добычу', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой получил добычу с трупа противника и положил её в рюкзак.',
         [V.DATE, V.TIME, V.MOB, V.HERO, V.ARTIFACT], None),

        ('ACTION_BATTLEPVE1X1_PUT_LOOT_NO_SPACE', 14, 'Журнал: Нет места в рюкзаке', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой получил добычу, но в рюкзаке нет для неё места (добыча выкидывается).',
         [V.DATE, V.TIME, V.MOB, V.HERO, V.ARTIFACT], None),

        ('ACTION_BATTLEPVE1X1_START', 15, 'Журнал: Начало боя', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Встреча с противником.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_COMPANION_DO_EXORCIMS', 16, 'Журнал: спутник героя изгоняет демона', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой встречает демона, после чего его спутник изгоняет демона, завершая бой.',
         [V.DATE, V.TIME, V.MOB, V.HERO, V.COMPANION], None),

        ('ACTION_BATTLEPVE1X1_DIARY_HERO_AND_MOB_KILLED', 17, 'Дневник: Герой и враг убили друг друга', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой и враг убили друг друга.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_JOURNAL_HERO_AND_MOB_KILLED', 18, 'Журнал: Герой и враг убили друг друга', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой и враг убили друг друга.',
         [V.DATE, V.TIME, V.MOB, V.HERO], None),

        ('ACTION_BATTLEPVE1X1_REPLACE_LOOT_WHEN_NO_SPACE', 19, 'Журнал: герой заменил предмет в рюкзаке на добычу', relations.LEXICON_GROUP.ACTION_BATTLEPVE1X1,
         'Герой получил добычу, но в рюкзаке нет для неё места. Поэтому герой выкидывает самый ненужный (дешёвый) предмет из рюкзака и кладёт туда добычу.',
         [V.DATE, V.TIME, V.MOB, V.HERO, V.ARTIFACT, V.DROPPED_ARTIFACT], None),

        ]
