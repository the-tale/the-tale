# coding: utf-8

import math
import random

from game.balance import constants as c, enums as e

# from game.map.places.modifiers.exceptions import PlaceModifierException

from common.utils.enum import create_enum

from game.map.places.conf import places_settings


EFFECT_SOURCES = create_enum('EFFECT_SOURCES', (('PERSON', 0, u'персонаж'),))

def _get_profession_effects(type_):
    return dict( (profession_id, modifiers[type_]) for profession_id, modifiers in c.PROFESSION_TO_CITY_MODIFIERS.items())

class PlaceModifierBase(object):

    NAME = None
    DESCRIPTION = None
    PERSON_EFFECTS = None
    PERSON_POWER_MODIFIER = 10

    def __init__(self, place):
        self.place = place

    @property
    def power_effects(self):
        if not hasattr(self, '_power_effects'):
            self._power_effects = sorted(self.get_power_effects(), key=lambda x: -x[2])
        return self._power_effects

    @property
    def power(self):
        if not hasattr(self, '_power'):
            self._power = sum(effect[2] for effect in self.power_effects) * self.size_modifier
        return self._power

    @property
    def size_modifier(self): return (math.log(self.place.size, 2) + 1) / 2.0

    @classmethod
    def get_id(cls): return cls.TYPE

    def get_power_effects(self):
        effects = []

        total_persons_power = self.place.total_persons_power

        for person in self.place.persons:
            person_power_percent = float(person.power) / (total_persons_power+1)

            person_effect = self.PERSON_POWER_MODIFIER * self.PERSON_EFFECTS[person.type] * person.mastery

            if  person_effect == 0: continue

            effects.append((EFFECT_SOURCES.PERSON, '%s %s-%s' % (person.name, person.race_verbose, person.type_verbose), person_power_percent * person_effect))

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
    def modify_battles_per_turn(self, battles_per_turn): return battles_per_turn
    def modify_power(self, power): return power
    def modify_place_size(self, size): return size
    def modify_terrain_change_power(self, power): return power
    def full_regen_allowed(self): return False
    def modify_move_speed(self, speed): return speed


class TradeCenter(PlaceModifierBase):

    TYPE = e.CITY_MODIFIERS.TRADE_CENTER
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.TRADE_CENTER)
    NAME = u'Торговый центр'
    DESCRIPTION = u'В городе идёт оживлённая торговля, поэтому герои всегда могут найти выгодную цену для продажи своих трофеев или покупки артефактов.'

    def modify_sell_price(self, price): return price * 1.1
    def modify_buy_price(self, price): return price * 0.9


class CraftCenter(PlaceModifierBase):

    TYPE = e.CITY_MODIFIERS.CRAFT_CENTER
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.CRAFT_CENTER)
    NAME = u'Город мастеров'
    DESCRIPTION = u'Большое количество мастеров, трудящихся в городе, позволяет героям приобретать лучшие артефакты.'

    def can_buy_better_artifact(self): return random.uniform(0, 1) < 0.1


class Fort(PlaceModifierBase):

    TYPE = e.CITY_MODIFIERS.FORT
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.FORT)
    NAME = u'Форт'
    DESCRIPTION = u'Постоянное присутствие военных делает окрестности города безопаснее для путешествий.'

    def modify_battles_per_turn(self, battles_per_turn): return battles_per_turn * 0.75


class PoliticalCenter(PlaceModifierBase):

    TYPE = e.CITY_MODIFIERS.POLITICAL_CENTER
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.POLITICAL_CENTER)
    NAME = u'Политический центр'
    DESCRIPTION = u'Активная политическая жизнь приводит к тому, что усиливаются все изменения влияния (и положительные и отрицательные).'

    def modify_power(self, power): return power * 1.25


class Polic(PlaceModifierBase):
    TYPE = e.CITY_MODIFIERS.POLIC
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.POLIC)
    NAME = u'Полис'
    DESCRIPTION = u'Самостоятельная политика города вместе с большими свободами граждан способствует увеличению размера и широкому распространению влияния.'

    def modify_place_size(self, size): return min(places_settings.MAX_SIZE, size + 2)
    def modify_terrain_change_power(self, power): return power * 1.25


class Resort(PlaceModifierBase):

    TYPE = e.CITY_MODIFIERS.RESORT
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.RESORT)
    NAME = u'Курорт'
    DESCRIPTION = u'Город прославлен своими здравницами и особой атмосферой, в которой раны затягиваются особенно быстро. При посещении города герои полностью восстанавливают своё здоровье.'

    def full_regen_allowed(self): return True


class TransportNode(PlaceModifierBase):
    TYPE = e.CITY_MODIFIERS.TRANSPORT_NODE
    PERSON_EFFECTS = _get_profession_effects(e.CITY_MODIFIERS.TRANSPORT_NODE)
    NAME = u'Транспортный узел'
    DESCRIPTION = u'Хорошие дороги и обилие гостиниц делает путешествие по дорогам в окрестностях города быстрым и комфортным.'

    def modify_move_speed(self, speed): return speed * 1.25


MODIFIERS = dict( (modifier.get_id(), modifier)
                  for modifier in globals().values()
                  if isinstance(modifier, type) and issubclass(modifier, PlaceModifierBase) and modifier != PlaceModifierBase)
