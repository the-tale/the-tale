# coding: utf-8


from rels import Column
from rels.django_staff import DjangoEnum

class HELP_CHOICES(DjangoEnum):
    priority = Column(unique=False)

    _records = ( ('HEAL', 0, u'лечение', 160),
                 ('TELEPORT', 1, u'телепорт', 160),
                 ('LIGHTING', 2, u'молния', 160),
                 ('START_QUEST', 3, u'начало задания', 800),
                 ('MONEY', 4, u'деньги', 40),
                 ('RESURRECT', 5, u'воскрешение', 800),
                 ('EXPERIENCE', 6, u'прозрение', 20),
                 ('STOCK_UP_ENERGY', 7, u'запас энергии', 1))
