# coding: utf-8

import random

from common.utils.logic import random_value_by_priority

from game.actions.contexts.battle import Damage

class Actor(object):

    def __init__(self, actor, context):
        self.actor = actor
        self.context = context
        self.messages = []

    @property
    def initiative(self): return self.actor.initiative * self.context.initiative

    @property
    def name(self): return self.actor.name

    @property
    def level(self): return self.actor.level

    @property
    def normalized_name(self): return self.actor.normalized_name

    @property
    def basic_damage(self): return self.actor.basic_damage

    @property
    def health(self): return self.actor.health

    @property
    def max_health(self): return self.actor.max_health

    def change_health(self, value):
        # TODO: change for heal & kick methods?
        old_health = self.actor.health
        self.actor.health = int(max(0, min(self.actor.health + value, self.actor.max_health)))
        return int(self.actor.health - old_health)

    def choose_ability(self):
        choice_abilities = [ (ability, ability.priority) for ability in self.actor.abilities.active_abilities if ability.can_be_used(self)]
        return random_value_by_priority(choice_abilities)

    def update_context(self, enemy):
        self.actor.abilities.update_context(self, enemy)

    def process_effects(self, messanger):
        fire_damage = self.context.fire_damage
        if fire_damage:
            damage = self.context.modify_incoming_damage(Damage(magic=fire_damage))
            self.change_health(-damage.total)
            messanger.add_message('action_battlepve1x1_periodical_fire_damage', actor=self, damage=damage.total)

        poison_damage = self.context.poison_damage
        if poison_damage:
            damage = self.context.modify_incoming_damage(Damage(magic=poison_damage))
            self.change_health(-damage.total)
            messanger.add_message('action_battlepve1x1_periodical_poison_damage', actor=self, damage=damage.total)


def make_turn(actor1, actor2, messanger):

    actor1_initiative = random.uniform(0, actor1.initiative + actor2.initiative)

    if actor1_initiative < actor1.initiative:
        return strike(actor1, actor2, messanger)
    else:
        return strike(actor2, actor1, messanger)


def strike(attacker, defender, messanger):

    attacker.context.on_own_turn()
    defender.context.on_enemy_turn()

    attacker.update_context(defender)
    defender.update_context(attacker)

    attacker.process_effects(messanger)
    defender.process_effects(messanger)

    if attacker.context.is_stunned:
        messanger.add_message('action_battlepve1x1_battle_stun', actor=attacker)
        return

    ability = attacker.choose_ability()

    if ability.LOGIC_TYPE._is_WITHOUT_CONTACT:
        strike_without_contact(ability, attacker, defender, messanger)
    elif ability.LOGIC_TYPE._is_WITH_CONTACT:
        strike_with_contact(ability, attacker, defender, messanger)


def strike_with_contact(ability, attacker, defender, messanger):

    if attacker.context.should_miss_attack():
        ability.on_miss(messanger, attacker, defender)
        return

    ability.use(messanger, attacker, defender)


def strike_without_contact(ability, attacker, defender, messanger):
    ability.use(messanger, attacker, defender)
