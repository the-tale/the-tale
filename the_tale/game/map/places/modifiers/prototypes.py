# coding: utf-8

import math
import random

from game.balance import constants as c, enums as e


from common.utils.enum import create_enum

from game.persons.relations import PROFESSION_TO_CITY_MODIFIERS


EFFECT_SOURCES = create_enum('EFFECT_SOURCES', (('PERSON', 0, u'персонаж'),))

def _get_profession_effects(type_):
    return dict( (profession_id, modifiers[type_]) for profession_id, modifiers in PROFESSION_TO_CITY_MODIFIERS.items())

class PlaceModifierBase(object):

    NAME = None
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
        в городе 7-ого уровня 2 персонажа со способностями 0.7 и влиянием 0.35 каждый в сумме должны накапливать 75 очков
        2*7*0.35*0.7 ~ 3.43 с модификатором силы персонажа - 34.3 -> на 7-ом уровне можификатор от размера должен быть примерно 2.2
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

            effects.append((EFFECT_SOURCES.PERSON, '%s %s-%s' % (person.name, person.race_verbose, person.type.text), person_power_percent * person_effect))

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
    def can_buy_better_artifact(self): return False
    def modify_economic_size(self, size): return size
    def modify_terrain_change_power(self, power): return power
    def full_regen_allowed(self): return False
    def modify_experience(self, exp): return exp


class TradeCenter(PlaceModifierBase):

    TYPE = e.CITY_MODIFIERS.TRADE_CENTER
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.TRADE_CENTER)
    NAME = u'Торговый центр'
    DESCRIPTION = u'В городе идёт оживлённая торговля, поэтому герои всегда могут найти выгодную цену для продажи своих трофеев или покупки артефактов. Увеличивается производство и уровень свободы в городе.'

    PRODUCTION_MODIFIER = c.PLACE_GOODS_BONUS / 2
    FREEDOM_MODIFIER = 0.1

    def modify_sell_price(self, price): return price * 1.1
    def modify_buy_price(self, price): return price * 0.9


class CraftCenter(PlaceModifierBase):

    TYPE = e.CITY_MODIFIERS.CRAFT_CENTER
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.CRAFT_CENTER)
    NAME = u'Город мастеров'
    DESCRIPTION = u'Большое количество мастеров, трудящихся в городе, позволяет героям приобретать лучшие артефакты. Увеличивается уровень производства в гроде.'

    PRODUCTION_MODIFIER = c.PLACE_GOODS_BONUS

    def can_buy_better_artifact(self): return random.uniform(0, 1) < 0.1


class Fort(PlaceModifierBase):
    TYPE = e.CITY_MODIFIERS.FORT
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.FORT)
    NAME = u'Форт'
    DESCRIPTION = u'Постоянное присутствие военных делает окрестности города безопаснее для путешествий.'

    SAFETY_MODIFIER = 0.05


class PoliticalCenter(PlaceModifierBase):

    TYPE = e.CITY_MODIFIERS.POLITICAL_CENTER
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.POLITICAL_CENTER)
    NAME = u'Политический центр'
    DESCRIPTION = u'Активная политическая жизнь приводит к тому, что усиливаются все изменения влияния (и положительные и отрицательные) — увеличивается уровень свободы в городе.'

    FREEDOM_MODIFIER = 0.25


class Polic(PlaceModifierBase):
    TYPE = e.CITY_MODIFIERS.POLIC
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.POLIC)
    NAME = u'Полис'
    DESCRIPTION = u'Самостоятельная политика города вместе с большими свободами граждан способствует увеличению размера экономики и уровня свободы в городе.'

    FREEDOM_MODIFIER = 0.1

    def modify_economic_size(self, size): return size + 1
    def modify_terrain_change_power(self, power): return power * 1.2


class Resort(PlaceModifierBase):

    TYPE = e.CITY_MODIFIERS.RESORT
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.RESORT)
    NAME = u'Курорт'
    DESCRIPTION = u'Город прославлен своими здравницами и особой атмосферой, в которой раны затягиваются особенно быстро. При посещении города герои полностью восстанавливают своё здоровье. Увеличивается уровень безопасности города и уровень свободы.'

    FREEDOM_MODIFIER = 0.1
    SAFETY_MODIFIER = 0.01

    def full_regen_allowed(self): return True


class TransportNode(PlaceModifierBase):
    TYPE = e.CITY_MODIFIERS.TRANSPORT_NODE
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.TRANSPORT_NODE)
    NAME = u'Транспортный узел'
    DESCRIPTION = u'Хорошие дороги и обилие гостиниц делает путешествие по дорогам в окрестностях города быстрым и комфортным. Увеличивается уровень транспорта в городе.'

    TRANSPORT_MODIFIER = 0.2


class Outlaws(PlaceModifierBase):
    TYPE = e.CITY_MODIFIERS.OUTLAWS
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.OUTLAWS)
    NAME = u'Вольница'
    DESCRIPTION = u'Город облюбован всевозможными авантюристами, бунтарями, беглыми преступниками, бастардами и просто свободолюбивыми людьми, которые готовы любыми средствами защищать свою свободу и свой уклад. Любое задание, связанное с этим городом, принесёт дополнительные опыт герою. Так же в городе увеличен уровень свободы и уменьшен уровень безопасности.'

    FREEDOM_MODIFIER = 0.35
    SAFETY_MODIFIER = -0.05
    EXPERIENCE_MODIFIER = 0.25



MODIFIERS = dict( (modifier.get_id(), modifier)
                  for modifier in globals().values()
                  if isinstance(modifier, type) and issubclass(modifier, PlaceModifierBase) and modifier != PlaceModifierBase)
