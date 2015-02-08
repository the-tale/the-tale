# coding: utf-8

from rels import Column, NullObject
from rels.django import DjangoEnum

from the_tale.accounts.clans.conf import clans_settings

from the_tale.game.heroes.relations import PREFERENCE_TYPE
from the_tale.game.artifacts.relations import RARITY


CLAN_OWNERSHIP_RIGHT_DESCRIPTION = u'Если вам не хватает могущества для владения гильдией, Вы можете приобрести разрешение на владение ей за печеньки.'
PREFERENCE_DESCRIPTION = u'Убрать ограничение на уровень героя'


def preference_record(id, preference_type):
    return ('PREFERENCE_%s' % preference_type.name,
            id,
            preference_type.text,
            PREFERENCE_DESCRIPTION,
            None,
            preference_type.level_required,
            preference_type,
            u'Предпочтение "%s"' % preference_type.text)


class PERMANENT_PURCHASE_TYPE(DjangoEnum):
    description = Column(unique=False)
    might_required = Column(unique=False, single_type=False)
    level_required = Column(unique=False, single_type=False)
    preference_type = Column(single_type=False, related_name='purchase_type')
    full_name = Column()

    records = ( ('CLAN_OWNERSHIP_RIGHT', 0, u'Разрешение на владение гильдией',
                  CLAN_OWNERSHIP_RIGHT_DESCRIPTION, clans_settings.OWNER_MIGHT_REQUIRED, None, NullObject(), u'Разрешение на владение гильдией'),

                  preference_record(1, PREFERENCE_TYPE.MOB),
                  preference_record(2, PREFERENCE_TYPE.PLACE),
                  preference_record(3, PREFERENCE_TYPE.FRIEND),
                  preference_record(4, PREFERENCE_TYPE.ENEMY),
                  preference_record(5, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE),
                  preference_record(6, PREFERENCE_TYPE.EQUIPMENT_SLOT),
                  preference_record(7, PREFERENCE_TYPE.RISK_LEVEL),
                  preference_record(8, PREFERENCE_TYPE.FAVORITE_ITEM),
                  preference_record(9, PREFERENCE_TYPE.ARCHETYPE),
                  preference_record(10, PREFERENCE_TYPE.COMPANION_DEDICATION),
                  preference_record(11, PREFERENCE_TYPE.COMPANION_EMPATHY))


class RANDOM_PREMIUM_CHEST_REWARD(DjangoEnum):
    priority = Column(unique=False)
    description = Column(unique=False)
    arguments = Column(unique=False, no_index=True)
    hero_method = Column(unique=False)

    records = ( ('NORMAL_ARTIFACT', 0, u'обычный артефакт', 60, u'случайный обычный артефакт (лучше среднего для текущего уровня героя)',
                 {'rarity': RARITY.NORMAL, 'better': True}, 'purchase_artifact'),
                ('ENERGY', 1, u'энергия',                   20, u'500 энергии',
                 {'energy': 500}, 'purchase_energy_bonus'),
                ('RARE_ARTIFACT', 2, u'редкий артефакт',    15, u'случайный редкий артефакт',
                 {'rarity': RARITY.RARE, 'better': False}, 'purchase_artifact'),
                ('EXPERIENCE', 3, u'опыт',                  4,  u'1500 опыта',
                 {'experience': 1500}, 'purchase_experience'),
                ('EPIC_ARTIFACT', 4, u'эпический артефакт', 1,  u'случайный эпический артефакт',
                 {'rarity': RARITY.EPIC, 'better': False}, 'purchase_artifact'),)


class GOODS_GROUP(DjangoEnum):
    uid = Column()
    uid_prefix = Column(unique=False)

    records = ( ('PREMIUM', 0, u'подписка', 'subscription', 'subscription-'),
                ('ENERGY', 1, u'энергия', 'energy', 'energy-'),
                ('CHEST', 2, u'сундук', 'random-premium-chest', 'random-premium-chest'),
                ('PREFERENCES', 3, u'предпочтения', 'preference', 'preference-'),
                ('PREFERENCES_RESET', 4, u'сброс предпочтений', 'preference-reset','hero-preference-reset-'),
                ('HABITS', 5, u'черты', 'habits', 'hero-habits-'),
                ('ABILITIES', 6, u'способности', 'abilities', 'hero-abilities-'),
                ('CLANS', 7, u'гильдии', 'clans', 'clan-'),
                ('CARDS', 8, u'Карты судьбы', 'cards', 'cards-') )
