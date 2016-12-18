# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.balance import constants as c

from the_tale.game import attributes


class BUILDING_STATE(DjangoEnum):
    records = ( ('WORKING', 0, 'работает'),
                ('DESTROYED', 1, 'уничтожено') )


class BUILDING_TYPE(DjangoEnum):
    records = ( ('SMITHY', 0, 'кузница'),
                ('FISHING_LODGE', 1, 'домик рыболова'),
                ('TAILOR_SHOP', 2, 'мастерская портного'),
                ('SAWMILL', 3, 'лесопилка'),
                ('HUNTER_HOUSE', 4, 'домик охотника'),
                ('WATCHTOWER', 5, 'сторожевая башня'),
                ('TRADING_POST', 6, 'торговый пост'),
                ('INN', 7, 'трактир'),
                ('DEN_OF_THIEVE', 8, 'логово вора'),
                ('FARM', 9, 'ферма'),
                ('MINE', 10, 'шахта'),
                ('TEMPLE', 11, 'храм'),
                ('HOSPITAL', 12, 'больница'),
                ('LABORATORY', 13, 'лаборатория'),
                ('SCAFFOLD', 14, 'плаха'),
                ('MAGE_TOWER', 15, 'башня мага'),
                ('GUILDHALL', 16, 'ломбард'),
                ('BUREAU', 17, 'бюро'),
                ('MANOR', 18, 'цех'),
                ('SCENE', 19, 'сцена'),
                ('MEWS', 20, 'конюшни'),
                ('RANCH', 21, 'ранчо') )


