# coding: utf-8

import math
import random

from game.balance.enums import PERSON_TYPE

# from game.map.places.modifiers.exceptions import PlaceModifierException

from common.utils.enum import create_enum

from game.map.places.conf import places_settings


EFFECT_SOURCES = create_enum('EFFECT_SOURCES', (('PERSON', 0, u'персонаж'),))


class PlaceModifierBase(object):

    NAME = None
    DESCRIPTION = None

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: 0,
                       PERSON_TYPE.FISHERMAN: 0,
                       PERSON_TYPE.TAILOR: 0,
                       PERSON_TYPE.CARPENTER: 0,
                       PERSON_TYPE.HUNTER: 0,
                       PERSON_TYPE.WARDEN: 0,
                       PERSON_TYPE.MERCHANT: 0,
                       PERSON_TYPE.INNKEEPER: 0,
                       PERSON_TYPE.ROGUE: 0,
                       PERSON_TYPE.FARMER: 0,
                       PERSON_TYPE.MINER: 0,
                       PERSON_TYPE.PRIEST: 0,
                       PERSON_TYPE.PHYSICIAN: 0,
                       PERSON_TYPE.ALCHEMIST: 0,
                       PERSON_TYPE.EXECUTIONER: 0,
                       PERSON_TYPE.MAGICIAN: 0,
                       PERSON_TYPE.MAYOR: 0,
                       PERSON_TYPE.BUREAUCRAT: 0,
                       PERSON_TYPE.ARISTOCRAT: 0,
                       PERSON_TYPE.BARD: 0}

    NECESSARY_BORDER = 75
    ENOUGH_BORDER = 50

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
    def size_modifier(self): return math.log(self.place.size, 2) + 1

    @classmethod
    def get_id(cls): return cls.__name__.lower()

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
    def is_enough_power(self): return self.power >= self.ENOUGH_BORDER

    @property
    def can_be_choosen(self): return self.power >= self.NECESSARY_BORDER

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

    NAME = u'Торговый центр'
    DESCRIPTION = u'В городе идёт оживлённая торговля, поэтому герои всегда могут найти выгодную цену для продажи своих трофеев или покупки артефактов.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: 2,
                       PERSON_TYPE.FISHERMAN: 1,
                       PERSON_TYPE.TAILOR: 2,
                       PERSON_TYPE.CARPENTER: 2,
                       PERSON_TYPE.HUNTER: 1,
                       PERSON_TYPE.WARDEN: -1,
                       PERSON_TYPE.MERCHANT: 5,
                       PERSON_TYPE.INNKEEPER: 3,
                       PERSON_TYPE.ROGUE: 1,
                       PERSON_TYPE.FARMER: 1,
                       PERSON_TYPE.MINER: 1,
                       PERSON_TYPE.PRIEST: -2,
                       PERSON_TYPE.PHYSICIAN: -2,
                       PERSON_TYPE.ALCHEMIST: 2,
                       PERSON_TYPE.EXECUTIONER: -3,
                       PERSON_TYPE.MAGICIAN: 2,
                       PERSON_TYPE.MAYOR: -2,
                       PERSON_TYPE.BUREAUCRAT: -3,
                       PERSON_TYPE.ARISTOCRAT: 1,
                       PERSON_TYPE.BARD: 3 }

    def modify_sell_price(self, price): return price * 1.1
    def modify_buy_price(self, price): return price * 0.9


