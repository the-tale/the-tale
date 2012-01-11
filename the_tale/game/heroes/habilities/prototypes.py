#coding: utf-8

from ..hmessages import generator as msg_generator

class ABILITY_TYPE:
    BATTLE = 'battle'


class ABILITIES_EVENTS:
    
    STRIKE_MOB = 'strike_mob'


def sum_probabilities(a, b): return a + b - a * b


class AbilityPrototype(object):

    TYPE = None
    EVENTS = []
    LEVELS = []
    
    NAME = u''
    DESCRIPTIN = u''

    def __init__(self, level):
        self.level = level

    @classmethod
    def get_id(cls): return cls.__name__.lower()

    def use(self, *argv):
        raise NotImplemented('you should declare use method in child classes')

    @property
    def priority(self): return self.LEVELS[self.level][0]

    def can_use(self, hero):
        return True
    

class MagicMushroom(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    EVENTS = [ABILITIES_EVENTS.STRIKE_MOB]
    #<priority, damage factor>
    LEVELS = [(1, 1.5),
              (1, 2.0),
              (1, 2.5),
              (1, 3.0)]

    NAME = u'Волшебный гриб'
    
    DESCRIPTION = u'Находясь в бою, герой может силой своей могучей воли вырастить волшебный гриб, съев который, станет наносить увеличеный урон противникам, пока сам не получит повреждения.'

    def use(self, hero):
        hero.context.ability_magick_mushroom = self.LEVELS[self.level][1]
        hero.push_message(msg_generator.msg_habilities_use(hero, self))


class Sidestep(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    EVENTS = [ABILITIES_EVENTS.STRIKE_MOB]
    #<priority, success probability>
    LEVELS = [(1, 0.2),
              (1, 0.4),
              (1, 0.6),
              (1, 0.8)]

    NAME = u'Шаг в сторону'
    
    DESCRIPTION = u'Герой быстро меняет свою позицию, дезариентируя противника из-за чего следующий удар по герою уйдёт в пустоту.'

    def use(self, hero):
        hero.context.ability_once_mob_miss = sum_probabilities(hero.context.ability_once_mob_miss, self.LEVELS[self.level][1])
        hero.push_message(msg_generator.msg_habilities_use(hero, self))


class RunUpPush(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    EVENTS = [ABILITIES_EVENTS.STRIKE_MOB]
    #<priority, damage factor, stun probability>
    LEVELS = [(1, 0.5, 0.1),
              (1, 1.0, 0.2),
              (1, 1.5, 0.3),
              (1, 2.0, 0.4)]

    NAME = u'Разбег-толчок'
    
    DESCRIPTION = u'Герой разбегается и наносит урон противнику. Существует вероятность, что противник будет оглушён и пропустит следующую атаку.'

    def use(self, hero):
        hero.context.ability_once_damage_factor *= self.LEVELS[self.level][1]
        hero.context.ability_once_mob_miss = sum_probabilities(hero.context.ability_once_mob_miss, self.LEVELS[self.level][2])
        hero.push_message(msg_generator.msg_habilities_use(hero, self))


class MeNotHere(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    EVENTS = [ABILITIES_EVENTS.STRIKE_MOB]
    #<priority, health percent, hide probability>
    LEVELS = [(2, 0.1, 0.1),
              (3, 0.11, 0.15),
              (4, 0.13, 0.2),
              (5, 0.15, 0.25)]

    NAME = u'Нет никто'
    
    DESCRIPTION = u'Если у героя останется мало здоровья, то он может попытаться спрятаться, тем самым выйдя из боя'

    def can_use(self, hero):
        return hero.health / float(hero.max_health) <= self.LEVELS[self.level][1]

    def use(self, hero):
        hero.context.ability_once_leave_battle = sum_probabilities(hero.context.ability_once_leave_battle, self.LEVELS[self.level][2])
        hero.push_message(msg_generator.msg_habilities_use(hero, self))


class Regeneration(AbilityPrototype):
    
    TYPE = ABILITY_TYPE.BATTLE
    EVENTS = [ABILITIES_EVENTS.STRIKE_MOB]
    #<priority, health percent>
    LEVELS = [(1, 0.5),
              (1, 0.7),
              (1, 0.10),
              (1, 0.13)]

    NAME = u'Регенерация'
    
    DESCRIPTION = u'Во время боя герой может восстановить часть своего здоровья'

    def can_use(self, hero):
        return hero.health < hero.max_health

    def use(self, hero):
        health_to_regen = hero.max_health * self.LEVELS[self.level][1]
        hero.health = min(hero.health + health_to_regen, hero.max_health)
        hero.push_message(msg_generator.msg_habilities_use(hero, self))


ABILITIES = dict( (ability.get_id(), ability) 
                  for ability in globals().values() 
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
