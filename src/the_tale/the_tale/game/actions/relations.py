
import smart_imports

smart_imports.all()


UNINITIALIZED_STATE = 'uninitialized'


class ACTION_EVENT(rels_django.DjangoEnum):

    records = (('DISHONORABLE', 0, 'бесчестный герой'),
               ('NOBLE', 1, 'благородный герой'),
               ('AGGRESSIVE', 2, 'аггрессивный герой'),
               ('PEACEABLE', 3, 'миролюбивый герой'),)


class ACTION_HABIT_MODE(rels_django.DjangoEnum):

    records = (('AGGRESSIVE', 0, 'агрессивное действие'),
               ('PEACEFUL', 1, 'мирное действие'),
               ('COMPANION', 2, 'зависит от спутника'))


class ACTION_EVENT_REWARD(rels_django.DjangoEnum):
    priority = rels.Column(unique=False)

    records = (('NOTHING', 0, 'без награды', c.HABIT_EVENT_NOTHING_PRIORITY),
               ('MONEY', 1, 'деньги', c.HABIT_EVENT_MONEY_PRIORITY),
               ('ARTIFACT', 2, 'артефакт', c.HABIT_EVENT_ARTIFACT_PRIORITY),
               ('EXPERIENCE', 3, 'опыт', c.HABIT_EVENT_EXPERIENCE_PRIORITY))


class ACTION_TYPE(rels_django.DjangoEnum):
    meta = rels.Column(unique=False)
    technical = rels.Column(unique=False)

    records = (('IDLENESS', 0, 'герой бездельничает', False, False),
               ('QUEST', 1, 'герой выполненяет задание', False, False),

               ('BATTLE_PVE_1X1', 3, 'герой сражается 1x1 с монстром', False, False),
               ('RESURRECT', 4, 'герой воскресает', False, False),
               ('IN_PLACE', 5, 'герой в городе', False, False),
               ('REST', 6, 'герой лечится', False, False),
               ('EQUIPPING', 7, 'герой экипируется', False, False),
               ('TRADING', 8, 'герой торгует', False, False),

               ('RELIGION_CEREMONY', 10, 'герой проводит ритуал в честь Хранителя', False, False),
               ('DO_NOTHING', 11, 'техническое действие для особых действий героя в заданиях', False, False),
               ('META_PROXY', 12, 'техническое прокси-действие для взаимодействия героев', False, True),
               ('ARENA_PVP_1X1', 13, 'герой сражается 1x1 с другим героем', True, False),

               ('TEST', 14, 'техническое действие для тестов', False, True),

               ('HEAL_COMPANION', 15, 'герой ухаживает за спутником', False, False),
               ('FIRST_STEPS', 16, 'действия героя сразу после иницииации', False, False),

               ('MOVE_SIMPLE', 17, 'герой движется из одной точки в другую', False, False),
               ('NAVIGATE', 18, 'герой выбирает дальнейший путь', False, False))
