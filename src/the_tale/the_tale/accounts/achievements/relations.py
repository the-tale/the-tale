# coding: utf-8

import rels
from rels.django import DjangoEnum


class ACHIEVEMENT_GROUP(DjangoEnum): # visualization
    slug = rels.Column()

    records = ( ('TIME', 0, 'Время', 'time'),
                ('MONEY', 1, 'Деньги', 'money'),
                ('MOBS', 2, 'Монстры', 'mobs'),
                ('ARTIFACTS', 3, 'Артефакты', 'artifacts'),
                ('QUESTS', 4, 'Задания', 'quests'),
                ('DEATHS', 5, 'Смерти', 'deaths'),
                ('PVP', 6, 'PvP', 'pvp'),
                ('POLITICS', 7, 'Политика', 'politics'),
                ('KEEPER', 8, 'Хранитель', 'keeper'),
                ('CHARACTER', 9, 'Характер', 'character'),
                ('CARDS', 10, 'Карты Судьбы', 'cards'),
                ('LEGENDS', 11, 'Легенды', 'legends'))


class ACHIEVEMENTS_SOURCE(DjangoEnum):
    records = ( ('ACCOUNT', 0, 'аккаунт'),
                ('GAME_OBJECT', 1, 'игровой объект'),
                ('NONE', 2, 'нет источника'))


class ACHIEVEMENT_TYPE(DjangoEnum): # filtration
    source = rels.Column(unique=False)

    records = ( ('TIME', 0, 'Время', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('MONEY', 1, 'Деньги', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('MOBS', 2, 'Монстры', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('ARTIFACTS', 3, 'Артефакты', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('QUESTS', 4, 'Задания', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('DEATHS', 5, 'Смерти', ACHIEVEMENTS_SOURCE.GAME_OBJECT),

                ('PVP_BATTLES_1X1', 6, 'PvP бои', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('PVP_VICTORIES_1X1', 7, 'Процент PvP побед', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('POLITICS_ACCEPTED_BILLS', 8, 'Принятые законы', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('POLITICS_VOTES_TOTAL', 9, 'Отданные голосов', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('POLITICS_VOTES_FOR', 10, 'Голоса, отданные «за»', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('POLITICS_VOTES_AGAINST', 11, 'Голоса, отданные «против»', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('KEEPER_HELP_COUNT', 12, 'Помощь герою', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('KEEPER_MIGHT', 13, 'Могущество', ACHIEVEMENTS_SOURCE.ACCOUNT),
                ('HABITS_HONOR', 14, 'Черты: Честь', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('HABITS_PEACEFULNESS', 15, 'Черты: Миролюбие', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('KEEPER_CARDS_USED', 16, 'Использовано карт', ACHIEVEMENTS_SOURCE.GAME_OBJECT),
                ('KEEPER_CARDS_COMBINED', 17, 'Объединено карт', ACHIEVEMENTS_SOURCE.GAME_OBJECT),

                ('LEGENDS', 18, 'Легендарный подвиг', ACHIEVEMENTS_SOURCE.NONE)
        )