class CraftCenter(PlaceModifierBase):

    NAME = u'Город мастеров'
    DESCRIPTION = u'Большое количество мастеров, трудящихся в городе, позволяет героям приобретать лучшие артефакты.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: 3,
                       PERSON_TYPE.FISHERMAN: 1,
                       PERSON_TYPE.TAILOR: 3,
                       PERSON_TYPE.CARPENTER: 3,
                       PERSON_TYPE.HUNTER: 1,
                       PERSON_TYPE.WARDEN: 0,
                       PERSON_TYPE.MERCHANT: -2,
                       PERSON_TYPE.INNKEEPER: -4,
                       PERSON_TYPE.ROGUE: -2,
                       PERSON_TYPE.FARMER: 1,
                       PERSON_TYPE.MINER: 1,
                       PERSON_TYPE.PRIEST: -2,
                       PERSON_TYPE.PHYSICIAN: -2,
                       PERSON_TYPE.ALCHEMIST: 3,
                       PERSON_TYPE.EXECUTIONER: -3,
                       PERSON_TYPE.MAGICIAN: 2,
                       PERSON_TYPE.MAYOR: 1,
                       PERSON_TYPE.BUREAUCRAT: -2,
                       PERSON_TYPE.ARISTOCRAT: -4,
                       PERSON_TYPE.BARD: -2 }

    def can_buy_better_artifact(self): return random.uniform(0, 1) < 0.1


class Fort(PlaceModifierBase):

    NAME = u'Форт'
    DESCRIPTION = u'Постоянное присутствие военных делает окрестности города более безопасыми для путешествий.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: 2,
                       PERSON_TYPE.FISHERMAN: -2,
                       PERSON_TYPE.TAILOR: 1,
                       PERSON_TYPE.CARPENTER: 1,
                       PERSON_TYPE.HUNTER: 2,
                       PERSON_TYPE.WARDEN: 5,
                       PERSON_TYPE.MERCHANT: -1,
                       PERSON_TYPE.INNKEEPER: -2,
                       PERSON_TYPE.ROGUE: 3,
                       PERSON_TYPE.FARMER: -2,
                       PERSON_TYPE.MINER: 1,
                       PERSON_TYPE.PRIEST: 1,
                       PERSON_TYPE.PHYSICIAN: 2,
                       PERSON_TYPE.ALCHEMIST: 1,
                       PERSON_TYPE.EXECUTIONER: 4,
                       PERSON_TYPE.MAGICIAN: 1,
                       PERSON_TYPE.MAYOR: 2,
                       PERSON_TYPE.BUREAUCRAT: 1,
                       PERSON_TYPE.ARISTOCRAT: 2,
                       PERSON_TYPE.BARD: 1 }

    def modify_battles_per_turn(self, battles_per_turn): return battles_per_turn * 0.75


class PoliticalCenter(PlaceModifierBase):

    NAME = u'Политический центр'
    DESCRIPTION = u'Активная политическая жизнь приводит к тому, что усиливаются все изменения влияния (и положительные и отрицательные).'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: -1,
                       PERSON_TYPE.FISHERMAN: -1,
                       PERSON_TYPE.TAILOR: -1,
                       PERSON_TYPE.CARPENTER: -1,
                       PERSON_TYPE.HUNTER: -1,
                       PERSON_TYPE.WARDEN: 2,
                       PERSON_TYPE.MERCHANT: 3,
                       PERSON_TYPE.INNKEEPER: 1,
                       PERSON_TYPE.ROGUE: 3,
                       PERSON_TYPE.FARMER: -1,
                       PERSON_TYPE.MINER: -1,
                       PERSON_TYPE.PRIEST: 1,
                       PERSON_TYPE.PHYSICIAN: 0,
                       PERSON_TYPE.ALCHEMIST: -1,
                       PERSON_TYPE.EXECUTIONER: 3,
                       PERSON_TYPE.MAGICIAN: 2,
                       PERSON_TYPE.MAYOR: 5,
                       PERSON_TYPE.BUREAUCRAT: 2,
                       PERSON_TYPE.ARISTOCRAT: 4,
                       PERSON_TYPE.BARD: 2 }

    def modify_power(self, power): return power * 1.25


