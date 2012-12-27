#coding: utf-8
import random

from common.utils.enum import create_enum

from game.balance import formulas as f

ABILITY_TYPE = create_enum('ABILITY_TYPE', (('BATTLE', 0, u'боевая'),
                                            ('NONBATTLE', 1, u'небоевая'),) )

ABILITY_ACTIVATION_TYPE = create_enum('ABILITY_ACTIVATION_TYPE', (('ACTIVE', 0, u'активная'),
                                                                  ('PASSIVE', 1, u'пассивная'),))


ABILITY_LOGIC_TYPE = create_enum('ABILITY_LOGIC_TYPE', (('WITHOUT_CONTACT', 0, u'безконтактная'),
                                                        ('WITH_CONTACT', 1, u'контактная'),))

ABILITY_AVAILABILITY = create_enum('ABILITY_AVAILABILITY', (('FOR_PLAYERS', 0b0001, u'только для игроков'),
                                                            ('FOR_MONSTERS', 0b0010, u'только для монстров'),
                                                            ('FOR_ALL', 0b0011, u'для всех')))


class AbilityPrototype(object):

    TYPE = None
    ACTIVATION_TYPE = None
    LOGIC_TYPE = None
    PRIORITY = None
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_ALL

    NAME = u''
    normalized_name = u''
    DESCRIPTIN = u''
    MAX_LEVEL = 5

    def __init__(self, level=1):
        self.level = level

    def serialize(self):
        return {'level': self.level}

    @classmethod
    def deserialize(cls, data):
        return cls(level=data['level'])

    @property
    def type(self): return ABILITY_TYPE(self.TYPE)

    @property
    def availability(self): return ABILITY_AVAILABILITY(self.AVAILABILITY)

    @property
    def activation_type(self): return ABILITY_ACTIVATION_TYPE(self.ACTIVATION_TYPE)

    @property
    def has_max_level(self): return self.level == self.MAX_LEVEL

    @property
    def priority(self): return self.PRIORITY[self.level-1]

    @classmethod
    def get_id(cls): return cls.__name__.lower()

    def modify_attribute(self, name, value): return value

    def update_context(self, actor, enemy): pass

    def update_quest_reward(self, hero, money): return money

    def update_buy_price(self, hero, money): return money

    def update_sell_price(self, hero, money): return money

    def can_be_used(self, actor): return True

    def use(self, *argv):
        raise NotImplemented('you should declare use method in child classes')

    def on_miss(self, *argv):
        raise NotImplemented('you should declare on_miss method in child classes')

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.level == other.level)


