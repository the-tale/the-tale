
import smart_imports

smart_imports.all()


V = lexicon_relations.VARIABLE


KEYS = [('ACTION_HEAL_COMPANION_DESCRIPTION', 600000, 'Описание', relations.LEXICON_GROUP.ACTION_HEAL_COMPANION,
         'Краткая декларация того, что делает герой.',
         [V.DATE, V.TIME, V.HERO, V.COMPANION], None),

        ('ACTION_HEAL_COMPANION_HEALING', 600001, 'Журнал: уход за спутником', relations.LEXICON_GROUP.ACTION_HEAL_COMPANION,
         'Герой ухаживает за спутником.',
         [V.DATE, V.TIME, V.HERO, V.COMPANION], None),

        ('ACTION_HEAL_COMPANION_START', 600002, 'Журнал: Начало', relations.LEXICON_GROUP.ACTION_HEAL_COMPANION,
         'Герой начинает ухаживать за спутником.',
         [V.DATE, V.TIME, V.HERO, V.COMPANION], None),

        ('ACTION_HEAL_COMPANION_FINISH', 600003, 'Журнал: окончание', relations.LEXICON_GROUP.ACTION_HEAL_COMPANION,
         'Герой заканчивает ухаживать за спутником и восстанавливает ему немного здоровья.',
         [V.DATE, V.TIME, V.HERO, V.COMPANION, V.HEALTH], 'companion#N +health#HP'),

        ('ACTION_HEAL_COMPANION_FINISH_WITHOUT_HEALING', 600004, 'Журнал: окончание без лечения', relations.LEXICON_GROUP.ACTION_HEAL_COMPANION,
         'Герой заканчивает ухаживать за спутником, но у того и так полное здоровье.',
         [V.DATE, V.TIME, V.HERO, V.COMPANION], None),
        ]
