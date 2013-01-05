# coding: utf-8

from game.persons.models import PERSON_TYPE
from game.game_info import RACE

# from game.map.places.modifiers.exceptions import PlaceModifierException

from common.utils.enum import create_enum


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
                       PERSON_TYPE.ARISTOCRAT: 0 }

    RACE_EFFECTS = { RACE.HUMAN: 0,
                     RACE.ELF: 0,
                     RACE.ORC: 0,
                     RACE.GOBLIN: 0,
                     RACE.DWARF: 0 }

    NECESSARY_BORDER = 75
    ENOUGH_BORDER = 50

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
            self._power = sum(effect[2] for effect in self.power_effects) * self.place.size
        return self._power

    @classmethod
    def get_id(cls): return cls.__name__.lower()

    def get_power_effects(self):
        effects = []

        total_persons_power = self.place.total_persons_power

        for person in self.place.persons:
            person_power_percent = float(person.power) / (total_persons_power+1)

            person_effect = self.PERSON_EFFECTS[person.type] * self.RACE_EFFECTS[person.race]

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


class TradeCenter(PlaceModifierBase):

    NAME = u'Торговый центр'
    DESCRIPTION = u'В городе идёт оживлённая торговля, поэтому герои всегда могут найти выгодную цену для продажи своих трофеев или покупки артефактов.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: 2,
                       PERSON_TYPE.FISHERMAN: 1,
                       PERSON_TYPE.TAILOR: 2,
                       PERSON_TYPE.CARPENTER: 2,
                       PERSON_TYPE.HUNTER: 1,
                       PERSON_TYPE.WARDEN: 0,
                       PERSON_TYPE.MERCHANT: 5,
                       PERSON_TYPE.INNKEEPER: 3,
                       PERSON_TYPE.ROGUE: -5,
                       PERSON_TYPE.FARMER: 1,
                       PERSON_TYPE.MINER: 1,
                       PERSON_TYPE.PRIEST: -2,
                       PERSON_TYPE.PHYSICIAN: -2,
                       PERSON_TYPE.ALCHEMIST: 2,
                       PERSON_TYPE.EXECUTIONER: -3,
                       PERSON_TYPE.MAGICIAN: 2,
                       PERSON_TYPE.MAYOR: 2,
                       PERSON_TYPE.BUREAUCRAT: -3,
                       PERSON_TYPE.ARISTOCRAT: -1 }

    RACE_EFFECTS = { RACE.HUMAN: 1,
                     RACE.ELF: 1,
                     RACE.ORC: 0.5,
                     RACE.GOBLIN: 3,
                     RACE.DWARF: 2 }


class CraftCenter(PlaceModifierBase):

    NAME = u'Город мастеров'
    DESCRIPTION = u'Большое количество мастеров, трудящихся в городе, позволяет героям приобретать лучшие артефакты.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: 5,
                       PERSON_TYPE.FISHERMAN: 0,
                       PERSON_TYPE.TAILOR: 2,
                       PERSON_TYPE.CARPENTER: 2,
                       PERSON_TYPE.HUNTER: 1,
                       PERSON_TYPE.WARDEN: 0,
                       PERSON_TYPE.MERCHANT: -2,
                       PERSON_TYPE.INNKEEPER: -3,
                       PERSON_TYPE.ROGUE: -2,
                       PERSON_TYPE.FARMER: 1,
                       PERSON_TYPE.MINER: 1,
                       PERSON_TYPE.PRIEST: -2,
                       PERSON_TYPE.PHYSICIAN: -2,
                       PERSON_TYPE.ALCHEMIST: 2,
                       PERSON_TYPE.EXECUTIONER: -3,
                       PERSON_TYPE.MAGICIAN: 1,
                       PERSON_TYPE.MAYOR: 2,
                       PERSON_TYPE.BUREAUCRAT: -2,
                       PERSON_TYPE.ARISTOCRAT: -4 }

    RACE_EFFECTS = { RACE.HUMAN: 1,
                     RACE.ELF: 1,
                     RACE.ORC: 1.5,
                     RACE.GOBLIN: 1.5,
                     RACE.DWARF: 3 }


class Fort(PlaceModifierBase):

    NAME = u'Форт'
    DESCRIPTION = u'Постоянное присутствие военных делает окрестности города более безопасыми для путешествий.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: 2,
                       PERSON_TYPE.FISHERMAN: 0,
                       PERSON_TYPE.TAILOR: 1,
                       PERSON_TYPE.CARPENTER: 1,
                       PERSON_TYPE.HUNTER: 2,
                       PERSON_TYPE.WARDEN: 5,
                       PERSON_TYPE.MERCHANT: 0,
                       PERSON_TYPE.INNKEEPER: 1,
                       PERSON_TYPE.ROGUE: 3,
                       PERSON_TYPE.FARMER: -2,
                       PERSON_TYPE.MINER: -2,
                       PERSON_TYPE.PRIEST: 1,
                       PERSON_TYPE.PHYSICIAN: 2,
                       PERSON_TYPE.ALCHEMIST: 1,
                       PERSON_TYPE.EXECUTIONER: 4,
                       PERSON_TYPE.MAGICIAN: 1,
                       PERSON_TYPE.MAYOR: 3,
                       PERSON_TYPE.BUREAUCRAT: 1,
                       PERSON_TYPE.ARISTOCRAT: 2 }

    RACE_EFFECTS = { RACE.HUMAN: 2,
                     RACE.ELF: 1,
                     RACE.ORC: 4,
                     RACE.GOBLIN: 0.5,
                     RACE.DWARF: 3 }


