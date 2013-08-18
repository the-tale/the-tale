# coding: utf-8

from rels import Column, NullObject
from rels.django_staff import DjangoEnum

from accounts.clans.conf import clans_settings

from game.heroes.relations import PREFERENCE_TYPE


CLAN_OWNERSHIP_RIGHT_DESCRIPTION = u'Если вам не хватает могущества для владения гильдией, Вы можете приобрести разрешение на владение ей за печеньки.'
PREFERENCE_DESCRIPTION = u'Убрать ограничение на уровень героя'


def preference_record(id, preference_type):
    return ('PREFERENCE_%s' % preference_type.name,
            id,
            u'Предпочтение «%s»' % preference_type.text,
            PREFERENCE_DESCRIPTION,
            None,
            preference_type.level_required,
            preference_type)


class PERMANENT_PURCHASE_TYPE(DjangoEnum):
    description = Column(unique=False)
    might_required = Column(unique=False, single_type=False)
    level_required = Column(unique=False, single_type=False)
    preference_type = Column(single_type=False, related_name='purchase_type')

    _records = ( ('CLAN_OWNERSHIP_RIGHT', 0, u'Разрешение на владение гильдией',
                  CLAN_OWNERSHIP_RIGHT_DESCRIPTION, clans_settings.OWNER_MIGHT_REQUIRED, None, NullObject()),

                  preference_record(1, PREFERENCE_TYPE.MOB),
                  preference_record(2, PREFERENCE_TYPE.PLACE),
                  preference_record(3, PREFERENCE_TYPE.FRIEND),
                  preference_record(4, PREFERENCE_TYPE.ENEMY),
                  preference_record(5, PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE),
                  preference_record(6, PREFERENCE_TYPE.EQUIPMENT_SLOT)  )
