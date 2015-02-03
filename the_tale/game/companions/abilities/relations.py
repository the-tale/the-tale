# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class EFFECT(DjangoEnum):
    records = ( (u'COHERENCE_SPEED', 0, u'скорость изменения слаженности'),
                (u'CHANGE_HABITS', 1, u'изменение характера'),
                (u'QUEST_MONEY_REWARD', 2, u'денежная награда за задание'),
                (u'MAX_BAG_SIZE', 3, u'максимальный размер рюкзака'),
                (u'POLITICS_POWER', 4, u'бонус к влиянию'),
                (u'MAGIC_DAMAGE_BONUS', 5, u'бонус к магическому урону героя'),
                (u'PHYSIC_DAMAGE_BONUS', 6, u'бонус к физическому урону героя'))



class FIELDS(DjangoEnum):
    common = Column(unique=False)

    records = ( ('COHERENCE_SPEED', 0, u'слаженность', False),
                ('HONOR', 1, u'честь', False),
                ('PEACEFULNESS', 2, u'миролюбие', False),
                ('START_1', 3, u'начальная 1', False),
                ('START_2', 4, u'начальная 2', False),
                ('START_3', 5, u'начальная 3', False),
                ('ABILITY_1', 6, u'способность 1', True),
                ('ABILITY_2', 7, u'способность 2', True),
                ('ABILITY_3', 8, u'способность 3', True),
                ('ABILITY_4', 9, u'способность 4', True),
                ('ABILITY_5', 10, u'способность 5', True),
                ('ABILITY_6', 11, u'способность 6', True),
                ('ABILITY_7', 12, u'способность 7', True),
                ('ABILITY_8', 13, u'способность 8', True),
                ('ABILITY_9', 14, u'способность 9', True) )
