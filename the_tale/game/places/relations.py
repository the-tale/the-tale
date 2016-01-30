# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c


class BUILDING_STATE(DjangoEnum):
    records = ( ('WORKING', 0, u'работает'),
                ('DESTROYED', 1, u'уничтожено') )


class BUILDING_TYPE(DjangoEnum):
    records = ( ('SMITHY', 0, u'кузница'),
                ('FISHING_LODGE', 1, u'домик рыболова'),
                ('TAILOR_SHOP', 2, u'мастерская портного'),
                ('SAWMILL', 3, u'лесопилка'),
                ('HUNTER_HOUSE', 4, u'домик охотника'),
                ('WATCHTOWER', 5, u'сторожевая башня'),
                ('TRADING_POST', 6, u'торговый пост'),
                ('INN', 7, u'трактир'),
                ('DEN_OF_THIEVE', 8, u'логово вора'),
                ('FARM', 9, u'ферма'),
                ('MINE', 10, u'шахта'),
                ('TEMPLE', 11, u'храм'),
                ('HOSPITAL', 12, u'больница'),
                ('LABORATORY', 13, u'лаборатория'),
                ('SCAFFOLD', 14, u'плаха'),
                ('MAGE_TOWER', 15, u'башня мага'),
                ('GUILDHALL', 16, u'ламбард'),
                ('BUREAU', 17, u'бюро'),
                ('MANOR', 18, u'цех'),
                ('SCENE', 19, u'сцена'),
                ('MEWS', 20, u'конюшни'),
                ('RANCH', 21, u'ранчо') )


class ATTRIBUTE_TYPE(DjangoEnum):
    records = ( ('AGGREGATED', 0, u'аггрегируемый'),
                ('CALCULATED', 1, u'вычисляемый'))


