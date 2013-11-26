# coding: utf-8

from rels.django import DjangoEnum


class ARTIFACT_TYPE(DjangoEnum):

    records = ( ('USELESS', 0, u'хлам'),
                 ('MAIN_HAND', 1, u'основная рука'),
                 ('OFF_HAND', 2, u'вторая рука'),
                 ('PLATE', 3, u'броня'),
                 ('AMULET', 4, u'амулет'),
                 ('HELMET', 5, u'шлем'),
                 ('CLOAK', 6, u'плащ'),
                 ('SHOULDERS', 7, u'наплечники'),
                 ('GLOVES', 8, u'перчатки'),
                 ('PANTS', 9, u'штаны'),
                 ('BOOTS', 10, u'сапоги'),
                 ('RING', 11, u'кольцо') )
