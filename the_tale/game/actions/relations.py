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
