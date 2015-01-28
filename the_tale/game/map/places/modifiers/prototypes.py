# coding: utf-8

import math

from the_tale.common.utils.decorators import lazy_property

from the_tale.game.balance import constants as c


from the_tale.game.persons.relations import PROFESSION_TO_CITY_MODIFIERS

from the_tale.game.map.places.relations import CITY_MODIFIERS, EFFECT_SOURCES


class PlaceModifierBase(object):

    TYPE = None
    DESCRIPTION = None
    PERSON_EFFECTS = None
    PERSON_POWER_MODIFIER = 20

    SAFETY_MODIFIER = 0.0
    PRODUCTION_MODIFIER = 0.0
    TRANSPORT_MODIFIER = 0.0
    FREEDOM_MODIFIER = 0.0

    EXPERIENCE_MODIFIER = 0.0

    def __init__(self, place):
        self.place = place

    @lazy_property
    def NAME(self): return self.TYPE.text

    @lazy_property
    def PERSON_EFFECTS(self):
        return dict( (profession_id, modifiers[self.TYPE.value]) for profession_id, modifiers in PROFESSION_TO_CITY_MODIFIERS.items())

    @property
    def power_effects(self):
        if not hasattr(self, '_power_effects'):
            self._power_effects = sorted(self.get_power_effects(), key=lambda x: -x[2])
        return self._power_effects

    @property
    def power_effects_for_template(self):
        return [(name, power) for source, name, power in self.power_effects]

    @property
    def power(self):
        if not hasattr(self, '_power'):
            self._power = sum(effect[2] for effect in self.power_effects) * self.size_modifier
        return self._power

    @property
    def size_modifier(self):
        u'''
        методика расчёта:
        в городе 7-ого уровня 2 жителя со способностями 0.7 и влиянием 0.35 каждый в сумме должны накапливать 75 очков
        2*7*0.35*0.7 ~ 3.43 с модификатором силы жителя - 34.3 -> на 7-ом уровне можификатор от размера должен быть примерно 2.2
        '''
        return (math.log(self.place.size, 2) + 1) / 1.7

    @classmethod
    def get_id(cls): return cls.TYPE

    def get_power_effects(self):
        effects = []

        total_persons_power = self.place.total_persons_power

        for person in self.place.persons:
            person_power_percent = float(person.power) / (total_persons_power+1)

            person_effect = self.PERSON_POWER_MODIFIER * self.PERSON_EFFECTS[person.type.value] * person.mastery

            if  person_effect == 0: continue

            effects.append((EFFECT_SOURCES.PERSON, person.full_name, person_power_percent * person_effect))

        return effects

    @property
    def is_enough_power(self): return self.power >= c.PLACE_TYPE_ENOUGH_BORDER

    @property
    def can_be_choosen(self): return self.power >= c.PLACE_TYPE_NECESSARY_BORDER

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.place == other.place)

    def __ne__(self, other): return not self.__eq__(other)


    def modify_sell_price(self, price): return price
    def modify_buy_price(self, price): return price
    def modify_buy_better_artifact(self, probability): return probability
    def modify_economic_size(self, size): return size
    def modify_terrain_change_power(self, power): return power
    def modify_terrain_owning_radius(self, radius): return radius
    def modify_experience(self, exp): return exp
    def modify_stability_renewing_speed(self, stability): return stability

    def full_regen_allowed(self): return False
    def companion_regen_allowed(self): return False
    def energy_regen_allowed(self): return False



class TradeCenter(PlaceModifierBase):

    TYPE = CITY_MODIFIERS.TRADE_CENTER
    DESCRIPTION = u'В городе идёт оживлённая торговля, поэтому герои всегда могут найти выгодную цену для продажи своих трофеев или покупки артефактов. Увеличивается производство и уровень свободы в городе.'

    PRODUCTION_MODIFIER = c.PLACE_GOODS_BONUS / 2
    FREEDOM_MODIFIER = 0.1

    def modify_sell_price(self, price): return price * 1.1
    def modify_buy_price(self, price): return price * 0.9


