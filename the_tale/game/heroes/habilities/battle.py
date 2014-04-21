#coding: utf-8
import random

from the_tale.game.heroes.habilities.prototypes import AbilityPrototype
from the_tale.game.heroes.habilities import relations

from the_tale.game.balance import constants as c, formulas as f


class HIT(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = [100]
    MAX_LEVEL = 1

    NAME = u'Удар'
    normalized_name = NAME
    DESCRIPTION = u'Каждый уважающий себя герой должен быть в состоянии ударить противника, или пнуть.'

    DAMAGE_MODIFIER = [1.00]

    @property
    def damage_modifier(self): return self.DAMAGE_MODIFIER[self.level-1]

    def use(self, messanger, actor, enemy):
        damage = actor.basic_damage*self.damage_modifier
        damage = actor.context.modify_outcoming_damage(damage)
        damage = enemy.context.modify_incoming_damage(damage)
        enemy.change_health(-damage.total)
        messanger.add_message('hero_ability_hit', attacker=actor, defender=enemy, damage=damage.total)

    def on_miss(self, messanger, actor, enemy):
        messanger.add_message('hero_ability_hit_miss', attacker=actor, defender=enemy)


class STRONG_HIT(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITH_CONTACT

    PRIORITY = [15, 16, 17, 18, 19]

    NAME = u'Тяжёлый удар'
    normalized_name = NAME
    DESCRIPTION = u'Если хорошенько размахнуться и правильно ударить, то удар получится намного сильнее и болезненней.'

    DAMAGE_MODIFIER = [1.25, 1.4, 1.55, 1.7, 1.85]

    @property
    def damage_modifier(self): return self.DAMAGE_MODIFIER[self.level-1]

    def use(self, messanger, actor, enemy):
        damage = actor.basic_damage * self.damage_modifier
        damage = actor.context.modify_outcoming_damage(damage)
        damage = enemy.context.modify_incoming_damage(damage)
        enemy.change_health(-damage.total)
        messanger.add_message('hero_ability_strong_hit', attacker=actor, defender=enemy, damage=damage.total)

    def on_miss(self, messanger, actor, enemy):
        messanger.add_message('hero_ability_strong_hit_miss', attacker=actor, defender=enemy)


class MAGIC_MUSHROOM(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = [9, 11, 11, 12, 12]

    NAME = u'Волшебный гриб'
    normalized_name = NAME
    DESCRIPTION = u'Герой всегда носит с собой особые грибы, съев один из которых в бою, на некоторое время существенно увеличивает наносимый урон.'

    DAMAGE_FACTORS = [ [1.75, 1.55, 1.25, 1.05],
                       [1.85, 1.65, 1.40, 1.15],
                       [1.90, 1.70, 1.45, 1.20],
                       [2.05, 1.80, 1.60, 1.30],
                       [2.15, 1.85, 1.70, 1.35] ]

    @property
    def damage_factors(self): return self.DAMAGE_FACTORS[self.level-1]

    def use(self, messanger, actor, enemy): # pylint: disable=W0613
        actor.context.use_ability_magic_mushroom(self.damage_factors)
        messanger.add_message('hero_ability_magicmushroom', actor=actor)


class SIDESTEP(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = [12, 13, 14, 15, 16]

    NAME = u'Шаг в сторону'
    normalized_name = NAME
    DESCRIPTION = u'Герой быстро меняет свою позицию, дезориентируя противника, из-за чего тот начинает промахиваться.'

    MISS_PROBABILITIES = [ [1.00, 0.35, 0.175],
                           [1.00, 0.45, 0.200, 0.05],
                           [1.00, 0.55, 0.225, 0.10, 0.05],
                           [1.00, 0.65, 0.250, 0.15, 0.10],
                           [1.00, 0.75, 0.275, 0.20, 0.15]]

    @property
    def miss_probabilities(self): return self.MISS_PROBABILITIES[self.level-1]

    def use(self, messanger, actor, enemy):
        enemy.context.use_ability_sidestep(self.miss_probabilities)
        messanger.add_message('hero_ability_sidestep', attacker=actor, defender=enemy)

    def on_miss(self, messanger, actor, enemy):
        messanger.add_message('hero_ability__miss', attacker=actor, defender=enemy)


class RUN_UP_PUSH(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = [7, 8, 9, 10, 11]

    NAME = u'Разбег-толчок'
    normalized_name = NAME
    DESCRIPTION = u'Герой разбегается и наносит урон противнику. Враг будет оглушён и пропустит один или несколько ходов атаки.'

    DAMAGE_MODIFIER = [0.35, 0.45, 0.55, 0.65, 0.75]

    STUN_LENGTH = [ (1.0, 1.6),
                    (1.0, 1.7),
                    (1.0, 1.9),
                    (1.0, 2.2),
                    (1.0, 2.6) ]

    @property
    def stun_length(self): return self.STUN_LENGTH[self.level-1]

    @property
    def damage_modifier(self): return self.DAMAGE_MODIFIER[self.level-1]

    def use(self, messanger, actor, enemy):
        damage = actor.basic_damage * self.damage_modifier
        damage = actor.context.modify_outcoming_damage(damage)
        damage = enemy.context.modify_incoming_damage(damage)
        enemy.change_health(-damage.total)
        enemy.context.use_stun(int(round(random.uniform(*self.stun_length))))
        messanger.add_message('hero_ability_runuppush', attacker=actor, defender=enemy, damage=damage.total)

    def on_miss(self, messanger, actor, enemy):
        messanger.add_message('hero_ability_runuppush_miss', attacker=actor, defender=enemy)



class REGENERATION(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = [8, 9, 10, 11, 12]

    NAME = u'Регенерация'
    normalized_name = NAME
    DESCRIPTION = u'Во время боя герой может восстановить часть своего здоровья.'

    RESTORED_PERCENT = [0.17, 0.20, 0.23, 0.25, 0.28]

    @property
    def restored_percent(self): return self.RESTORED_PERCENT[self.level-1]

    def can_be_used(self, actor): return actor.health < actor.max_health

    def use(self, messanger, actor, enemy): # pylint: disable=W0613
        health_to_regen = f.mob_hp_to_lvl(actor.level) * self.restored_percent * (1 + random.uniform(-c.DAMAGE_DELTA, c.DAMAGE_DELTA))# !!!MOB HP, NOT HERO!!!
        applied_health = int(round(actor.change_health(health_to_regen)))
        messanger.add_message('hero_ability_regeneration', actor=actor, health=applied_health)


class CRITICAL_HIT(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Критический удар'
    normalized_name = NAME
    DESCRIPTION = u'Удача благосклонна к герою — урон от любого удара может существенно увеличиться.'

    CRITICAL_CHANCE = [0.03, 0.06, 0.09, 0.10, 0.13]

    @property
    def critical_chance(self): return self.CRITICAL_CHANCE[self.level-1]

    def update_context(self, actor, enemy):
        actor.context.use_crit_chance(self.critical_chance)


class BERSERK(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Берсерк'
    normalized_name = NAME
    DESCRIPTION = u'Чем меньше у героя остаётся здоровья, тем больше урона врагу он наносит.'

    MAXIMUM_BONUS = [0.05, 0.10, 0.15, 0.20, 0.25]

    @property
    def maximum_bonus(self): return self.MAXIMUM_BONUS[self.level-1]

    def update_context(self, actor, enemy):
        actor.context.use_berserk(1 + self.maximum_bonus * float(actor.max_health - actor.health) / actor.max_health)


class NINJA(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = u'Ниндзя'
    normalized_name = NAME
    DESCRIPTION = u'Ниндзя может уклониться от атаки противника.'

    MISS_PROBABILITY = [0.025, 0.05, 0.075, 0.10, 0.120]

    @property
    def miss_probability(self): return self.MISS_PROBABILITY[self.level-1]

    def update_context(self, actor, enemy):
        enemy.context.use_ninja(self.miss_probability)


class FIREBALL(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = [4, 5, 6, 7, 8]

    NAME = u'Шар огня'
    normalized_name = NAME
    DESCRIPTION = u'Герой запускает в противника шар волшебного огня, нанося большой урон и поджигая врага.'

    DAMAGE_MODIFIER = [1.45, 1.50, 1.55, 1.60, 1.65]
    PERIODIC_DAMAGE_MODIFIERS = [ [0.18, 0.08],
                                  [0.22, 0.12, 0.02],
                                  [0.26, 0.16, 0.06],
                                  [0.30, 0.20, 0.10, 0.05],
                                  [0.34, 0.24, 0.14, 0.09] ]

    @property
    def damage_modifier(self): return self.DAMAGE_MODIFIER[self.level-1]

    @property
    def periodic_damage_modifiers(self): return self.PERIODIC_DAMAGE_MODIFIERS[self.level-1]

    def use(self, messanger, actor, enemy):
        damage = actor.basic_damage * self.damage_modifier
        outcoming_damage = actor.context.modify_outcoming_damage(damage)
        damage = enemy.context.modify_incoming_damage(outcoming_damage)
        enemy.change_health(-damage.total)
        enemy.context.use_damage_queue_fire([outcoming_damage * modifier for modifier in self.periodic_damage_modifiers])
        messanger.add_message('hero_ability_fireball', attacker=actor, defender=enemy, damage=damage.total)

    def on_miss(self, messanger, actor, enemy):
        messanger.add_message('hero_ability_fireball_miss', attacker=actor, defender=enemy)


class POISON_CLOUD(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = [6, 7, 8, 9, 10]

    NAME = u'Ядовитое облако'
    normalized_name = NAME
    DESCRIPTION = u'Вокруг противника сгущается ядовитое облако, вызывающее сильное отравление, из-за которого враг начинает постепенно терять здоровье.'

    PERIODIC_DAMAGE_MODIFIERS = [ [0.75, 0.50, 0.25],
                                  [0.90, 0.65, 0.40],
                                  [1.00, 0.70, 0.45],
                                  [1.05, 0.75, 0.50],
                                  [1.10, 0.80, 0.55]]

    @property
    def periodic_damage_modifiers(self): return self.PERIODIC_DAMAGE_MODIFIERS[self.level-1]

    def use(self, messanger, actor, enemy):
        damage = actor.basic_damage
        damage = actor.context.modify_outcoming_damage(damage)
        enemy.context.use_damage_queue_poison([damage * modifier for modifier in self.periodic_damage_modifiers])
        messanger.add_message('hero_ability_poison_cloud', attacker=actor, defender=enemy)


class VAMPIRE_STRIKE(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITH_CONTACT
    PRIORITY = [14, 15, 16, 17, 18]

    NAME = u'Удар вампира'
    normalized_name = NAME
    DESCRIPTION = u'Секретный удар, лечащий героя на величину, пропорциональную нанесённому урону.'

    DAMAGE_FRACTION = [0.85, 0.95, 1.00, 1.10, 1.15]
    HEAL_FRACTION =   [0.45, 0.55, 0.65, 0.70, 0.75]

    @property
    def heal_fraction(self): return self.HEAL_FRACTION[self.level-1]

    @property
    def damage_fraction(self): return self.DAMAGE_FRACTION[self.level-1]

    def use(self, messanger, actor, enemy):
        damage = actor.basic_damage * self.damage_fraction
        damage = actor.context.modify_outcoming_damage(damage)
        damage = enemy.context.modify_incoming_damage(damage)
        health = int(round(damage.total * self.heal_fraction))
        enemy.change_health(-damage.total)
        actor.change_health(health)
        messanger.add_message('hero_ability_vampire_strike', attacker=actor, defender=enemy, damage=damage.total, health=health)

    def on_miss(self, messanger, actor, enemy):
        messanger.add_message('hero_ability_vampire_strike_miss', attacker=actor, defender=enemy)


class FREEZING(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = [7, 8, 10, 10, 11]

    NAME = u'Заморозка'
    normalized_name = NAME
    DESCRIPTION = u'Противника пронзает ужасный холод, замедляя его движения.'

    INITIATIVE_MODIFIERS = [ [0.37, 0.48, 0.58, 0.68, 0.78, 0.88],
                             [0.33, 0.44, 0.54, 0.64, 0.74, 0.84, 0.94],
                             [0.29, 0.39, 0.51, 0.61, 0.71, 0.81, 0.91],
                             [0.25, 0.35, 0.47, 0.57, 0.67, 0.77, 0.87],
                             [0.23, 0.33, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]]

    @property
    def initiative_modifiers(self): return self.INITIATIVE_MODIFIERS[self.level-1]

    def use(self, messanger, actor, enemy):
        enemy.context.use_initiative(self.initiative_modifiers)
        messanger.add_message('hero_ability_freezing', attacker=actor, defender=enemy)


class SPEEDUP(AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.ACTIVE
    LOGIC_TYPE = relations.ABILITY_LOGIC_TYPE.WITHOUT_CONTACT
    PRIORITY = [8, 10, 11, 11, 12]

    NAME = u'Ускорение'
    normalized_name = NAME
    DESCRIPTION = u'Воин накачивает себя магической энергией, временно улучшая свои рефлексы.'

    INITIATIVE_MODIFIERS = [ [2.90, 2.40, 1.80, 1.40],
                             [3.15, 2.55, 2.00, 1.55, 1.05],
                             [3.20, 2.70, 2.10, 1.70, 1.20],
                             [3.35, 2.85, 2.35, 1.85, 1.35],
                             [3.50, 3.00, 2.50, 2.00, 1.50] ]

    @property
    def initiative_modifiers(self): return self.INITIATIVE_MODIFIERS[self.level-1]

    def use(self, messanger, actor, enemy):
        actor.context.use_initiative(self.initiative_modifiers)
        messanger.add_message('hero_ability_speedup', attacker=actor, defender=enemy)


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
