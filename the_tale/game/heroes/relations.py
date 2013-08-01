# coding: utf-8

from rels import Column
from rels.django_staff import DjangoEnum

from game.heroes.statistics import MONEY_SOURCE

class PREFERENCE_TYPE(DjangoEnum):
    level_required = Column()

    _records = ( ('MOB', 0, u'любимая добыча', 7),
                 ('PLACE', 1, u'родной город', 3),
                 ('FRIEND', 2, u'соратник', 11),
                 ('ENEMY', 3, u'враг', 16),
                 ('ENERGY_REGENERATION_TYPE', 4, u'религиозность', 1),
                 ('EQUIPMENT_SLOT', 5, u'экипировка', 21) )


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
