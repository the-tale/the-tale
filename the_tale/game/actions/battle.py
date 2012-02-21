# coding: utf-8

import random

from ..heroes.habilities import ABILITIES_LOGIC_TYPE

class Actor(object):

    def __init__(self, actor, context): 
        self.actor = actor
        self.context = context
        self.messages = []

    @property
    def initiative(self): return self.actor.battle_speed

    @property
    def name(self): return self.actor.name

    @property
    def power(self): return self.actor.power
    
    def get_basic_damage(self): return self.actor.get_basic_damage()

    @property
    def health(self): return self.actor.health

    @property
    def max_health(self): return self.actor.max_health

    def get_formatter(self): return self.actor.get_formatter()

    def change_health(self, value):
        result = self.actor.health + value
        self.actor.health = int(min(self.actor.health + value, self.actor.max_health))
        return int(value - (result - self.actor.health))
  
    def choose_ability(self, enemy): 
        choice_abilities = self.actor.abilities.active_abilities
        domain = 0

        for ability in choice_abilities:
            domain += ability.PRIORITY

        choice_value = random.randint(0, domain)

        choosen_ability = None

        for ability in choice_abilities:
            if choice_value <= ability.PRIORITY:
                choosen_ability = ability
                break
            choice_value -= ability.PRIORITY
            
        return choosen_ability


def make_turn(actor1, actor2, messanger):

    actor1_initiative = random.uniform(0, actor1.initiative + actor2.initiative)

    if actor1_initiative < actor1.initiative:
        return strike(actor1, actor2, messanger)
    else:
        return strike(actor2, actor1, messanger)


def strike(attacker, defender, messanger):

    attacker.context.on_own_turn()

    if attacker.context.is_stunned:
        messanger.add_message('action_battlepve1x1_battle_stun', actor=attacker)
        return

    ability = attacker.choose_ability(defender)

    if ability.LOGIC_TYPE == ABILITIES_LOGIC_TYPE.WITHOUT_CONTACT:
        strike_without_contact(ability, attacker, defender, messanger)
    elif ability.LOGIC_TYPE == ABILITIES_LOGIC_TYPE.WITH_CONTACT:
        strike_without_contact(ability, attacker, defender, messanger)


def strike_with_contact(ability, attacker, defender, messanger):

    if attacker.context.should_miss_attack():
        messanger.add_message('action_battlepve1x1_battle_miss', attacker=attacker, ability=ability, defender=defender)
        return

    ability.use(messanger, attacker, defender)

    
def strike_without_contact(ability, attacker, defender, messanger):
    ability.use(messanger, attacker, defender)