class HIT(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITY_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = [100, 100, 100, 100, 100]

    NAME = u'Удар'
    normalized_name = NAME
    DESCRIPTION = u'Каждый уважающий себя герой должен быть в состоянии ударить противника, или пнуть.'

    DAMAGE_MODIFIER = [1.00, 1.25, 1.50, 2.00, 2.25]

    @property
    def damage_modifier(self): return self.DAMAGE_MODIFIER[self.level-1]

    def use(self, messanger, actor, enemy):
        damage = actor.context.modify_initial_damage(actor.basic_damage*self.damage_modifier)
        enemy.change_health(-damage)
        messanger.add_message('hero_ability_hit', attacker=actor, defender=enemy, damage=damage)

    def on_miss(self, messanger, actor, enemy):
        messanger.add_message('hero_ability_hit_miss', attacker=actor, defender=enemy)


class MAGIC_MUSHROOM(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITY_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = [10, 10, 10, 10, 10]

    NAME = u'Волшебный гриб'
    normalized_name = NAME
    DESCRIPTION = u'Находясь в бою, герой может силой своей могучей воли вырастить волшебный гриб, съев который, некоторое время станет наносить увеличенный урон противникам.'

    DAMAGE_FACTORS = [ [2.00, 1.50],
                       [2.25, 1.75, 1.25],
                       [2.50, 2.00, 1.50],
                       [2.75, 2.25, 1.75, 1.25],
                       [3.00, 2.50, 2.00, 1.50] ]

    @property
    def damage_factors(self): return self.DAMAGE_FACTORS[self.level-1]

    def use(self, messanger, actor, enemy):
        actor.context.use_ability_magic_mushroom(self.damage_factors)
        messanger.add_message('hero_ability_magicmushroom', actor=actor)


class SIDESTEP(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITY_LOGIC_TYPE.WITHOUT_CONTACT

    PRIORITY = [10, 11, 12, 13, 14]

    NAME = u'Шаг в сторону'
    normalized_name = NAME
    DESCRIPTION = u'Герой быстро меняет свою позицию, дезориентируя противника, из-за чего тот начинает промахиваться.'

    MISS_PROBABILITIES = [ [0.50, 0.25, 0.125],
                           [0.60, 0.30, 0.150],
                           [0.70, 0.35, 0.175],
                           [0.80, 0.40, 0.200, 0.1000],
                           [0.90, 0.45, 0.225, 0.1125] ]

    @property
    def miss_probabilities(self): return self.MISS_PROBABILITIES[self.level-1]

    def use(self, messanger, actor, enemy):
        enemy.context.use_ability_sidestep(self.miss_probabilities)
        messanger.add_message('hero_ability_sidestep', attacker=actor, defender=enemy)

    def on_miss(self, messanger, actor, enemy):
        messanger.add_message('hero_ability__miss', attacker=actor, defender=enemy)


class RUN_UP_PUSH(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITY_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = [10, 11, 12, 13, 14]

    NAME = u'Разбег-толчок'
    normalized_name = NAME
    DESCRIPTION = u'Герой разбегается и наносит урон противнику. Враг будет оглушён и пропустит следующую атаку.'

    STUN_LENGTH = [ (1, 1),
                    (1, 2),
                    (1, 3),
                    (2, 3),
                    (2, 4) ]

    @property
    def stun_length(self): return self.STUN_LENGTH[self.level-1]

    def use(self, messanger, actor, enemy):
        damage = actor.context.modify_initial_damage(actor.basic_damage)
        enemy.change_health(-damage)
        enemy.context.use_stun(random.randint(*self.stun_length))
        messanger.add_message('hero_ability_runuppush', attacker=actor, defender=enemy, damage=damage)

    def on_miss(self, messanger, actor, enemy):
        messanger.add_message('hero_ability_runuppush_miss', attacker=actor, defender=enemy)



class REGENERATION(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = ABILITY_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = [10, 11, 12, 13, 14]

    NAME = u'Регенерация'
    normalized_name = NAME
    DESCRIPTION = u'Во время боя герой может восстановить часть своего здоровья.'

    RESTORED_PERCENT = [0.05, 0.10, 0.15, 0.20, 0.25]

    @property
    def restored_percent(self): return self.RESTORED_PERCENT[self.level-1]

    def can_be_used(self, actor): return actor.health < actor.max_health

    def use(self, messanger, actor, enemy):
        health_to_regen = f.mob_hp_to_lvl(actor.level) * self.restored_percent # !!!MOB HP, NOT HERO!!!
        applied_health = actor.change_health(health_to_regen)
        messanger.add_message('hero_ability_regeneration', actor=actor, health=applied_health)


class CRITICAL_HIT(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Критический удар'
    normalized_name = NAME
    DESCRIPTION = u'Удача благосклонна к герою — урон от любого удара может существенно увеличится.'

    CRITICAL_CHANCE = [0.05, 0.08, 0.11, 0.14, 0.17]

    @property
    def critical_chance(self): return self.CRITICAL_CHANCE[self.level-1]

    def update_context(self, actor, enemy):
        actor.context.use_crit_chance(self.critical_chance)


class BERSERK(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Берсерк'
    normalized_name = NAME
    DESCRIPTION = u'Чем меньше у героя остаётся здоровья, тем сильнее его удары.'

    MAXIMUM_BONUS = [0.1, 0.13, 0.16, 0.19, 0.22]

    @property
    def maximum_bonus(self): return self.MAXIMUM_BONUS[self.level-1]

    def update_context(self, actor, enemy):
        actor.context.use_berserk(1 + self.maximum_bonus * float(actor.max_health - actor.health) / actor.max_health)


class NINJA(AbilityPrototype):

    TYPE = ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Ниндзя'
    normalized_name = NAME
    DESCRIPTION = u'Ниндзя может уклониться от атаки противника.'

    MISS_PROBABILITY = [0.05, 0.08, 0.11, 0.14, 0.17]

    @property
    def miss_probability(self): return self.MISS_PROBABILITY[self.level-1]

    def update_context(self, actor, enemy):
        enemy.context.use_ninja(self.miss_probability)



ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
