# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c


class ACTION_EVENT(DjangoEnum):

    records = ( ('DISHONORABLE', 0, u'бесчестный герой'),
                ('NOBLE', 1, u'благородный герой'),
                ('AGGRESSIVE', 2, u'аггрессивный герой'),
                ('PEACEABLE', 3, u'миролюбивый герой'),)


class ACTION_EVENT_REWARD(DjangoEnum):
    priority = Column(unique=False)

    records = ( ('NOTHING', 0, u'без награды', c.HABIT_EVENT_NOTHING_PRIORITY),
                ('MONEY', 1, u'деньги', c.HABIT_EVENT_MONEY_PRIORITY),
                ('ARTIFACT', 2, u'артефакт', c.HABIT_EVENT_ARTIFACT_PRIORITY),
                ('EXPERIENCE', 3, u'опыт', c.HABIT_EVENT_EXPERIENCE_PRIORITY) )



class ACTION_TYPE(DjangoEnum):
    meta = Column(unique=False)
    technical = Column(unique=False)

    records = ( ('IDLENESS', 0, u'безделие', False, False),
                ('QUEST',    1, u'задание', False, False),
                ('MOVE_TO', 2, u'путешествие между городами', False, False),
                ('BATTLE_PVE_1X1', 3, u'сражение 1x1 с монстром', False, False),
                ('RESURRECT', 4, u'воскрешение', False, False),
                ('IN_PLACE', 5, u'действия в городе', False, False),
                ('REST', 6, u'отдых', False, False),
                ('EQUIPPING', 7, u'экипировка', False, False),
                ('TRADING', 8, u'торговля', False, False),
                ('MOVE_NEAR_PLACE', 9, u'путешествие около города', False, False),
                ('REGENERATE_ENERGY', 10, u'восстановление энергии', False, False),
                ('DO_NOTHING', 11, u'действие без эффекта на игру', False, False),
                ('META_PROXY', 12, u'прокси-действия для взаимодействия героев', False, True),
                ('ARENA_PVP_1X1', 13, u'PvP 1x1', True, False),

                ('TEST', 14, u'проверочное действие', False, True),

                ('HEAL_COMPANION', 15, u'уход за спутником', False, False),
                )
