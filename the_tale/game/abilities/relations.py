# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c


class HELP_CHOICES(DjangoEnum):
    priority = Column(unique=False)

    records = ( ('HEAL', 0, u'лечение', 160),
                ('TELEPORT', 1, u'телепорт', 160),
                ('LIGHTING', 2, u'молния', 160),
                ('START_QUEST', 3, u'начало задания', 800),
                ('MONEY', 4, u'деньги', 40),
                ('RESURRECT', 5, u'воскрешение', 800),
                ('EXPERIENCE', 6, u'прозрение', 5),
                ('STOCK_UP_ENERGY', 7, u'запас энергии', 1),
                ('HEAL_COMPANION', 8, u'лечение спутника', 20))


class ABILITY_TYPE(DjangoEnum):
    cost = Column(unique=False)
    description = Column()
    request_attributes = Column(unique=False)

    records = ( ('HELP', 'help', u'Помочь', c.ANGEL_HELP_COST, u'Попытаться помочь герою, чем бы тот не занимался', ()),
                ('ARENA_PVP_1x1', 'arena_pvp_1x1', u'Отправить на арену', c.ANGEL_ARENA_COST, u'Отправить героя на гладиаторскую арену', ()),
                ('ARENA_PVP_1x1_LEAVE_QUEUE', 'arena_pvp_1x1_leave_queue', u'Выйти из очереди', 0, u'Выйти из очереди на арену', ()),
                ('ARENA_PVP_1x1_ACCEPT', 'arena_pvp_1x1_accept', u'Принять вызов', c.ANGEL_ARENA_COST, u'Принять вызов другого героя', ('battle',)),
                ('BUILDING_REPAIR', 'building_repair', u'Вызвать рабочего', c.BUILDING_WORKERS_ENERGY_COST, u'Вызвать рабочего для ремонта здания', ('building',)),
                ('DROP_ITEM', 'drop_item', u'Выбросить предмет', 3, u'Выбросить из рюкзака самый ненужный предмет', ()))
