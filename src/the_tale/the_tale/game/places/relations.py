
import smart_imports

smart_imports.all()


class BUILDING_STATE(rels_django.DjangoEnum):
    records = (('WORKING', 0, 'работает'),
               ('DESTROYED', 1, 'уничтожено'))


class BUILDING_TYPE(rels_django.DjangoEnum):
    records = (('SMITHY', 0, 'кузница'),
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
               ('RANCH', 21, 'ранчо'))


attributes = game_attributes


class ATTRIBUTE(game_attributes.ATTRIBUTE):
    records = (attributes.attr('SIZE', 0, 'размер города', default=lambda: 1, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                               description='Влияет на развитие специализаций, радиус влияния и на потребление товаров его жителями. Зависит от производства товаров.'),

               attributes.attr('TERRAIN_RADIUS', 2, 'радиус изменений', verbose_units='кл', order=2, formatter=attributes.float_formatter,
                               description='Радиус в котором город изменяет мир (в клетках).'),
               attributes.attr('POLITIC_RADIUS', 3, 'радиус владений', verbose_units='кл', order=2, formatter=attributes.float_formatter,
                               description='Максимальное расстояние, на которое могут распространяться границы владений города (в клетках).'),
               attributes.attr('PRODUCTION', 4, 'производство', formatter=int, order=3,  # после POLITIC_RADIUS
                               description='Скорость производства товаров. Зависит от размера экономики города, площади владений, Мастеров и многих других эффектов. Если производство станет меньше нуля при отсутствии товаров на складах города и его единичном размере, то в городе начнётся производственный кризис. Для разрешения кризиса будет введена пошлина для всех проходящих героев.'),
               attributes.attr('GOODS', 5, 'товары', type=attributes.ATTRIBUTE_TYPE.CALCULATED, formatter=int,
                               description='Чтобы расти, город должен производить товары. Если их накапливается достаточно, то размер города увеличивается. Если товары кончаются, то уменьшается.'),
               attributes.attr('SAFETY', 7, 'безопасность', verbose_units='%', formatter=attributes.percents_formatter,
                               description='Вклад города в безопасность в его окрестностях.'),
               attributes.attr('TRANSPORT', 8, 'транспорт', verbose_units='%', formatter=attributes.percents_formatter,
                               description='Вклад города в развитие транспортной инфраструктуры в его окрестностях.'),
               attributes.attr('FREEDOM', 9, 'свобода', verbose_units='%', formatter=attributes.percents_formatter,
                               description='Насколько активна политическая жизнь в городе (как сильно изменяется влияние Мастеров от действий героев).'),
               attributes.attr('TAX', 10, 'пошлина', verbose_units='%', formatter=attributes.percents_formatter, order=3,
                               description='Размер пошлины, которую платят герои при посещении города (процент от наличности в кошельке героя).'),
               attributes.attr('STABILITY', 11, 'стабильность', order=0, verbose_units='%', formatter=attributes.percents_formatter,
                               description='Отражает текущую ситуацию в городе и влияет на многие его параметры. Уменьшается от изменений, происходящих в городе (например, при одобрении записи в Книге Судеб).'),
               attributes.attr('STABILITY_RENEWING_SPEED', 12, 'восстановление стабильности', order=-1, verbose_units='% в час', formatter=attributes.percents_formatter,
                               description='Скорость уменьшения штрафов к стабильности, вызванных созданием записей в Книге Судеб.'),
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
                               description='Влияет на скорость производства товаров в городе. Зависит от общей суммы влияния, поступившего в город, в результате выполнения героями заданий за определённый период времени (примерное количество недель: %d). Влияние от задания может быть отрицательным. Чем больше суммарное влияние по сравнению с другими городами, тем больше размер экономики. Расчитывается отдельно для городов Фронтира и центра.' % c.PLACE_POWER_HISTORY_WEEKS),

               # modifiers MUST be calculated before stability
               attributes.attr('MODIFIER_TRADE_CENTER', 23, 'специализация «Торговый центр»', order=-2, formatter=attributes.float_formatter,
                               description='Соответствие города специализации «Торговый центр».'),
               attributes.attr('MODIFIER_CRAFT_CENTER', 24, 'специализация «Город ремёсел»', order=-2, formatter=attributes.float_formatter,
                               description='Соответствие города специализации «Город мастеров».'),
               attributes.attr('MODIFIER_FORT', 25, 'специализация «Форт»', order=-2, formatter=attributes.float_formatter,
                               description='Соответствие города специализации «Форт».'),
               attributes.attr('MODIFIER_POLITICAL_CENTER', 26, 'специализация «Политический центр»', order=-2, formatter=attributes.float_formatter,
                               description='Соответствие города специализации «Политический центр».'),
               attributes.attr('MODIFIER_POLIC', 27, 'специализация «Полис»', order=-2, formatter=attributes.float_formatter,
                               description='Соответствие города специализации «Полис».'),
               attributes.attr('MODIFIER_RESORT', 28, 'специализация «Курорт»', order=-2, formatter=attributes.float_formatter,
                               description='Соответствие города специализации «Курорт».'),
               attributes.attr('MODIFIER_TRANSPORT_NODE', 29, 'специализация «Транспортный узел»', order=-2, formatter=attributes.float_formatter,
                               description='Соответствие города специализации «Транспортный узел».'),
               attributes.attr('MODIFIER_OUTLAWS', 30, 'специализация «Вольница»', order=-2, formatter=attributes.float_formatter,
                               description='Соответствие города специализации «Вольница».'),
               attributes.attr('MODIFIER_HOLY_CITY', 31, 'специализация «Святой город»', order=-2, formatter=attributes.float_formatter,
                               description='Соответствие города специализации «Святой город».'),

               attributes.attr('MODIFIER_MULTIPLIER', 32, 'сила специализаций', order=-2, default=lambda: 1, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                               description='Влияние города на соответствие специализациям.', formatter=attributes.float_formatter),

               attributes.attr('CULTURE', 33, 'культура', verbose_units='%', formatter=attributes.percents_formatter,
                               description='Насколько развита культура города, влияет на радиусы влияния и изменения ландшафта.'),

               attributes.attr('AREA', 34, 'площадь владений', order=0, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                               description='Площадь владений города. Чем больше у города владений, тем больше производство в нём. На Фронтире бонус к производству меньше.'),
               attributes.attr('MONEY_ECONOMIC', 35, 'торговля', default=lambda: 1, type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                               description='Влияет на скорость производства товаров в городе. Зависит от общего количества потраченных и полученных героями денег в городе за определённый период времени (примерное количество недель: %d). Чем больше сумма по сравнению с другими городами, тем больше размер торговли. Расчитывается отдельно для городов Фронтира и центра.' % c.PLACE_POWER_HISTORY_WEEKS),

               attributes.attr('TASK_BOARD', 36, 'доска заданий',
                               default=set, serializer=list, deserializer=set, apply=game_attributes.set_applier,
                               formatter=lambda attribute: 'кланов: {}'.format(len(attribute)),
                               description='Перечень гильдий, герои которых не бездельничают в городе. Управляется мероприятиями эмиссаров.'),
               attributes.attr('FAST_TRANSPORTATION', 37, 'служба сопровождения',
                               default=set, serializer=list, deserializer=set, apply=game_attributes.set_applier,
                               formatter=lambda attribute: 'кланов: {}'.format(len(attribute)),
                               description='Перечень гильдий, которые предоставляют своим героям услуги сопровождения в путешествиях.'),

               attributes.attr('COMPANIONS_SUPPORT', 38, 'поддержка спутников',
                               default=set, serializer=list, deserializer=set, apply=game_attributes.set_applier,
                               formatter=lambda attribute: 'кланов: {}'.format(len(attribute)),
                               description='Перечень гильдий, которые предоставляют лечение спутникам своих героев.'),

               attributes.attr('DEMOGRAPHICS_PRESSURE_HUMAN', 39, 'бонус демографического давления людей',
                               formatter=attributes.percents_formatter, verbose_units='%',
                               description='Модификация демографического давления мастеров людей.'),
               attributes.attr('DEMOGRAPHICS_PRESSURE_ELF', 40, 'бонус демографического давления эльфов',
                               formatter=attributes.percents_formatter, verbose_units='%',
                               description='Модификация демографического давления мастеров эльфов.'),
               attributes.attr('DEMOGRAPHICS_PRESSURE_ORC', 41, 'бонус демографического давления орков',
                               formatter=attributes.percents_formatter, verbose_units='%',
                               description='Модификация демографического давления мастеров орков.'),
               attributes.attr('DEMOGRAPHICS_PRESSURE_GOBLIN', 42, 'бонус демографического давления гоблинов',
                               formatter=attributes.percents_formatter, verbose_units='%',
                               description='Модификация демографического давления мастеров гоблинов.'),
               attributes.attr('DEMOGRAPHICS_PRESSURE_DWARF', 43, 'бонус демографического давления дварфов',
                               formatter=attributes.percents_formatter, verbose_units='%',
                               description='Модификация демографического давления мастеров дварфов.'),

               attributes.attr('TAX_SIZE_BORDER', 44, 'поддерживаемый размер', default=lambda: 1,
                               type=attributes.ATTRIBUTE_TYPE.CALCULATED,
                               description=f'Если есть риск уменьшения размера города ниже этого значения, город автоматически введёт пошлину, чтобы компенсировать недостаток производства. В городах размером больше 1, пошлина может компенсировать не более {c.MAX_PRODUCTION_FROM_TAX} производства.'),

               attributes.attr('CLAN_PROTECTOR', 45, 'гильдия-протектор', default=lambda: None,
                               apply=game_attributes.replace_applier, type=game_attributes.ATTRIBUTE_TYPE.REWRITABLE,
                               formatter=game_attributes.clan_formatter,
                               description='Гильдия, протекторатом которого является город. Мероприятяи эмиссаров гильдии-протектора, проводимые в городе, получают дополнительные и/или усиленные эффекты.'))


