# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c

from the_tale.game import attributes


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
                ('GUILDHALL', 16, u'ломбард'),
                ('BUREAU', 17, u'бюро'),
                ('MANOR', 18, u'цех'),
                ('SCENE', 19, u'сцена'),
                ('MEWS', 20, u'конюшни'),
                ('RANCH', 21, u'ранчо') )


class ATTRIBUTE(attributes.ATTRIBUTE):
    records = ( attributes.attr('SIZE', 0, u'размер города', default=lambda: 1, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                 description=u'Влияет на развитие специализаций, радиус влияния и на потребление товаров его жителями. Зависит от производства товаров.'),

                attributes.attr('TERRAIN_RADIUS', 2, u'радиус изменений', verbose_units=u'кл',
                 description=u'Радиус в котором город изменяет мир (в клетках).'),
                attributes.attr('POLITIC_RADIUS', 3, u'радиус владений', verbose_units=u'кл',
                 description=u'Максимальное расстояние, на которое могут распространяться границы владений города (в клетках).'),
                attributes.attr('PRODUCTION', 4, u'производство', formatter=int,
                 description=u'Скорость производства товаров. Зависит от размера экономики города и его Мастеров.'),
                attributes.attr('GOODS', 5, u'товары', type=attributes.ATTRIBUTE_TYPE.CALCULATED, formatter=int,
                 description=u'Чтобы расти, город должен производить товары. Если их накапливается достаточно, то размер города увеличивается. Если товары кончаются, то уменьшается.'),
                attributes.attr('KEEPERS_GOODS', 6, u'дары Хранителей', type=attributes.ATTRIBUTE_TYPE.CALCULATED, formatter=int,
                 description=u'Хранители могут подарить городу дополнительные товары, которые будут постепенно переводиться в производство (%2.f%% в час, но не менее %d). Чтобы сделать городу подарок, Вы можете использовать соответствующую Карту Судьбы.' % (c.PLACE_KEEPERS_GOODS_SPENDING*100, c.PLACE_GOODS_BONUS)),
                attributes.attr('SAFETY', 7, u'безопасность', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Насколько безопасно в окрестностях города (вероятность пройти по миру, не подвергнувшись нападению).'),
                attributes.attr('TRANSPORT', 8, u'транспорт', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Уровень развития транспортной инфраструктуры (с какой скоростью герои путешествуют в окрестностях города).'),
                attributes.attr('FREEDOM', 9, u'свобода', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Насколько активна политическая жизнь в городе (как сильно изменяется влияние Мастеров от действий героев).'),
                attributes.attr('TAX', 10, u'пошлина', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Размер пошлины, которую платят герои при посещении города (процент от наличности в кошельке героя).'),
                attributes.attr('STABILITY', 11, u'стабильность', order=0, verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Отражает текущую ситуацию в городе и влияет на многие его параметры. Уменьшается от изменений, происходящих в городе (при принятии законов), и постепенно восстанавливается до 100%.'),
                attributes.attr('STABILITY_RENEWING_SPEED', 12, u'восстановление стабильности', order=-1, verbose_units=u'% в час', formatter=attributes.percents_formatter,
                 description=u'Скорость восстановления стабильности в городе.'),
                attributes.attr('EXPERIENCE_BONUS', 13, u'бонус к опыту', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Бонус к количеству опыта за задания, связанные с этим городом.'),
                attributes.attr('BUY_PRICE', 14, u'цена покупки предметов', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Отклонение цены покупки экипировки в городе.'),
                attributes.attr('SELL_PRICE', 15, u'цена продажи предметов', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Отклонение цены продажи предметов в городе.'),
                attributes.attr('BUY_ARTIFACT_POWER', 16, u'сила покупаемых артефактов', order=0,
                 description=u'Сила артефактов, которые герой приобретает в городе.'),
                attributes.attr('ENERGY_REGEN_CHANCE', 19, u'восстановление энергии', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Шанс восстановить энергию при входе в город.'),
                attributes.attr('HERO_REGEN_CHANCE', 20, u'лечение героя', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Шанс героя полностью вылечиться при входе в город.'),
                attributes.attr('COMPANION_REGEN_CHANCE', 21, u'лечение спутника', verbose_units=u'%', formatter=attributes.percents_formatter,
                 description=u'Шанс спутника подлечиться при входе в город.'),
                attributes.attr('POWER_ECONOMIC', 22, u'экономика', default=lambda: 1, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                 description=u'Определяет скорость производства товаров городом. Зависит от общей суммы влияния, поступившего в город, в результате выполнения героями заданий за определённый период времени (примерное количество недель: %d). Влияние от задания может быть отрицательным. Чем больше суммарное влияние по сравнению с другими городами, тем больше размер экономики.' % c.PLACE_POWER_HISTORY_WEEKS),

                # modifiers MUST be calculated before stability
                attributes.attr('MODIFIER_TRADE_CENTER', 23, u'специализация «Торговый центр»', order=-1, formatter=attributes.float_formatter,
                 description=u'Соответствие города специализации «Торговый центр».'),
                attributes.attr('MODIFIER_CRAFT_CENTER', 24, u'специализация «Город мастеров»', order=-1, formatter=attributes.float_formatter,
                 description=u'Соответствие города специализации «Город мастеров».'),
                attributes.attr('MODIFIER_FORT', 25, u'специализация «Форт»', order=-1, formatter=attributes.float_formatter,
                 description=u'Соответствие города специализации «Форт».'),
                attributes.attr('MODIFIER_POLITICAL_CENTER', 26, u'специализация «Политический центр»', order=-1, formatter=attributes.float_formatter,
                 description=u'Соответствие города специализации «Политический центр».'),
                attributes.attr('MODIFIER_POLIC', 27, u'специализация «Полис»', order=-1, formatter=attributes.float_formatter,
                 description=u'Соответствие города специализации «Полис».'),
                attributes.attr('MODIFIER_RESORT', 28, u'специализация «Курорт»', order=-1, formatter=attributes.float_formatter,
                 description=u'Соответствие города специализации «Курорт».'),
                attributes.attr('MODIFIER_TRANSPORT_NODE', 29, u'специализация «Транспортный узел»', order=-1, formatter=attributes.float_formatter,
                 description=u'Соответствие города специализации «Транспортный узел».'),
                attributes.attr('MODIFIER_OUTLAWS', 30, u'специализация «Вольница»', order=-1, formatter=attributes.float_formatter,
                 description=u'Соответствие города специализации «Вольница».'),
                attributes.attr('MODIFIER_HOLY_CITY', 31, u'специализация «Святой город»', order=-1, formatter=attributes.float_formatter,
                 description=u'Соответствие города специализации «Святой город».'),

                attributes.attr('MODIFIER_MULTIPLIER', 32, u'сила специализаций', order=-1, default=lambda: 1, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                 description=u'Влияние города на соответствие специализациям.', formatter=attributes.float_formatter)  )


    EFFECTS_ORDER = sorted(set(record[5] for record in records))


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
