# coding: utf-8

from dext.utils import s11n

from .prototypes import MobPrototype
from .models import MobConstructor

class MobConstructorPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def uuid(self): return self.model.uuid

    @property
    def name(self): return self.model.name

    @property
    def health_relative_to_hero(self): return self.model.health_relative_to_hero

    @property
    def initiative(self): return self.model.initiative

    @property
    def power_per_level(self): return self.model.power_per_level

    @property
    def damage_dispersion(self): return self.model.damage_dispersion

    @property
    def terrain(self): return self.model.terrain

    @property
    def abilities(self): 
        if not hasattr(self, '_abilities'):
            self._abilities = s11n.from_json(self.model.abilities)
        return self._abilities

    @property
    def loot_list(self): 
        if not hasattr(self, '_loot_list'):
            self._loot_list = s11n.from_json(self.model.loot_list)
        return self._loot_list

    ################################
    # object methods
    ################################
    
    @classmethod
    def get_random_mob(cls, hero):
        constructor = cls(model=MobConstructor.objects.filter(terrain=hero.position.get_terrain()).order_by('?')[0])
        return constructor.generate_mob(hero)


    def generate_mob(self, hero):
        mob = MobPrototype.construct(level=hero.level, 
                                     NAME=self.name, 
                                     HEALTH_RELATIVE_TO_HERO=self.health_relative_to_hero, 
                                     INITIATIVE=self.initiative,
                                     DAMAGE_DISPERSION=self.damage_dispersion,
                                     POWER_PER_LEVEL=self.power_per_level,
                                     ABILITIES=self.abilities,
                                     LOOT_LIST=self.loot_list)
        return mob
