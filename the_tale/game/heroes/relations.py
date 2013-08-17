# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum

from game.artifacts.models import ARTIFACT_TYPE

from game.heroes.statistics import MONEY_SOURCE

class PREFERENCE_TYPE(DjangoEnum):
    level_required = Column()
    base_name = Column()

    _records = ( ('MOB', 0, u'любимая добыча', 7, 'mob'),
                 ('PLACE', 1, u'родной город', 3, 'place'),
                 ('FRIEND', 2, u'соратник', 11, 'friend'),
                 ('ENEMY', 3, u'враг', 16, 'enemy'),
                 ('ENERGY_REGENERATION_TYPE', 4, u'религиозность', 1, 'energy_regeneration_type'),
                 ('EQUIPMENT_SLOT', 5, u'экипировка', 21, 'equipment_slot') )


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



class EQUIPMENT_SLOT(DjangoEnum):
    artifact_type = Column()

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