class CraftCenter(PlaceModifierBase):

    TYPE = CITY_MODIFIERS.CRAFT_CENTER
    DESCRIPTION = u'Большое количество мастеров, трудящихся в городе, позволяет героям приобретать лучшие артефакты. Увеличивается уровень производства в городе.'

    PRODUCTION_MODIFIER = c.PLACE_GOODS_BONUS

    def modify_buy_better_artifact(self, probability): return probability * 1.1


class Fort(PlaceModifierBase):
    TYPE = CITY_MODIFIERS.FORT
    DESCRIPTION = u'Постоянное присутствие военных делает окрестности города безопаснее для путешествий.'

    SAFETY_MODIFIER = 0.05


class PoliticalCenter(PlaceModifierBase):

    TYPE = CITY_MODIFIERS.POLITICAL_CENTER
    DESCRIPTION = u'Активная политическая жизнь приводит к тому, что в городе увеличивается уровень свободы. Также увеличивается радиус влияния города и ускоряется восстановление стабильности.'

    FREEDOM_MODIFIER = 0.25

    def modify_terrain_owning_radius(self, radius): return radius * 1.25

    def modify_stability_renewing_speed(self, stability): return stability * 2


class Polic(PlaceModifierBase):
    TYPE = CITY_MODIFIERS.POLIC
    DESCRIPTION = u'Самостоятельная политика города вместе с большими свободами граждан способствуют увеличению размера экономики и уровня свободы в городе. Кроме того увеличивается радиус, в котором город влияет на изменение ландшафта.'

    FREEDOM_MODIFIER = 0.1

    def modify_economic_size(self, size): return size + 1
    def modify_terrain_change_power(self, power): return power * 1.2


class Resort(PlaceModifierBase):

    TYPE = CITY_MODIFIERS.RESORT
    DESCRIPTION = u'Город прославлен своими здравницами и особой атмосферой, в которой раны затягиваются особенно быстро. При посещении города герои полностью восстанавливают своё здоровье, их спутники восстанавливают 1 здоровья. Увеличивается уровень безопасности города и уровень свободы.'

    FREEDOM_MODIFIER = 0.1
    SAFETY_MODIFIER = 0.02

    def full_regen_allowed(self): return True
    def companion_regen_allowed(self): return True


class TransportNode(PlaceModifierBase):
    TYPE = CITY_MODIFIERS.TRANSPORT_NODE
    DESCRIPTION = u'Хорошие дороги и обилие гостиниц делают путешествие по дорогам в окрестностях города быстрым и комфортным. Увеличивается уровень транспорта в городе.'

    TRANSPORT_MODIFIER = 0.2


class Outlaws(PlaceModifierBase):
    TYPE = CITY_MODIFIERS.OUTLAWS
    DESCRIPTION = u'Город облюбован всевозможными авантюристами, бунтарями, беглыми преступниками, бастардами и просто свободолюбивыми людьми, которые готовы любыми средствами защищать свою свободу и свой уклад. Любое задание, связанное с этим городом, принесёт дополнительные опыт герою. Также в городе увеличен уровень свободы и уменьшен уровень безопасности.'

    FREEDOM_MODIFIER = 0.35
    SAFETY_MODIFIER = -0.1
    EXPERIENCE_MODIFIER = 0.25


class HolyCity(PlaceModifierBase):
    TYPE = CITY_MODIFIERS.HOLY_CITY
    DESCRIPTION = u'Город является средоточием религиозной жизни Пандоры. У каждого героя рано или поздно появляется желание посетить это святое место, чтобы дать отдых своему духу. Обилие паломников способствует развитию транспортной системы города, но излишняя религиозность жителей отрицательно сказывается на производстве и свободе. Сильная энергетика города позволяет Хранителям восстанавливать немного энергии, когда их герои посещают город.'

    PRODUCTION_MODIFIER = -c.PLACE_GOODS_BONUS / 2
    TRANSPORT_MODIFIER = 0.1
    FREEDOM_MODIFIER = -0.25

    def energy_regen_allowed(self): return True



MODIFIERS = dict( (modifier.get_id(), modifier)
                  for modifier in globals().values()
                  if isinstance(modifier, type) and issubclass(modifier, PlaceModifierBase) and modifier != PlaceModifierBase)
