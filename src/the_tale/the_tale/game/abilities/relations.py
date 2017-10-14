# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c


class HELP_CHOICES(DjangoEnum):
    priority = Column(unique=False)

    records = ( ('HEAL', 0, 'лечение', 160),
                ('TELEPORT', 1, 'телепорт', 160),
                ('LIGHTING', 2, 'молния', 160),
                ('START_QUEST', 3, 'начало задания', 800),
                ('MONEY', 4, 'деньги', 40),
                ('RESURRECT', 5, 'воскрешение', 800),
                ('EXPERIENCE', 6, 'прозрение', 5),
                ('STOCK_UP_ENERGY', 7, 'запас энергии', 1),
                ('HEAL_COMPANION', 8, 'лечение спутника', 20))


class ABILITY_TYPE(DjangoEnum):
    cost = Column(unique=False)
    description = Column()
    request_attributes = Column(unique=False)

    records = ( ('HELP', 'help', 'Помочь', c.ANGEL_HELP_COST, 'Попытаться помочь герою, чем бы тот не занимался', ()),
                ('ARENA_PVP_1x1', 'arena_pvp_1x1', 'Отправить на арену', c.ANGEL_ARENA_COST, 'Отправить героя на гладиаторскую арену', ()),
                ('ARENA_PVP_1x1_LEAVE_QUEUE', 'arena_pvp_1x1_leave_queue', 'Выйти из очереди', c.ANGEL_ARENA_QUIT_COST, 'Выйти из очереди на арену', ()),
                ('ARENA_PVP_1x1_ACCEPT', 'arena_pvp_1x1_accept', 'Принять вызов', c.ANGEL_ARENA_COST, 'Принять вызов другого героя', ('battle',)),
                ('DROP_ITEM', 'drop_item', 'Выбросить предмет', c.ANGEL_DROP_ITEM_COST, 'Выбросить из рюкзака самый ненужный предмет', ()))
