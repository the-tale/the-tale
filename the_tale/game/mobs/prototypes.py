# -*- coding: utf-8 -*-
import math
import random

def get_mob_by_data(data):
    return MOB_PROTOTYPES[data['type']](data=data)

class MobException(Exception): pass

class MOB_DIFFICULTY:
    VERY_EASY = 'very_easy'
    EASY = 'easy'
    SOMEWHAT_EASY = 'somewhat_easy'
    NORMAL = 'normal'
    SOMEWHAT_HARD = 'somewhat_hard'
    HARD = 'hard'
    VERY_HARD = 'very_hard'
    IMPOSSIBLE = 'impossible'

DIFFICULTY_ORDER = (MOB_DIFFICULTY.VERY_EASY, 
                    MOB_DIFFICULTY.EASY, 
                    MOB_DIFFICULTY.SOMEWHAT_EASY, 
                    MOB_DIFFICULTY.NORMAL, 
                    MOB_DIFFICULTY.SOMEWHAT_HARD, 
                    MOB_DIFFICULTY.HARD, 
                    MOB_DIFFICULTY.VERY_HARD, 
                    MOB_DIFFICULTY.IMPOSSIBLE)

DIFFICULTY_TO_POWER_COOFICIENT = { MOB_DIFFICULTY.VERY_EASY: 0.4, 
                                   MOB_DIFFICULTY.EASY: 0.6, 
                                   MOB_DIFFICULTY.SOMEWHAT_EASY: 0.8, 
                                   MOB_DIFFICULTY.NORMAL: 1.0, 
                                   MOB_DIFFICULTY.SOMEWHAT_HARD: 1.2, 
                                   MOB_DIFFICULTY.HARD: 1.4, 
                                   MOB_DIFFICULTY.VERY_HARD: 1.6, 
                                   MOB_DIFFICULTY.IMPOSSIBLE: 1.8}

class MobAttributes(object):

    def __init__(self, damage_to_hero, damage_to_mob, battle_speed):
        self.damage_to_hero = damage_to_hero
        self.damage_to_mob = damage_to_mob
        self.battle_speed = battle_speed

    def get_damage_to_hero(self, hero):
        percents = random.uniform(*self.damage_to_hero)
        return percents, int(percents * hero.health)

    def get_damage_from_hero(self, hero):
        damage = random.randint(math.floor(hero.min_damage), math.ceil(hero.max_damage))
        percents_cooficient = (self.damage_to_mob[1] - self.damage_to_mob[0]) / float(hero.max_damage - hero.min_damage)
        damage_percents = self.damage_to_mob[0] + (damage - hero.min_damage) * percents_cooficient

        return hero.context.update_damage_from_hero(damage_percents, damage)

    def serialize(self):
        return {'damage_to_hero': self.damage_to_hero,
                'damage_to_mob': self.damage_to_mob,
                'battle_speed': self.battle_speed}

    @classmethod
    def deserialize(cls, data):
        return cls(damage_to_hero=data['damage_to_hero'],
                   damage_to_mob=data['damage_to_mob'],
                   battle_speed=data['battle_speed'])



class MobAttributesConstructor(object):

    def __init__(self, damage_to_hero, damage_to_mob, battle_speed):
        self.damage_to_hero = damage_to_hero
        self.damage_to_mob = damage_to_mob
        self.battle_speed = battle_speed

    def construct_attributes(self, difficulty):
        power = DIFFICULTY_TO_POWER_COOFICIENT[difficulty]
        return MobAttributes(damage_to_hero= map(lambda x: x * power,  self.damage_to_hero),
                             damage_to_mob= map(lambda x: x * power,  self.damage_to_mob),
                             battle_speed=random.uniform(*self.battle_speed))

class MobPrototype(object):

    NAME = ''
    LOOT_LIST = []
    ATTRIBUTES = None
    LOOT_BASIC_MODIFICATOR = None
    LOOT_EFFECTS_MODIFICATOR = None

    def __init__(self, hero_power=None, difficulty=None, data=None):
        if data:
            self.deserialize(data)
            return
            
        self.difficulty = difficulty
        self.health = 1.0
        self.power = DIFFICULTY_TO_POWER_COOFICIENT[difficulty] * hero_power
        self.attributes = self.ATTRIBUTES.construct_attributes(difficulty)

    @property
    def name(self):
        return u'%s (%s)' % (self.NAME, self.difficulty)

    @property
    def battle_speed(self):
        return self.attributes.battle_speed

    @classmethod
    def get_type_name(cls):
        return cls.__name__.lower()

    def strike_hero(self, hero):
        damage_percents, damage = self.attributes.get_damage_to_hero(hero)
        hero.health -= damage
        return damage

    def strike_by_hero(self, hero):
        damage_percents, damage = self.attributes.get_damage_from_hero(hero)
        self.health -= damage_percents
        return damage

    def striked_by(self, percents):
        self.health = max(0, self.health-percents)

    def kill(self):
        pass

    def get_loot(self, hero_chaoticity):
        from ..artifacts.constructors import generate_loot
        return generate_loot(self.LOOT_LIST, self.power, self.LOOT_BASIC_MODIFICATOR, self.LOOT_EFFECTS_MODIFICATOR, hero_chaoticity)

    def serialize(self):
        return {'type': self.get_type_name(),
                'attributes': self.attributes.serialize(),
                'health': self.health,
                'power': self.power,
                'difficulty': self.difficulty}

    def deserialize(self, data):
        self.difficulty = data['difficulty']
        self.health = data['health']
        self.power = data['power']
        self.attributes = MobAttributes.deserialize(data=data['attributes'])

    def ui_info(self):
        return { 'name': self.name,
                 'difficulty': self.difficulty,
                 'health': self.health }


from ..artifacts import constructors as loot

class Rat(MobPrototype):

    NAME = u'крыса'
    LOOT_LIST = [ (10, loot.RatTailConstructor),
                  (1, loot.PieceOfCheeseConstructor) ]

    ATTRIBUTES = MobAttributesConstructor(damage_to_hero=(0.05, 0.1), 
                                          damage_to_mob=(0.15, 0.25), 
                                          battle_speed=(3, 6) )
    LOOT_BASIC_MODIFICATOR = 2.0
    LOOT_EFFECTS_MODIFICATOR = 0.5

class Bandit(MobPrototype):

    NAME = u'бандит'
    LOOT_LIST = [ (1, loot.FakeAmuletConstructor),
                  (1, loot.BrokenSword),
                  (100, loot.DecrepitPlate)]
                  
    ATTRIBUTES = MobAttributesConstructor(damage_to_hero=(0.1, 0.2), 
                                          damage_to_mob=(0.1, 0.2), 
                                          battle_speed=(1, 4) )
    LOOT_BASIC_MODIFICATOR = 2.0
    LOOT_EFFECTS_MODIFICATOR = 0.5

MOB_PROTOTYPES = dict( (type_name.lower(), prototype)
                       for type_name, prototype in globals().items()
                       if isinstance(prototype, type) and issubclass(prototype, MobPrototype) and prototype != MobPrototype)

def get_random_mob():
    prototype = random.choice(MOB_PROTOTYPES.values())
    # TODO: calculate hero power
    return prototype(hero_power=1, difficulty=random.choice([MOB_DIFFICULTY.EASY, MOB_DIFFICULTY.NORMAL, MOB_DIFFICULTY.SOMEWHAT_HARD]) )
                                 
                                 