class PoliticalCenter(PlaceModifierBase):

    NAME = u'Политический центр'
    DESCRIPTION = u'Активная политическая жизнь приводит к тому, что усиливаются все изменения влияния (и положительные и отрицательные).'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: -1,
                       PERSON_TYPE.FISHERMAN: -1,
                       PERSON_TYPE.TAILOR: -1,
                       PERSON_TYPE.CARPENTER: -1,
                       PERSON_TYPE.HUNTER: -1,
                       PERSON_TYPE.WARDEN: 1,
                       PERSON_TYPE.MERCHANT: 2,
                       PERSON_TYPE.INNKEEPER: 2,
                       PERSON_TYPE.ROGUE: 3,
                       PERSON_TYPE.FARMER: -1,
                       PERSON_TYPE.MINER: -1,
                       PERSON_TYPE.PRIEST: 1,
                       PERSON_TYPE.PHYSICIAN: 0,
                       PERSON_TYPE.ALCHEMIST: -1,
                       PERSON_TYPE.EXECUTIONER: 2,
                       PERSON_TYPE.MAGICIAN: 1,
                       PERSON_TYPE.MAYOR: 5,
                       PERSON_TYPE.BUREAUCRAT: 2,
                       PERSON_TYPE.ARISTOCRAT: 4 }

    RACE_EFFECTS = { RACE.HUMAN: 3,
                     RACE.ELF: 2,
                     RACE.ORC: 1,
                     RACE.GOBLIN: 2,
                     RACE.DWARF: 1 }


class Polic(PlaceModifierBase):

    NAME = u'Полис'
    DESCRIPTION = u'Самостоятельная политика города вместе с большими свободами граждам способствует более широкому распространению влияния города.'

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
                       PERSON_TYPE.PRIEST: 2,
                       PERSON_TYPE.PHYSICIAN: 2,
                       PERSON_TYPE.ALCHEMIST: 2,
                       PERSON_TYPE.EXECUTIONER: -2,
                       PERSON_TYPE.MAGICIAN: 2,
                       PERSON_TYPE.MAYOR: 5,
                       PERSON_TYPE.BUREAUCRAT: -3,
                       PERSON_TYPE.ARISTOCRAT: -1 }

    RACE_EFFECTS = { RACE.HUMAN: 3,
                     RACE.ELF: 1,
                     RACE.ORC: 1,
                     RACE.GOBLIN: 2,
                     RACE.DWARF: 1 }


class Resort(PlaceModifierBase):

    NAME = u'Курорт'
    DESCRIPTION = u'Город прославлен своими здравницами, в которых раны героев затягиваются особенно быстро.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: -2,
                       PERSON_TYPE.FISHERMAN: 2,
                       PERSON_TYPE.TAILOR: 0,
                       PERSON_TYPE.CARPENTER: 0,
                       PERSON_TYPE.HUNTER: 2,
                       PERSON_TYPE.WARDEN: 1,
                       PERSON_TYPE.MERCHANT: 2,
                       PERSON_TYPE.INNKEEPER: 2,
                       PERSON_TYPE.ROGUE: -5,
                       PERSON_TYPE.FARMER: 0,
                       PERSON_TYPE.MINER: -3,
                       PERSON_TYPE.PRIEST: 1,
                       PERSON_TYPE.PHYSICIAN: 3,
                       PERSON_TYPE.ALCHEMIST: 1,
                       PERSON_TYPE.EXECUTIONER: -4,
                       PERSON_TYPE.MAGICIAN: 1,
                       PERSON_TYPE.MAYOR: 0,
                       PERSON_TYPE.BUREAUCRAT: -1,
                       PERSON_TYPE.ARISTOCRAT: 2 }

    RACE_EFFECTS = { RACE.HUMAN: 2,
                     RACE.ELF: 1,
                     RACE.ORC: 1,
                     RACE.GOBLIN: 2,
                     RACE.DWARF: 1 }


class TransportNode(PlaceModifierBase):

    NAME = u'Транстпортный узел'
    DESCRIPTION = u'Хорошие дороги и обилие гостиниц делает путешествие в окрестностях города быстрым и комфортным.'

    PERSON_EFFECTS = { PERSON_TYPE.BLACKSMITH: 0,
                       PERSON_TYPE.FISHERMAN: 0,
                       PERSON_TYPE.TAILOR: 0,
                       PERSON_TYPE.CARPENTER: 0,
                       PERSON_TYPE.HUNTER: 0,
                       PERSON_TYPE.WARDEN: 2,
                       PERSON_TYPE.MERCHANT: 3,
                       PERSON_TYPE.INNKEEPER: 5,
                       PERSON_TYPE.ROGUE: -2,
                       PERSON_TYPE.FARMER: 0,
                       PERSON_TYPE.MINER: 0,
                       PERSON_TYPE.PRIEST: 0,
                       PERSON_TYPE.PHYSICIAN: 0,
                       PERSON_TYPE.ALCHEMIST: 0,
                       PERSON_TYPE.EXECUTIONER: 0,
                       PERSON_TYPE.MAGICIAN: 1,
                       PERSON_TYPE.MAYOR: 2,
                       PERSON_TYPE.BUREAUCRAT: -1,
                       PERSON_TYPE.ARISTOCRAT: 2 }

    RACE_EFFECTS = { RACE.HUMAN: 2,
                     RACE.ELF: 1,
                     RACE.ORC: 0.5,
                     RACE.GOBLIN: 1,
                     RACE.DWARF: 3 }


MODIFIERS = dict( (modifier.get_id(), modifier)
                  for modifier in globals().values()
                  if isinstance(modifier, type) and issubclass(modifier, PlaceModifierBase) and modifier != PlaceModifierBase)
