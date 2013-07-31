# coding: utf-8


from rels import Column
from rels.django_staff import DjangoEnum

class HELP_CHOICES(DjangoEnum):
    priority = Column(unique=False)

    _records = ( ('HEAL', 0, u'лечение', 8),
                 ('TELEPORT', 1, u'телепорт', 8),
                 ('LIGHTING', 2, u'молния', 8),
                 ('START_QUEST', 3, u'начало задания', 40),
                 ('MONEY', 4, u'деньги', 2),
                 ('RESURRECT', 5, u'воскрешение', 40),
                 ('EXPERIENCE', 6, u'прозрение', 1))