class ATTRIBUTE(attributes.ATTRIBUTE):
    records = ( attributes.attr('SIZE', 0, 'размер города', default=lambda: 1, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                 description='Влияет на развитие специализаций, радиус влияния и на потребление товаров его жителями. Зависит от производства товаров.'),

                attributes.attr('TERRAIN_RADIUS', 2, 'радиус изменений', verbose_units='кл', order=2, formatter=attributes.float_formatter,
                 description='Радиус в котором город изменяет мир (в клетках).'),
                attributes.attr('POLITIC_RADIUS', 3, 'радиус владений', verbose_units='кл', order=2, formatter=attributes.float_formatter,
                 description='Максимальное расстояние, на которое могут распространяться границы владений города (в клетках).'),
                attributes.attr('PRODUCTION', 4, 'производство', formatter=int,
                 description='Скорость производства товаров. Зависит от размера экономики города и его Мастеров.'),
                attributes.attr('GOODS', 5, 'товары', type=attributes.ATTRIBUTE_TYPE.CALCULATED, formatter=int,
                 description='Чтобы расти, город должен производить товары. Если их накапливается достаточно, то размер города увеличивается. Если товары кончаются, то уменьшается.'),
                attributes.attr('KEEPERS_GOODS', 6, 'дары Хранителей', type=attributes.ATTRIBUTE_TYPE.CALCULATED, formatter=int,
                 description='Хранители могут подарить городу дополнительные товары, которые будут постепенно переводиться в производство (%2.f%% в час, но не менее %d). Чтобы сделать городу подарок, Вы можете использовать соответствующую Карту Судьбы.' % (c.PLACE_KEEPERS_GOODS_SPENDING*100, c.PLACE_GOODS_BONUS)),
                attributes.attr('SAFETY', 7, 'безопасность', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Насколько безопасно в окрестностях города (вероятность пройти по миру, не подвергнувшись нападению).'),
                attributes.attr('TRANSPORT', 8, 'транспорт', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Уровень развития транспортной инфраструктуры (с какой скоростью герои путешествуют в окрестностях города).'),
                attributes.attr('FREEDOM', 9, 'свобода', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Насколько активна политическая жизнь в городе (как сильно изменяется влияние Мастеров от действий героев).'),
                attributes.attr('TAX', 10, 'пошлина', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Размер пошлины, которую платят герои при посещении города (процент от наличности в кошельке героя).'),
                attributes.attr('STABILITY', 11, 'стабильность', order=0, verbose_units='%', formatter=attributes.percents_formatter,
                 description='Отражает текущую ситуацию в городе и влияет на многие его параметры. Уменьшается от изменений, происходящих в городе (при принятии законов), и постепенно восстанавливается до 100%.'),
                attributes.attr('STABILITY_RENEWING_SPEED', 12, 'восстановление стабильности', order=-1, verbose_units='% в час', formatter=attributes.percents_formatter,
                 description='Скорость восстановления стабильности в городе.'),
                attributes.attr('EXPERIENCE_BONUS', 13, 'бонус к опыту', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Бонус к количеству опыта за задания, связанные с этим городом.'),
                attributes.attr('BUY_PRICE', 14, 'цена покупки предметов', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Отклонение цены покупки экипировки в городе.'),
                attributes.attr('SELL_PRICE', 15, 'цена продажи предметов', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Отклонение цены продажи предметов в городе.'),
                attributes.attr('BUY_ARTIFACT_POWER', 16, 'сила покупаемых артефактов', order=0,
                 description='Сила артефактов, которые герой приобретает в городе.'),
                attributes.attr('ENERGY_REGEN_CHANCE', 19, 'восстановление энергии', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Шанс восстановить энергию при входе в город.'),
                attributes.attr('HERO_REGEN_CHANCE', 20, 'лечение героя', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Шанс героя полностью вылечиться при входе в город.'),
                attributes.attr('COMPANION_REGEN_CHANCE', 21, 'лечение спутника', verbose_units='%', formatter=attributes.percents_formatter,
                 description='Шанс спутника подлечиться при входе в город.'),
                attributes.attr('POWER_ECONOMIC', 22, 'экономика', default=lambda: 1, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                 description='Определяет скорость производства товаров городом. Зависит от общей суммы влияния, поступившего в город, в результате выполнения героями заданий за определённый период времени (примерное количество недель: %d). Влияние от задания может быть отрицательным. Чем больше суммарное влияние по сравнению с другими городами, тем больше размер экономики.' % c.PLACE_POWER_HISTORY_WEEKS),

                # modifiers MUST be calculated before stability
                attributes.attr('MODIFIER_TRADE_CENTER', 23, 'специализация «Торговый центр»', order=-1, formatter=attributes.float_formatter,
                 description='Соответствие города специализации «Торговый центр».'),
                attributes.attr('MODIFIER_CRAFT_CENTER', 24, 'специализация «Город мастеров»', order=-1, formatter=attributes.float_formatter,
                 description='Соответствие города специализации «Город мастеров».'),
                attributes.attr('MODIFIER_FORT', 25, 'специализация «Форт»', order=-1, formatter=attributes.float_formatter,
                 description='Соответствие города специализации «Форт».'),
                attributes.attr('MODIFIER_POLITICAL_CENTER', 26, 'специализация «Политический центр»', order=-1, formatter=attributes.float_formatter,
                 description='Соответствие города специализации «Политический центр».'),
                attributes.attr('MODIFIER_POLIC', 27, 'специализация «Полис»', order=-1, formatter=attributes.float_formatter,
                 description='Соответствие города специализации «Полис».'),
                attributes.attr('MODIFIER_RESORT', 28, 'специализация «Курорт»', order=-1, formatter=attributes.float_formatter,
                 description='Соответствие города специализации «Курорт».'),
                attributes.attr('MODIFIER_TRANSPORT_NODE', 29, 'специализация «Транспортный узел»', order=-1, formatter=attributes.float_formatter,
                 description='Соответствие города специализации «Транспортный узел».'),
                attributes.attr('MODIFIER_OUTLAWS', 30, 'специализация «Вольница»', order=-1, formatter=attributes.float_formatter,
                 description='Соответствие города специализации «Вольница».'),
                attributes.attr('MODIFIER_HOLY_CITY', 31, 'специализация «Святой город»', order=-1, formatter=attributes.float_formatter,
                 description='Соответствие города специализации «Святой город».'),

                attributes.attr('MODIFIER_MULTIPLIER', 32, 'сила специализаций', order=-1, default=lambda: 1, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                 description='Влияние города на соответствие специализациям.', formatter=attributes.float_formatter),

                attributes.attr('CULTURE', 33, 'культура', verbose_units='%', formatter=attributes.percents_formatter,
                 description='На сколько развита культура города, влияет на радиусы влияния и изменения ландшафта.')       )


    EFFECTS_ORDER = sorted(set(record[5] for record in records))


class RESOURCE_EXCHANGE_TYPE(DjangoEnum):
    parameter = Column(unique=False, primary=False, single_type=False)
    amount = Column(unique=False, primary=False, single_type=False)
    direction = Column(unique=False, primary=False)

    PRODUCTION_BASE = int(c.PLACE_GOODS_BONUS / 2)
    SAFETY_BASE = c.PLACE_SAFETY_FROM_BEST_PERSON / 4
    TRANSPORT_BASE = c.PLACE_TRANSPORT_FROM_BEST_PERSON / 4
    TAX_BASE = 0.025

    records = ( ('NONE',  0, 'ничего', None, 0, 0),

                ('PRODUCTION_SMALL',  1, '%d продукции' % PRODUCTION_BASE, ATTRIBUTE.PRODUCTION, PRODUCTION_BASE, 1),
                ('PRODUCTION_NORMAL', 2, '%d продукции' % (PRODUCTION_BASE * 2), ATTRIBUTE.PRODUCTION, PRODUCTION_BASE * 2, 1),
                ('PRODUCTION_LARGE',  3, '%d продукции' % (PRODUCTION_BASE * 4), ATTRIBUTE.PRODUCTION, PRODUCTION_BASE * 4, 1),

                ('SAFETY_SMALL',      4, '%.2f%% безопасности' % float(SAFETY_BASE * 100), ATTRIBUTE.SAFETY, SAFETY_BASE, 1),
                ('SAFETY_NORMAL',     5, '%.2f%% безопасности' % float(SAFETY_BASE * 2 * 100), ATTRIBUTE.SAFETY, SAFETY_BASE * 2, 1),
                ('SAFETY_LARGE',      6, '%.2f%% безопасности' % float(SAFETY_BASE * 4 * 100), ATTRIBUTE.SAFETY, SAFETY_BASE * 4, 1),

                ('TRANSPORT_SMALL',   7, '%.2f%% транспорта' % float(TRANSPORT_BASE * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE, 1),
                ('TRANSPORT_NORMAL',  8, '%.2f%% транспорта' % float(TRANSPORT_BASE * 2 * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE * 2, 1),
                ('TRANSPORT_LARGE',   9, '%.2f%% транспорта' % float(TRANSPORT_BASE * 4 * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE * 4, 1),

                ('TAX_SMALL',   10, '%.2f%% пошлины' % float(TAX_BASE * 100), ATTRIBUTE.TAX, TAX_BASE, -1),
                ('TAX_NORMAL',  11, '%.2f%% пошлины' % float(TAX_BASE * 2 * 100), ATTRIBUTE.TAX, TAX_BASE * 2, -1),
                ('TAX_LARGE',   12, '%.2f%% пошлины' % float(TAX_BASE * 4 * 100), ATTRIBUTE.TAX, TAX_BASE * 4, -1) )
