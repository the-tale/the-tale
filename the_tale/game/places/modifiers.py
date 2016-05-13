# coding: utf-8
from rels import Column
from rels.django import DjangoEnum

from questgen.relations import PLACE_TYPE as QUEST_PLACE_TYPE

from the_tale.game.balance import constants as c
from the_tale.game import effects

from . import relations
from . import technical_words


def _modifier_linguistics_restrictions(modifier):
    def _linguistics_restrictions():
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage
        return (restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.CITY_MODIFIER, CITY_MODIFIERS.index_name[modifier].value).id, )
    return _linguistics_restrictions


def record(name, value, text, quest, modifier_effects, description):
    return (name,
            value,
            text,
            quest,
            getattr(technical_words, 'MODIFIER_{}'.format(name)),
            _modifier_linguistics_restrictions(name),
            tuple([effects.Effect(name=text, attribute=getattr(relations.ATTRIBUTE, attribute), value=value) for attribute, value in modifier_effects]),
            description,
            relations.ATTRIBUTE.index_name['MODIFIER_{}'.format(name)] if name != 'NONE' else None)


class CITY_MODIFIERS(DjangoEnum):
    quest_type = Column(unique=False)
    utg_name_form = Column()
    linguistics_restrictions = Column()
    effects = Column()
    description = Column()
    points_attribute = Column(unique=False, single_type=False)

    records = ( record('TRADE_CENTER', 0, u'Торговый центр', QUEST_PLACE_TYPE.NONE,
                       (('SELL_PRICE', 0.15), ('BUY_PRICE', -0.15), ('PRODUCTION', c.PLACE_GOODS_BONUS / 2), ('FREEDOM', 0.1)),
                       u'В городе идёт оживлённая торговля, поэтому герои всегда могут найти выгодную цену для продажи своих трофеев или покупки артефактов. Увеличивается производство и уровень свободы в городе.'),

                record('CRAFT_CENTER', 1, u'Город мастеров', QUEST_PLACE_TYPE.NONE,
                       (('BUY_ARTIFACT_POWER', 0.1), ('PRODUCTION', c.PLACE_GOODS_BONUS)),
                       u'Большое количество мастеров, трудящихся в городе, позволяет героям приобретать лучшие артефакты. Увеличивается уровень производства в городе.'),

                record('FORT', 2, u'Форт', QUEST_PLACE_TYPE.NONE,
                       (('SAFETY', 0.05),),
                       u'Постоянное присутствие военных делает окрестности города безопаснее для путешествий.'),

                record('POLITICAL_CENTER', 3, u'Политический центр', QUEST_PLACE_TYPE.NONE,
                       (('STABILITY_RENEWING_SPEED', c.PLACE_STABILITY_RECOVER_SPEED), ('POLITIC_RADIUS', 3), ('FREEDOM', 0.25)),
                       u'Активная политическая жизнь приводит к тому, что в городе увеличивается уровень свободы. Также увеличивается радиус влияния города и ускоряется восстановление стабильности.'),

                record('POLIC', 4, u'Полис', QUEST_PLACE_TYPE.NONE,
                       (('PRODUCTION', c.PLACE_GOODS_BONUS), ('TERRAIN_RADIUS', 3), ('FREEDOM', 0.1)),
                       u'Самостоятельная политика города вместе с большими свободами граждан способствуют увеличению производства и уровня свободы в городе. Кроме того увеличивается радиус, в котором город влияет на изменение ландшафта.'),

                record('RESORT', 5, u'Курорт', QUEST_PLACE_TYPE.NONE,
                       (('HERO_REGEN_CHANCE', 1.0), ('COMPANION_REGEN_CHANCE', 1.0), ('SAFETY', 0.02), ('FREEDOM', 0.1)),
                       u'Город прославлен своими здравницами и особой атмосферой, в которой раны затягиваются особенно быстро. При посещении города герои полностью восстанавливают своё здоровье. Спутники также восстанавливают немного здоровья. Увеличивается уровень безопасности города и уровень свободы.'),

                record('TRANSPORT_NODE', 6, u'Транспортный узел', QUEST_PLACE_TYPE.NONE,
                       (('TRANSPORT', 0.2),),
                       u'Хорошие дороги и обилие гостиниц делают путешествие по дорогам в окрестностях города быстрым и комфортным. Увеличивается уровень транспорта в городе.'),

                record('OUTLAWS', 7, u'Вольница', QUEST_PLACE_TYPE.NONE,
                       (('EXPERIENCE_BONUS', 0.25), ('FREEDOM', 0.35), ('SAFETY', -0.1)),
                       u'Город облюбован всевозможными авантюристами, бунтарями, беглыми преступниками, бастардами и просто свободолюбивыми людьми, которые готовы любыми средствами защищать свою свободу и свой уклад. Любое задание, связанное с этим городом, принесёт дополнительные опыт герою. Также в городе увеличен уровень свободы и уменьшен уровень безопасности.'),

                record('HOLY_CITY', 8, u'Святой город', QUEST_PLACE_TYPE.HOLY_CITY,
                       (('ENERGY_REGEN_CHANCE', 1.0), ('PRODUCTION', -c.PLACE_GOODS_BONUS / 2), ('TRANSPORT', 0.1), ('FREEDOM', -0.25)),
                       u'Город является средоточием религиозной жизни Пандоры. У каждого героя рано или поздно появляется желание посетить это святое место, чтобы дать отдых своему духу. Обилие паломников способствует развитию транспортной системы города, но излишняя религиозность жителей отрицательно сказывается на производстве и свободе. Сильная энергетика города позволяет Хранителям восстанавливать немного энергии, когда их герои посещают город.'),

                record('NONE', 9, u'Обычный город', QUEST_PLACE_TYPE.NONE,
                       (),
                       u'Город без особых свойств.') )
