# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum

from game.artifacts.models import ARTIFACT_TYPE

from game.heroes.statistics import MONEY_SOURCE

class RISK_LEVEL(DjangoEnum):
    health_percent_to_rest = Column()

    _records = ( ('VERY_HIGH', 0, u'очень высокий', 0.70),
                 ('HIGH',      1, u'высокий', 0.85),
                 ('NORMAL',    2, u'обычный', 1.00),
                 ('LOW',       3, u'низкий', 1.15),
                 ('VERY_LOW',  4, u'очень низкий', 1.30) )


class PREFERENCE_TYPE(DjangoEnum):
    level_required = Column()
    base_name = Column()
    prepair_method = Column(unique=False)
    nullable = Column(unique=False)

    _records = ( ('MOB', 0, u'любимая добыча', 43, 'mob', '_prepair_mob', True),
                 ('PLACE', 1, u'родной город', 4, 'place', '_prepair_place', True),
                 ('FRIEND', 2, u'соратник', 13, 'friend', '_prepair_person', True),
                 ('ENEMY', 3, u'противник', 26, 'enemy', '_prepair_person', True),
                 ('ENERGY_REGENERATION_TYPE', 4, u'религиозность', 1, 'energy_regeneration_type', '_prepair_value', False),
                 ('EQUIPMENT_SLOT', 5, u'экипировка', 34, 'equipment_slot', '_prepair_equipment_slot', True),
                 ('RISK_LEVEL', 6, u'уровень риска', 8, 'risk_level', '_prepair_risk_level', False),
                 ('FAVORITE_ITEM', 7, u'любимая вещь', 19, 'favorite_item', '_prepair_equipment_slot', True)
        )


class ITEMS_OF_EXPENDITURE(DjangoEnum):
    ui_id = Column()
    priority = Column(unique=False, primary=False)
    price_fraction = Column(unique=False, primary=False) # цена в доле от стандартной цены
    money_source = Column()

    _records = ( ('INSTANT_HEAL',        0, u'лечение',           'heal',       12, 0.3, MONEY_SOURCE.SPEND_FOR_HEAL),
                 ('BUYING_ARTIFACT',     1, u'покупка артефакта', 'artifact',   5,  1.5, MONEY_SOURCE.SPEND_FOR_ARTIFACTS),
                 ('SHARPENING_ARTIFACT', 2, u'заточка артефакта', 'sharpening', 4,  2.0, MONEY_SOURCE.SPEND_FOR_SHARPENING),
                 ('USELESS',             3, u'бесполезные траты', 'useless',    2,  0.4, MONEY_SOURCE.SPEND_FOR_USELESS),
                 ('IMPACT',              4, u'изменение влияния', 'impact',     4,  2.5, MONEY_SOURCE.SPEND_FOR_IMPACT),
                 ('EXPERIENCE',          5, u'обучение',          'experience', 1,  5.0, MONEY_SOURCE.SPEND_FOR_EXPERIENCE))

    @classmethod
    def get_quest_upgrade_equipment_fraction(cls):
        QUEST_PRICE_MODIFIER = 2
        return max(cls.BUYING_ARTIFACT.price_fraction, cls.SHARPENING_ARTIFACT.price_fraction) * QUEST_PRICE_MODIFIER




class EQUIPMENT_SLOT(DjangoEnum):
    artifact_type = Column(related_name='equipment_slot')

    _records = ( ('HAND_PRIMARY', 0, u'основная рука', ARTIFACT_TYPE.MAIN_HAND),
                 ('HAND_SECONDARY', 1, u'вспомогательная рука', ARTIFACT_TYPE.OFF_HAND),
                 ('HELMET', 2, u'шлем', ARTIFACT_TYPE.HELMET),
                 ('SHOULDERS', 3, u'наплечники', ARTIFACT_TYPE.SHOULDERS),
                 ('PLATE', 4, u'доспех', ARTIFACT_TYPE.PLATE),
                 ('GLOVES', 5, u'перчатки', ARTIFACT_TYPE.GLOVES),
                 ('CLOAK', 6, u'плащ', ARTIFACT_TYPE.CLOAK),
                 ('PANTS', 7, u'штаны', ARTIFACT_TYPE.PANTS),
                 ('BOOTS', 8, u'сапоги', ARTIFACT_TYPE.BOOTS),
                 ('AMULET', 9, u'амулет', ARTIFACT_TYPE.AMULET),
                 ('RING', 10, u'кольцо', ARTIFACT_TYPE.RING) )
