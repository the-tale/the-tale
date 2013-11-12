# coding: utf-8

from rels.django_staff import DjangoEnum


class ACHIEVEMENT_GROUP(DjangoEnum): # visualization
    _records = ( ('TIME', 0, u'Время'),
                 ('MONEY', 1, u'Деньги'),
                 ('MONSTERS', 2, u'Монстры'),
                 ('ARTIFACTS', 3, u'Артефакты'),
                 ('QUESTS', 4, u'Задания'),
                 ('DEATHS', 5, u'Смерти'))


class ACHIEVEMENT_TYPE(DjangoEnum): # filtration
    _records = ( ('TIME', 0, u'Время'),
                 ('MONEY', 1, u'Деньги'),
                 ('MONSTERS', 2, u'Монстры'),
                 ('ARTIFACTS', 3, u'Артефакты'),
                 ('QUESTS', 4, u'Задания'),
                 ('DEATHS', 5, u'Смерти'))
