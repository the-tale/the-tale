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
                ('DEATHS', 5, u'Смерти', 'deaths'),
                ('PVP', 6, u'PvP', 'pvp'),
                ('POLITICS', 7, u'Политика', 'politics'),
                ('KEEPER', 8, u'Хранитель', 'keeper'),
                ('CHARACTER', 9, u'Характер', 'character'))


class ACHIEVEMENTS_SOURCE(DjangoEnum):
    records = ( ('ACCOUNT', 0, u'аккаунт'),
                ('GAME_OBJECT', 1, u'игровой объект'))


class ACHIEVEMENT_TYPE(DjangoEnum): # filtration
    source = rels.Column(unique=False)

    records = ( ('TIME', 0, u'Время', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('MONEY', 1, u'Деньги', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('MOBS', 2, u'Монстры', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('ARTIFACTS', 3, u'Артефакты', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('QUESTS', 4, u'Задания', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('DEATHS', 5, u'Смерти', ACHIEVEMENTS_SOURCE.GAME_OBJECT),

                ('PVP_BATTLES_1X1', 6, u'PvP бои', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('PVP_VICTORIES_1X1', 7, u'Процент PvP побед', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('POLITICS_ACCEPTED_BILLS', 8, u'Принятые законы', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('POLITICS_VOTES_TOTAL', 9, u'Отданные голосов', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('POLITICS_VOTES_FOR', 10, u'Голоса, отданные «за»', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('POLITICS_VOTES_AGAINST', 11, u'Голоса, отданные «против»', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('KEEPER_HELP_COUNT', 12, u'Помощь герою', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('KEEPER_MIGHT', 13, u'Могущество', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('HABITS_HONOR', 14, u'Черты: Честь', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('HABITS_PEACEFULNESS', 15, u'Черты: Миролюбие', ACHIEVEMENTS_SOURCE.GAME_OBJECT)
        )
