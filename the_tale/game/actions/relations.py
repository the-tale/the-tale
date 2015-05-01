# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c


class ACTION_EVENT(DjangoEnum):

    records = ( ('DISHONORABLE', 0, u'бесчестный герой'),
                ('NOBLE', 1, u'благородный герой'),
                ('AGGRESSIVE', 2, u'аггрессивный герой'),
                ('PEACEABLE', 3, u'миролюбивый герой'),)


class ACTION_HABIT_MODE(DjangoEnum):

    records = ( ('AGGRESSIVE', 0, u'агрессивное действие'),
                ('PEACEFUL', 1, u'мирное действие'),
                ('COMPANION', 2, u'зависит от спутника'))


class ACTION_EVENT_REWARD(DjangoEnum):
    priority = Column(unique=False)

    records = ( ('NOTHING', 0, u'без награды', c.HABIT_EVENT_NOTHING_PRIORITY),
                ('MONEY', 1, u'деньги', c.HABIT_EVENT_MONEY_PRIORITY),
                ('ARTIFACT', 2, u'артефакт', c.HABIT_EVENT_ARTIFACT_PRIORITY),
                ('EXPERIENCE', 3, u'опыт', c.HABIT_EVENT_EXPERIENCE_PRIORITY) )



class ACTION_TYPE(DjangoEnum):
    meta = Column(unique=False)
    technical = Column(unique=False)

    records = ( ('IDLENESS', 0, u'герой бездельничает', False, False),
                ('QUEST',    1, u'герой выполненяет задание', False, False),
                ('MOVE_TO', 2, u'герой путешествует между городами', False, False),
                ('BATTLE_PVE_1X1', 3, u'герой сражается 1x1 с монстром', False, False),
                ('RESURRECT', 4, u'герой воскресает', False, False),
                ('IN_PLACE', 5, u'герой в городе', False, False),
                ('REST', 6, u'герой лечится', False, False),
                ('EQUIPPING', 7, u'герой экипируется', False, False),
                ('TRADING', 8, u'герой торгует', False, False),
                ('MOVE_NEAR_PLACE', 9, u'герой путешествует около города', False, False),
                ('REGENERATE_ENERGY', 10, u'герой восстановливает энергию Хранителю', False, False),
                ('DO_NOTHING', 11, u'техническое действие для особых действий героя в заданиях', False, False),
                ('META_PROXY', 12, u'техническое прокси-действие для взаимодействия героев', False, True),
                ('ARENA_PVP_1X1', 13, u'герой сражается 1x1 с другим героем', True, False),

                ('TEST', 14, u'техническое действие для тестов', False, True),

                ('HEAL_COMPANION', 15, u'герой ухаживает за спутником', False, False),
              )
