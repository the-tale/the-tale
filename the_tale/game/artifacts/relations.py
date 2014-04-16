# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance.power import PowerDistribution


class ARTIFACT_TYPE(DjangoEnum):

    records = ( ('USELESS', 0, u'хлам'),
                 ('MAIN_HAND', 1, u'основная рука'),
                 ('OFF_HAND', 2, u'вторая рука'),
                 ('PLATE', 3, u'доспех'),
                 ('AMULET', 4, u'амулет'),
                 ('HELMET', 5, u'шлем'),
                 ('CLOAK', 6, u'плащ'),
                 ('SHOULDERS', 7, u'наплечники'),
                 ('GLOVES', 8, u'перчатки'),
                 ('PANTS', 9, u'штаны'),
                 ('BOOTS', 10, u'обувь'),
                 ('RING', 11, u'кольцо') )



class ARTIFACT_POWER_TYPE(DjangoEnum):
    distribution = Column()

    records = ( ('MOST_MAGICAL', 0, u'магический', PowerDistribution(0.1, 0.9)),
                ('MAGICAL', 1, u'больше магический', PowerDistribution(0.25, 0.75)),
                ('NEUTRAL', 2, u'нейтральный', PowerDistribution(0.5, 0.5)),
                ('PHYSICAL', 3, u'больше физический', PowerDistribution(0.75, 0.25)),
                ('MOST_PHYSICAL', 4, u'физический', PowerDistribution(0.9, 0.1)) )


class ARTIFACT_RECORD_STATE(DjangoEnum):
    records = ( ('ENABLED', 0, u'в игре'),
                ('DISABLED', 1, u'вне игры') )
