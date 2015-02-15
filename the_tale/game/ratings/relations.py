# coding: utf-8

import rels
from rels.django import DjangoEnum

from the_tale.game.heroes.conf import heroes_settings


class RATING_TYPE(DjangoEnum):
    hint = rels.Column(primary=False, unique=False)
    field = rels.Column()

    records = ( ('MIGHT', 'might', u'Могущество', u'', 'might'),
                ('BILLS', 'bills', u'Принятые законы', u'', 'bills_count'),
                ('MAGIC_POWER', 'magic-power', u'Магическая сила героя', u'', 'magic_power'),
                ('PHYSIC_POWER', 'physic-power', u'Физическая сила героя', u'', 'physic_power'),
                ('LEVEL', 'level', u'Уровень героя', u'', 'level'),
                ('PHRASES', 'phrases', u'Добавленные фразы', u'', 'phrases_count'),
                ('PVP_BATTLES_1x1_NUMBER', 'pvp_battles_1x1_number', u'Сражения в PvP', u'', 'pvp_battles_1x1_number'),
                ('PVP_BATTLES_1x1_VICTORIES', 'pvp_battles_1x1_victories', u'Победы в PvP',
                 u'Для участия в рейтинге необходимо провести минимум %(min_pvp_battles)s боёв' % {'min_pvp_battles': heroes_settings.MIN_PVP_BATTLES}, 'pvp_battles_1x1_victories'),
                ('REFERRALS_NUMBER', 'referrals_number', u'Последователи', u'', 'referrals_number'),
                ('ACHIEVEMENTS_POINTS', 'achievements_points', u'Очки достижений', u'', 'achievements_points'),
                ('HELP_COUNT', 'help_count', u'Помощь герою', u'', 'help_count'),
                ('GIFTS_RETURNED', 'gifts_returned', u'Возвращено подарков',
                 u'Во время путешествия герой может найти потерянный детский подарок. Если помочь герою, когда подарок находится в рюкзаке, то он вернётся к ребёнку.',
                 'gifts_returned'))
