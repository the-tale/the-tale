# coding: utf-8


from rels import Column
from rels.django_staff import DjangoEnum

class HELP_CHOICES(DjangoEnum):
    priority = Column(unique=False)

    _records = ( ('HEAL', 0, u'лечение', 4),
                 ('TELEPORT', 1, u'телепорт', 4),
                 ('LIGHTING', 2, u'молния', 4),
                 ('START_QUEST', 3, u'начало задания', 4),
                 ('MONEY', 4, u'деньги', 1),
                 ('RESURRECT', 5, u'воскрешение', 10) )