class ATTRIBUTE(DjangoEnum):
    default = Column(unique=False, primary=False, single_type=False)
    type = Column(unique=False, primary=False)
    order = Column(unique=False, primary=False)
    description = Column(primary=False)

    records = ( ('SIZE', 0, u'размер города', lambda: 1, ATTRIBUTE_TYPE.CALCULATED, 1,
                 u'Влияет на количество советников в городе, развитие специализаций и на потребление товаров его жителями. Зависит от производства товаров.'),
                # ('ECONOMIC', 1, u'размер экономики', lambda: 1, ATTRIBUTE_TYPE.AGGREGATED, 1,
                #  u'Определяет скорость производства товаров городом.'),
                ('TERRAIN_RADIUS', 2, u'радиус изменений', lambda: 0, ATTRIBUTE_TYPE.CALCULATED, 1,
                 u'Радиус в котором город изменяет мир (в клетках).'),
                ('POLITIC_RADIUS', 3, u'радиус владений', lambda: 0, ATTRIBUTE_TYPE.CALCULATED, 1,
                 u'Максимальное расстояние, на которое могут распространяться границы владений города (в клетках).'),
                ('PRODUCTION', 4, u'производство', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Скорость производства товаров. Зависит от размера экономики города и состава его совета.'),
                ('GOODS', 5, u'товары', lambda: 0, ATTRIBUTE_TYPE.CALCULATED, 1,
                 u'Чтобы расти, город должен производить товары. Если их накапливается достаточно, то размер города увеличивается. Если товары кончаются, то уменьшается.'),
                ('KEEPERS_GOODS', 6, u'дары Хранителей', lambda: 0, ATTRIBUTE_TYPE.CALCULATED, 1,
                 u'Хранители могут подарить городу дополнительные товары, которые будут постепенно переводиться в производство (%2.f%% в час, но не менее %d). Чтобы сделать городу подарок, Вы можете использовать соответствующую Карту Судьбы.' % (c.PLACE_KEEPERS_GOODS_SPENDING*100, c.PLACE_GOODS_BONUS)),
                ('SAFETY', 7, u'безопасность', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Насколько безопасно в окрестностях города (вероятность пройти по миру, не подвергнувшись нападению).'),
                ('TRANSPORT', 8, u'транспорт', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Уровень развития транспортной инфраструктуры (с какой скоростью герои путешествуют в окрестностях города).'),
                ('FREEDOM', 9, u'свобода', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Насколько активна политическая жизнь в городе (как сильно изменяется влияние советников от действий героев).'),
                ('TAX', 10, u'пошлина', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Размер пошлины, которую платят герои при посещении города (процент от наличности в кошельке героя).'),
                ('STABILITY', 11, u'стабильность', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, 0,
                 u'Отражает текущую ситуацию в городе и влияет на многие его параметры. Уменьшается от изменений, происходящих в городе (при принятии законов), и постепенно восстанавливается до 100%.'),
                ('STABILITY_RENEWING_SPEED', 12, u'восстанволение стабильности', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, -1,
                 u'Скорость восстановления стабильности в городе.'),
                ('EXPERIENCE', 13, u'количество опыта', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Количество опыта за задания, связанные с этим городом.'),
                ('BUY_PRICE', 14, u'цена попупки предметов', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Цена покупки артефактов.'),
                ('SELL_PRICE', 15, u'цена продажи предметов', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Цена продажи предметов.'),
                ('BUY_ARTIFACT_POWER', 16, u'сила покупаемых артефактов', lambda: 0.0, ATTRIBUTE_TYPE.AGGREGATED, 0,
                 u'Сила артефактов, которые герой приобретает в городе.'),
                ('TERRAIN_RADIUS_MODIFIER', 17, u'относительный радиус изменений', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 0,
                 u'Относительный радиус в котором город изменяет мир.'),
                ('POLITIC_RADIUS_MODIFIER', 18, u'относительный радиус владений', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 0,
                 u'Относительное максимальное расстояние, на которое могут распространяться границы владений города.'),
                ('ENERGY_REGEN_CHANCE', 19, u'восстановление энергии', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Шанс восстановить энергию при входе в город.'),
                ('HERO_REGEN_CHANCE', 20, u'лечение героя', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Шанс героя полностью вылечиться при входе в город.'),
                ('COMPANION_REGEN_CHANCE', 21, u'лечение спутника', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Шанс спутника подлечиться при входе в город.'),
                ('POWER_ECONOMIC', 22, u'экономика влияния', lambda: 1, ATTRIBUTE_TYPE.CALCULATED, 1,
                 u'Определяет скорость производства товаров городом. Зависит от общей суммы влияния, поступившего в город, в результате выполнения героями заданий за определённый период времени (примерное количество недель: %d). Влияние от задания может быть отрицательным. Чем больше суммарное влияние по сравнению с другими городами, тем больше размер экономики.' % c.PLACE_POWER_HISTORY_WEEKS),

                ('MODIFIER_TRADE_CENTER', 23, u'Специализация «Торговый центр»', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Соответствие города специализации «Торговый центр».'),
                ('MODIFIER_CRAFT_CENTER', 24, u'Специализация «Город мастеров»', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Соответствие города специализации «Город мастеров».'),
                ('MODIFIER_FORT', 25, u'Специализация «Форт»', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Соответствие города специализации «Форт».'),
                ('MODIFIER_POLITICAL_CENTER', 26, u'Специализация «Политический центр»', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Соответствие города специализации «Политический центр».'),
                ('MODIFIER_POLIC', 27, u'Специализация «Полис»', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Соответствие города специализации «Полис».'),
                ('MODIFIER_RESORT', 28, u'Специализация «Курорт»', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Соответствие города специализации «Курорт».'),
                ('MODIFIER_TRANSPORT_NODE', 29, u'Специализация «Транспортный узел»', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Соответствие города специализации «Транспортный узел».'),
                ('MODIFIER_OUTLAWS', 30, u'Специализация «Вольница»', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Соответствие города специализации «Вольница».'),
                ('MODIFIER_HOLY_CITY', 31, u'Специализация «Святой город»', lambda: 0, ATTRIBUTE_TYPE.AGGREGATED, 1,
                 u'Соответствие города специализации «Святой город».')  )


    EFFECTS_ORDER = sorted(set(record[-2] for record in records))


class RESOURCE_EXCHANGE_TYPE(DjangoEnum):
    parameter = Column(unique=False, primary=False, single_type=False)
    amount = Column(unique=False, primary=False, single_type=False)
    direction = Column(unique=False, primary=False)

    PRODUCTION_BASE = int(c.PLACE_GOODS_BONUS / 2)
    SAFETY_BASE = c.PLACE_SAFETY_FROM_BEST_PERSON / 10.0
    TRANSPORT_BASE = c.PLACE_TRANSPORT_FROM_BEST_PERSON / 10.0
    TAX_BASE = 0.025

    records = ( ('NONE',  0, u'ничего', None, 0, 0),

                ('PRODUCTION_SMALL',  1, u'%d продукции' % PRODUCTION_BASE, ATTRIBUTE.PRODUCTION, PRODUCTION_BASE, 1),
                ('PRODUCTION_NORMAL', 2, u'%d продукции' % (PRODUCTION_BASE * 2), ATTRIBUTE.PRODUCTION, PRODUCTION_BASE * 2, 1),
                ('PRODUCTION_LARGE',  3, u'%d продукции' % (PRODUCTION_BASE * 4), ATTRIBUTE.PRODUCTION, PRODUCTION_BASE * 4, 1),

                ('SAFETY_SMALL',      4, u'%.1f%% безопасности' % float(SAFETY_BASE * 100), ATTRIBUTE.SAFETY, SAFETY_BASE, 1),
                ('SAFETY_NORMAL',     5, u'%.1f%% безопасности' % float(SAFETY_BASE * 2 * 100), ATTRIBUTE.SAFETY, SAFETY_BASE * 2, 1),
                ('SAFETY_LARGE',      6, u'%.1f%% безопасности' % float(SAFETY_BASE * 4 * 100), ATTRIBUTE.SAFETY, SAFETY_BASE * 4, 1),

                ('TRANSPORT_SMALL',   7, u'%.1f%% транспорта' % float(TRANSPORT_BASE * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE, 1),
                ('TRANSPORT_NORMAL',  8, u'%.1f%% транспорта' % float(TRANSPORT_BASE * 2 * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE * 2, 1),
                ('TRANSPORT_LARGE',   9, u'%.1f%% транспорта' % float(TRANSPORT_BASE * 4 * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE * 4, 1),

                ('TAX_SMALL',   10, u'%.1f%% пошлины' % float(TAX_BASE * 100), ATTRIBUTE.TAX, TAX_BASE, -1),
                ('TAX_NORMAL',  11, u'%.1f%% пошлины' % float(TAX_BASE * 2 * 100), ATTRIBUTE.TAX, TAX_BASE * 2, -1),
                ('TAX_LARGE',   12, u'%.1f%% пошлины' % float(TAX_BASE * 4 * 100), ATTRIBUTE.TAX, TAX_BASE * 4, -1) )
