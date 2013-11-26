# coding: utf-8

import rels
from rels.django import DjangoEnum


class ACHIEVEMENT_GROUP(DjangoEnum): # visualization
    slug = rels.Column()

    records = ( ('TIME', 0, u'Время', 'time'),
                 ('MONEY', 1, u'Деньги', 'money'),
                 ('MOBS', 2, u'Монстры', 'mobs'),
                 ('ARTIFACTS', 3, u'Артефакты', 'artifacts'),
                 ('QUESTS', 4, u'Задания', 'quests'),
                 ('DEATHS', 5, u'Смерти', 'deaths'))


class ACHIEVEMENT_TYPE(DjangoEnum): # filtration
    records = ( ('TIME', 0, u'Время'),
                 ('MONEY', 1, u'Деньги'),
                 ('MOBS', 2, u'Монстры'),
                 ('ARTIFACTS', 3, u'Артефакты'),
                 ('QUESTS', 4, u'Задания'),
                 ('DEATHS', 5, u'Смерти'))