ATTRIBUTE.EFFECTS_ORDER = sorted(set(record.order for record in ATTRIBUTE.records))


class RESOURCE_EXCHANGE_TYPE(rels_django.DjangoEnum):
    parameter = rels.Column(unique=False, primary=False, single_type=False)
    amount = rels.Column(unique=False, primary=False, single_type=False)
    direction = rels.Column(unique=False, primary=False)

    PRODUCTION_BASE = int(c.PLACE_GOODS_BONUS / 2)
    SAFETY_BASE = c.PLACE_SAFETY_FROM_BEST_PERSON / 4
    TRANSPORT_BASE = c.PLACE_TRANSPORT_FROM_BEST_PERSON / 4
    TAX_BASE = PRODUCTION_BASE * c.PLACE_TAX_PER_ONE_GOODS
    CULTURE_BASE = c.PLACE_CULTURE_FROM_BEST_PERSON / 4

    records = (('NONE', 0, 'ничего', None, 0, 0),

               ('PRODUCTION_SMALL', 1, '%d продукции' % PRODUCTION_BASE, ATTRIBUTE.PRODUCTION, PRODUCTION_BASE, 1),
               ('PRODUCTION_NORMAL', 2, '%d продукции' % (PRODUCTION_BASE * 2), ATTRIBUTE.PRODUCTION, PRODUCTION_BASE * 2, 1),
               ('PRODUCTION_LARGE', 13, '%d продукции' % (PRODUCTION_BASE * 3), ATTRIBUTE.PRODUCTION, PRODUCTION_BASE * 3, 1),
               ('PRODUCTION_EXTRA_LARGE', 3, '%d продукции' % (PRODUCTION_BASE * 4), ATTRIBUTE.PRODUCTION, PRODUCTION_BASE * 4, 1),

               ('SAFETY_SMALL', 4, '%.2f%% безопасности' % float(SAFETY_BASE * 100), ATTRIBUTE.SAFETY, SAFETY_BASE, 1),
               ('SAFETY_NORMAL', 5, '%.2f%% безопасности' % float(SAFETY_BASE * 2 * 100), ATTRIBUTE.SAFETY, SAFETY_BASE * 2, 1),
               ('SAFETY_LARGE', 14, '%.2f%% безопасности' % float(SAFETY_BASE * 3 * 100), ATTRIBUTE.SAFETY, SAFETY_BASE * 3, 1),
               ('SAFETY_EXTRA_LARGE', 6, '%.2f%% безопасности' % float(SAFETY_BASE * 4 * 100), ATTRIBUTE.SAFETY, SAFETY_BASE * 4, 1),

               ('TRANSPORT_SMALL', 7, '%.2f%% транспорта' % float(TRANSPORT_BASE * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE, 1),
               ('TRANSPORT_NORMAL', 8, '%.2f%% транспорта' % float(TRANSPORT_BASE * 2 * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE * 2, 1),
               ('TRANSPORT_LARGE', 15, '%.2f%% транспорта' % float(TRANSPORT_BASE * 3 * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE * 3, 1),
               ('TRANSPORT_EXTRA_LARGE', 9, '%.2f%% транспорта' % float(TRANSPORT_BASE * 4 * 100), ATTRIBUTE.TRANSPORT, TRANSPORT_BASE * 4, 1),

               ('TAX_SMALL', 10, '%.2f%% пошлины' % float(TAX_BASE * 100), ATTRIBUTE.TAX, TAX_BASE, -1),
               ('TAX_NORMAL', 11, '%.2f%% пошлины' % float(TAX_BASE * 2 * 100), ATTRIBUTE.TAX, TAX_BASE * 2, -1),
               ('TAX_LARGE', 16, '%.2f%% пошлины' % float(TAX_BASE * 3 * 100), ATTRIBUTE.TAX, TAX_BASE * 3, -1),
               ('TAX_EXTRA_LARGE', 12, '%.2f%% пошлины' % float(TAX_BASE * 4 * 100), ATTRIBUTE.TAX, TAX_BASE * 4, -1),

               ('CULTURE_SMALL', 17, '%.2f%% культуры' % float(CULTURE_BASE * 100), ATTRIBUTE.CULTURE, CULTURE_BASE, 1),
               ('CULTURE_NORMAL', 18, '%.2f%% культуры' % float(CULTURE_BASE * 2 * 100), ATTRIBUTE.CULTURE, CULTURE_BASE * 2, 1),
               ('CULTURE_LARGE', 19, '%.2f%% культуры' % float(CULTURE_BASE * 3 * 100), ATTRIBUTE.CULTURE, CULTURE_BASE * 3, 1),
               ('CULTURE_EXTRA_LARGE', 20, '%.2f%% культуры' % float(CULTURE_BASE * 4 * 100), ATTRIBUTE.CULTURE, CULTURE_BASE * 4, 1), )