class Polic(PlaceModifierBase):

    NAME = u'Полис'
    DESCRIPTION = u'Самостоятельная политика города вместе с большими свободами граждан способствует увеличению размера города более широкому распространению его влияния.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: 2,
                       PERSON_TYPE.FISHERMAN: 2,
                       PERSON_TYPE.TAILOR: 2,
                       PERSON_TYPE.CARPENTER: 2,
                       PERSON_TYPE.HUNTER: 2,
                       PERSON_TYPE.WARDEN: 2,
                       PERSON_TYPE.MERCHANT: 3,
                       PERSON_TYPE.INNKEEPER: 3,
                       PERSON_TYPE.ROGUE: -5,
                       PERSON_TYPE.FARMER: 2,
                       PERSON_TYPE.MINER: 2,
                       PERSON_TYPE.PRIEST: -2,
                       PERSON_TYPE.PHYSICIAN: 2,
                       PERSON_TYPE.ALCHEMIST: 2,
                       PERSON_TYPE.EXECUTIONER: -2,
                       PERSON_TYPE.MAGICIAN: 2,
                       PERSON_TYPE.MAYOR: -2,
                       PERSON_TYPE.BUREAUCRAT: -4,
                       PERSON_TYPE.ARISTOCRAT: -2,
                       PERSON_TYPE.BARD: 2 }

    def modify_place_size(self, size): return min(places_settings.MAX_SIZE, size + 2)
    def modify_terrain_change_power(self, power): return power * 1.25


class Resort(PlaceModifierBase):

    NAME = u'Курорт'
    DESCRIPTION = u'Город прославлен своими здравницами и особой атмосферой, в которой раны затягиваются особенно быстро. При посещении города герои полностью восстанавливают своё здоровье.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: -3,
                       PERSON_TYPE.FISHERMAN: 2,
                       PERSON_TYPE.TAILOR: -2,
                       PERSON_TYPE.CARPENTER: -2,
                       PERSON_TYPE.HUNTER: 2,
                       PERSON_TYPE.WARDEN: 2,
                       PERSON_TYPE.MERCHANT: 3,
                       PERSON_TYPE.INNKEEPER: 3,
                       PERSON_TYPE.ROGUE: -1,
                       PERSON_TYPE.FARMER: 2,
                       PERSON_TYPE.MINER: -3,
                       PERSON_TYPE.PRIEST: 2,
                       PERSON_TYPE.PHYSICIAN: 5,
                       PERSON_TYPE.ALCHEMIST: 1,
                       PERSON_TYPE.EXECUTIONER: -4,
                       PERSON_TYPE.MAGICIAN: 2,
                       PERSON_TYPE.MAYOR: 0,
                       PERSON_TYPE.BUREAUCRAT: -1,
                       PERSON_TYPE.ARISTOCRAT: 2,
                       PERSON_TYPE.BARD: 3 }

    def full_regen_allowed(self): return True


class TransportNode(PlaceModifierBase):

    NAME = u'Транстпортный узел'
    DESCRIPTION = u'Хорошие дороги и обилие гостиниц делает путешествие по дорогам в окрестностях города быстрым и комфортным.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: -2,
                       PERSON_TYPE.FISHERMAN: -1,
                       PERSON_TYPE.TAILOR: -2,
                       PERSON_TYPE.CARPENTER: -2,
                       PERSON_TYPE.HUNTER: -1,
                       PERSON_TYPE.WARDEN: 3,
                       PERSON_TYPE.MERCHANT: 4,
                       PERSON_TYPE.INNKEEPER: 5,
                       PERSON_TYPE.ROGUE: 1,
                       PERSON_TYPE.FARMER: -1,
                       PERSON_TYPE.MINER: -1,
                       PERSON_TYPE.PRIEST: -1,
                       PERSON_TYPE.PHYSICIAN: 0,
                       PERSON_TYPE.ALCHEMIST: -1,
                       PERSON_TYPE.EXECUTIONER: 0,
                       PERSON_TYPE.MAGICIAN: 1,
                       PERSON_TYPE.MAYOR: 2,
                       PERSON_TYPE.BUREAUCRAT: -1,
                       PERSON_TYPE.ARISTOCRAT: -1,
                       PERSON_TYPE.BARD: 1 }

    def modify_move_speed(self, speed): return speed * 1.25


MODIFIERS = dict( (modifier.get_id(), modifier)
                  for modifier in globals().values()
                  if isinstance(modifier, type) and issubclass(modifier, PlaceModifierBase) and modifier != PlaceModifierBase)
