# coding: utf-8

import rels
from rels.django import DjangoEnum

from the_tale.game.heroes.conf import heroes_settings


class RATING_TYPE(DjangoEnum):
    hint = rels.Column(primary=False, unique=False)

    records = ( ('MIGHT', 'might', u'Могущество', u''),
                ('BILLS', 'bills', u'Принятые законы', u''),
                ('MAGIC_POWER', 'magic-power', u'Магическая сила героя', u''),
                ('PHYSIC_POWER', 'physic-power', u'Физическая сила героя', u''),
                ('LEVEL', 'level', u'Уровень героя', u''),
                ('PHRASES', 'phrases', u'Добавленные фразы', u''),
                ('PVP_BATTLES_1x1_NUMBER', 'pvp_battles_1x1_number', u'Сражения в PvP', u''),
                ('PVP_BATTLES_1x1_VICTORIES', 'pvp_battles_1x1_victories', u'Победы в PvP',
                 u'Для участия в рейтинге необходимо провести минимум %(min_pvp_battles)s боёв' % {'min_pvp_battles': heroes_settings.MIN_PVP_BATTLES}),
                ('REFERRALS_NUMBER', 'referrals_number', u'Последователи', u''),
                ('ACHIEVEMENTS_POINTS', 'achievements_points', u'Очки достижений', u''),
                ('HELP_COUNT', 'help_count', u'Помощь герою', u''),
                ('GIFTS_RETURNED', 'gifts_returned', u'Возвращено подарков',
                 u'Во время путешествия герой может найти потерянный детский подарок. Если помочь герою, когда подарок находится в рюкзаке, то он вернётся к ребёнку.'))
