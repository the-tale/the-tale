# -*- coding: utf-8 -*-
from dext.utils import s11n
from dext.utils import database

from game.heroes.prototypes import get_heroes_by_query

from game.balance import constants as c

from game.angels.models import Angel


class AngelPrototype(object):

    def __init__(self, model=None):
        self.model = model
        self.updated = False

    @classmethod
    def get_by_id(cls, id_):
        return cls(model=Angel.objects.get(id=id_))

    @classmethod
    def get_by_account(cls, account):
        return cls(model=Angel.objects.get(account_id=account.id))

    @property
    def id(self): return self.model.id

    @property
    def name(self): return self.model.name

    def get_updated_at_turn(self): return self.model.updated_at_turn
    def set_updated_at_turn(self, value): self.model.updated_at_turn = value
    updated_at_turn = property(get_updated_at_turn, set_updated_at_turn)

    @property
    def energy_maximum(self): return c.ANGEL_ENERGY_MAX

    def get_energy_at_turn(self, turn_number):
        # print turn_number, self.updated_at_turn, c.ANGEL_ENERGY_REGENERATION_PERIOD
        regeneration_periods = int(turn_number - self.updated_at_turn) / c.ANGEL_ENERGY_REGENERATION_PERIOD
        return min(self.energy_maximum, self.model.energy + c.ANGEL_ENERGY_REGENERATION_AMAUNT * regeneration_periods)

    def set_energy_at_turn(self, turn_number, energy):
        self.updated_at_turn = turn_number
        self.updated = True
        self.model.energy = energy

    def heroes(self):
        #TODO: now this code only works on bundle init phase
        #      using it from another places is dangerouse becouse of
        #      desinchronization between workers and database
        if not hasattr(self, '_heroes'):
            self._heroes = get_heroes_by_query(self.model.heroes.all())
        return self._heroes

    def load_abilities(self):
        from ..abilities.prototypes import AbilityPrototype
        from ..abilities.deck import ABILITIES
        data = s11n.from_json(self.model.abilities)
        abilities = {}
        for ability_dict in data.values():
            ability = AbilityPrototype.deserialize(ability_dict)
            if ability is None:
                continue
            abilities[ability.get_type()] = ability

        for ability_type, ability in ABILITIES.items():
            if ability_type not in abilities:
                abilities[ability_type] = ability()

        self._abilities = abilities

    def save_abilities(self):
        data = {}
        for ability in self.abilities.values():
            data[ability.get_type()] = ability.serialize()
        self.model.abilities = s11n.to_json(data)

    @property
    def abilities(self):
        if not hasattr(self, '_abilities'):
            self.load_abilities()
        return self._abilities

    ###########################################
    # Object operations
    ###########################################

    def remove(self):
        for hero in self.heroes():
            hero.remove()
        self.model.delete()

    def save(self):
        self.save_abilities()
        database.raw_save(self.model)
        # self.model.save(force_update=True)
        self.updated = False

    def ui_info(self, turn_number, ignore_actions=False, ignore_quests=False):
        return {'id': self.id,
                'name': self.name,
                'energy': { 'max': self.energy_maximum,
                            'value': self.get_energy_at_turn(turn_number) },
                'abilities': [ability.ui_info() for ability_type, ability in self.abilities.items()]
                }

    @classmethod
    def create(cls, account, name):
        # from ..abilities import deck
        # TODO: rewrite from create-change-save to save
        angel_model = Angel.objects.create(account=account.model, name=name, energy=c.ANGEL_ENERGY_MAX)
        angel = AngelPrototype(model=angel_model)
        # angel.abilities.update({deck.Help.get_type(): deck.Help()})
        # angel.save()

        return angel


    ###########################################
    # Next turn operations
    ###########################################

    def process_turn(self, turn_number):
        return turn_number + 1

    def __eq__(self, other):
        # print 'angel'
        # print self.id == other.id
        # print self.name == other.name
        # print self.updated_at_turn == other.updated_at_turn
        # print self.energy == other.energy
        # print self.abilities == other.abilities
        return (self.id == other.id and
                self.name == other.name and
                self.updated_at_turn == other.updated_at_turn and
                self.model.energy == other.model.energy and
                self.abilities == other.abilities)
