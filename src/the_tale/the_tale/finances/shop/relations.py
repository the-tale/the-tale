# coding: utf-8

from rels import Column, NullObject
from rels.django import DjangoEnum

from the_tale.accounts.clans.conf import clans_settings

from the_tale.game.artifacts.relations import RARITY


INFINIT_PREMIUM_DESCRIPTION = 'Вечная подписка даёт вам все бонусы подписчика на всё время игры.'


class PERMANENT_PURCHASE_TYPE(DjangoEnum):
    description = Column(unique=False)
    might_required = Column(unique=False, single_type=False)
    level_required = Column(unique=False, single_type=False)
    full_name = Column()

    records = (('INFINIT_SUBSCRIPTION', 12, 'Вечная подписка', INFINIT_PREMIUM_DESCRIPTION, None, None, 'Вечная подписка'),)


class RANDOM_PREMIUM_CHEST_REWARD(DjangoEnum):
    priority = Column(unique=False)
    description = Column(unique=False)
    arguments = Column(unique=False, no_index=True)
    hero_method = Column(unique=False)

    records = ( ('NORMAL_ARTIFACT', 0, 'обычный артефакт', 60, 'случайный обычный артефакт (лучше среднего для текущего уровня героя)',
                 {'rarity': RARITY.NORMAL, 'better': True}, 'purchase_artifact'),
                ('ENERGY', 1, 'энергия',                   20, '500 энергии',
                 {'energy': 500}, 'purchase_energy_bonus'),
                ('RARE_ARTIFACT', 2, 'редкий артефакт',    15, 'случайный редкий артефакт',
                 {'rarity': RARITY.RARE, 'better': False}, 'purchase_artifact'),
                ('EXPERIENCE', 3, 'опыт',                  4,  '1500 опыта',
                 {'experience': 1500}, 'purchase_experience'),
                ('EPIC_ARTIFACT', 4, 'эпический артефакт', 1,  'случайный эпический артефакт',
                 {'rarity': RARITY.EPIC, 'better': False}, 'purchase_artifact'),)


class GOODS_GROUP(DjangoEnum):
    uid = Column()
    uid_prefix = Column(unique=False)

    records = ( ('PREMIUM', 0, 'подписка', 'subscription', 'subscription-'),
                ('ENERGY', 1, 'энергия', 'energy', 'energy-'),
                ('CHEST', 2, 'сундук', 'random-premium-chest', 'random-premium-chest'),
                ('PREFERENCES', 3, 'предпочтения', 'preference', 'preference-'),
                ('PREFERENCES_RESET', 4, 'сброс предпочтений', 'preference-reset','hero-preference-reset-'),
                ('HABITS', 5, 'черты', 'habits', 'hero-habits-'),
                ('ABILITIES', 6, 'способности', 'abilities', 'hero-abilities-'),
                ('CLANS', 7, 'гильдии', 'clans', 'clan-'),
                ('CARDS', 8, 'Карты судьбы', 'cards', 'cards-') )
