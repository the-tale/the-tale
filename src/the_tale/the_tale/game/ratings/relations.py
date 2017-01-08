# coding: utf-8

import rels
from rels.django import DjangoEnum

from the_tale.game.heroes.conf import heroes_settings


class RATING_TYPE(DjangoEnum):
    hint = rels.Column(primary=False, unique=False)
    field = rels.Column()

    records = ( ('MIGHT', 'might', 'Могущество', '', 'might'),
                ('BILLS', 'bills', 'Принятые записи в Книге Судеб', '', 'bills_count'),
                ('MAGIC_POWER', 'magic-power', 'Магическая сила героя', '', 'magic_power'),
                ('PHYSIC_POWER', 'physic-power', 'Физическая сила героя', '', 'physic_power'),
                ('LEVEL', 'level', 'Уровень героя', '', 'level'),
                ('PHRASES', 'phrases', 'Добавленные фразы', '', 'phrases_count'),
                ('PVP_BATTLES_1x1_NUMBER', 'pvp_battles_1x1_number', 'Сражения в PvP', '', 'pvp_battles_1x1_number'),
                ('PVP_BATTLES_1x1_VICTORIES', 'pvp_battles_1x1_victories', 'Победы в PvP',
                 'Для участия в рейтинге необходимо провести минимум %(min_pvp_battles)s боёв' % {'min_pvp_battles': heroes_settings.MIN_PVP_BATTLES}, 'pvp_battles_1x1_victories'),
                ('REFERRALS_NUMBER', 'referrals_number', 'Последователи', '', 'referrals_number'),
                ('ACHIEVEMENTS_POINTS', 'achievements_points', 'Очки достижений', '', 'achievements_points'),
                ('HELP_COUNT', 'help_count', 'Помощь герою', '', 'help_count'),
                ('GIFTS_RETURNED', 'gifts_returned', 'Возвращено подарков',
                 'Во время путешествия герой может найти потерянный детский подарок. Если помочь герою, когда подарок находится в рюкзаке, то он вернётся к ребёнку.',
                 'gifts_returned'),
                ('POLITICS_POWER', 'politics_power', 'Влиятельность', 'Влияние, которое герой оказывает своими заданиями (участвуют только герои, влияющие на всех Мастеров)', 'politics_power'),
              )
