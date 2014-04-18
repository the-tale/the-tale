# coding: utf-8

from rels import Column, NullObject
from rels.django import DjangoEnum

from the_tale.accounts.clans.conf import clans_settings

from the_tale.game.heroes.relations import PREFERENCE_TYPE


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
                  preference_record(9, PREFERENCE_TYPE.ARCHETYPE))


class RANDOM_PREMIUM_CHEST_REWARD(DjangoEnum):
    priority = Column(unique=False)
    description = Column(unique=False)
    arguments = Column(unique=False, no_index=True)
    hero_method = Column()

    records = ( ('ARTIFACT', 0, u'артефакт', 6, u'случайный артефакт (лучше среднего для текущего уровня героя)', {}, 'purchase_artifact'),
                ('ENERGY', 1, u'энергия', 3, u'750 энергии', {'energy': 750}, 'purchase_energy_bonus'),
                ('EXPERIENCE', 2, u'опыт', 1, u'1500 опыта', {'experience': 1500}, 'purchase_experience') )


class GOODS_GROUP(DjangoEnum):
    uid_prefix = Column(unique=False)

    records = ( ('PREMIUM', 0, u'подписка', 'subscription-'),
                ('ENERGY', 1, u'энергия', 'energy-'),
                ('CHEST', 2, u'сундук', 'random-premium-chest'),
                ('PREFERENCES', 3, u'предпочтения', 'preference-'),
                ('PREFERENCE_RESET', 4 , u'сброс предпочтений', 'hero-preference-reset-'),
                ('HABITS', 5, u'черты', 'hero-habits-'),
                ('ABILITIES', 6, u'способности', 'hero-abilities-'),
                ('CLANS', 7, u'гильдии', 'clan-')  )
