
import smart_imports

smart_imports.all()


def _modifier_linguistics_restrictions(modifier):
    def _linguistics_restrictions():
        from the_tale.linguistics import restrictions as linguistics_restrictions
        return (linguistics_restrictions.get(getattr(CITY_MODIFIERS, modifier)), )

    return _linguistics_restrictions


def record(name, value, text, quest, modifier_effects, description):
    return (name,
            value,
            text,
            quest,
            getattr(technical_words, 'MODIFIER_{}'.format(name)),
            _modifier_linguistics_restrictions(name),
            tuple([tt_api_effects.Effect(name=text,
                                         attribute=getattr(relations.ATTRIBUTE, attribute),
                                         value=value)
                   for attribute, value in modifier_effects]),
            description,
            getattr(relations.ATTRIBUTE, 'MODIFIER_{}'.format(name)) if name != 'NONE' else None)


class CITY_MODIFIERS(rels_django.DjangoEnum):
    quest_type = rels.Column(unique=False)
    utg_name_form = rels.Column()
    linguistics_restrictions = rels.Column()
    effects = rels.Column(no_index=True, unique=False)
    description = rels.Column()
    points_attribute = rels.Column(unique=False, single_type=False)

    records = (record('TRADE_CENTER', 0, 'Торговый центр', questgen_relations.PLACE_TYPE.NONE,
                      (('SELL_PRICE', 0.15), ('BUY_PRICE', -0.15), ('PRODUCTION', c.PLACE_GOODS_BONUS / 2), ('FREEDOM', 0.1)),
                      'В городе идёт оживлённая торговля, поэтому герои всегда могут найти выгодную цену для продажи своих трофеев или покупки артефактов. Увеличивается производство и уровень свободы в городе.'),

               record('CRAFT_CENTER', 1, 'Город ремёсел', questgen_relations.PLACE_TYPE.NONE,
                      (('PRODUCTION', c.PLACE_GOODS_BONUS),),
                      'Большое количество мастеров, трудящихся в городе, увеличивает уровень производства.'),

               record('FORT', 2, 'Форт', questgen_relations.PLACE_TYPE.NONE,
                      (('SAFETY', 0.05),),
                      'Постоянное присутствие военных делает окрестности города безопаснее для путешествий.'),

               record('POLITICAL_CENTER', 3, 'Политический центр', questgen_relations.PLACE_TYPE.NONE,
                      (('STABILITY_RENEWING_SPEED', c.PLACE_STABILITY_RECOVER_SPEED), ('POLITIC_RADIUS', 3), ('FREEDOM', 0.25)),
                      'Активная политическая жизнь приводит к тому, что в городе увеличивается уровень свободы. Также увеличивается радиус влияния города и ускоряется восстановление стабильности.'),

               record('POLIC', 4, 'Полис', questgen_relations.PLACE_TYPE.NONE,
                      (('PRODUCTION', c.PLACE_GOODS_BONUS), ('TERRAIN_RADIUS', 3), ('FREEDOM', 0.1)),
                      'Самостоятельная политика города вместе с большими свободами граждан способствуют увеличению производства и уровня свободы в городе. Кроме того увеличивается радиус, в котором город влияет на изменение ландшафта.'),

               record('RESORT', 5, 'Курорт', questgen_relations.PLACE_TYPE.NONE,
                      (('HERO_REGEN_CHANCE', 1.0), ('COMPANION_REGEN_CHANCE', 1.0), ('SAFETY', 0.02), ('FREEDOM', 0.1)),
                      'Город прославлен своими здравницами и особой атмосферой, в которой раны затягиваются особенно быстро. При посещении города герои полностью восстанавливают своё здоровье. Спутники также восстанавливают немного здоровья. Увеличивается уровень безопасности города и уровень свободы.'),

               record('TRANSPORT_NODE', 6, 'Транспортный узел', questgen_relations.PLACE_TYPE.NONE,
                      (('TRANSPORT', 0.2),),
                      'Хорошие дороги и обилие гостиниц делают путешествие по дорогам в окрестностях города быстрым и комфортным. Увеличивается уровень транспорта в городе.'),

               record('OUTLAWS', 7, 'Вольница', questgen_relations.PLACE_TYPE.NONE,
                      (('EXPERIENCE_BONUS', 0.25), ('FREEDOM', 0.35), ('SAFETY', -0.1)),
                      'Город облюбован всевозможными авантюристами, бунтарями, беглыми преступниками, бастардами и просто свободолюбивыми людьми, которые готовы любыми средствами защищать свою свободу и свой уклад. Любое задание, связанное с этим городом, принесёт дополнительный опыт герою. Также в городе увеличен уровень свободы и уменьшен уровень безопасности.'),

               record('HOLY_CITY', 8, 'Святой город', questgen_relations.PLACE_TYPE.HOLY_CITY,
                      (('ENERGY_REGEN_CHANCE', 1.0), ('PRODUCTION', -c.PLACE_GOODS_BONUS / 2), ('TRANSPORT', 0.1), ('FREEDOM', -0.25)),
                      'Город является средоточием религиозной жизни Пандоры. У каждого героя рано или поздно появляется желание посетить это святое место, чтобы дать отдых своему духу. Обилие паломников способствует развитию транспортной системы города, но излишняя религиозность жителей отрицательно сказывается на производстве и свободе. Сильная энергетика города позволяет Хранителям восстанавливать немного энергии, когда их герои посещают город.'),

               record('NONE', 9, 'Обычный город', questgen_relations.PLACE_TYPE.NONE,
                      (),
                      'Город без особых свойств.'))
