# coding: utf-8

import random

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f


from the_tale.common.utils.logic import random_value_by_priority


class Actor(object):

    __slots__ = ('actor', 'context', 'messages')

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
    def utg_name(self): return self.actor.utg_name

    @property
    def utg_name_form(self): return self.actor.utg_name_form

    def linguistics_restrictions(self): return self.actor.linguistics_restrictions()

    @property
    def basic_damage(self): return self.actor.basic_damage

    @property
    def power(self): return self.actor.power

    @property
    def has_companion(self): return getattr(self.actor, 'companion', None) is not None

    @property
    def companion(self): return self.actor.companion

    def remove_companion(self):
        self.actor.remove_companion()

    @property
    def health(self): return self.actor.health

    @property
    def max_health(self): return self.actor.max_health

    # @property
    # def mob_type(self): return self.actor.mob_type

    def change_health(self, value):
        # TODO: change for heal & kick methods?
        old_health = self.actor.health
        self.actor.health = int(max(0, min(self.actor.health + value, self.actor.max_health)))
        return int(self.actor.health - old_health)

    def choose_ability(self):
        choice_abilities = [ (ability, ability.priority) for ability in self.actor.abilities.active_abilities if ability.can_be_used(self)]
        choice_abilities += [ (ability, ability.priority)
                              for ability in self.actor.additional_abilities
                              if ability.activation_type.is_ACTIVE and ability.can_be_used(self)]
        return random_value_by_priority(choice_abilities)

    def update_context(self, enemy):
        self.actor.update_context(self, enemy)

    def process_effects(self, messanger):
        fire_damage = self.context.fire_damage
        if fire_damage:
            damage = self.context.modify_incoming_damage(fire_damage)
            self.change_health(-damage.total)
            messanger.add_message('action_battlepve1x1_periodical_fire_damage', actor=self, damage=damage.total)

        poison_damage = self.context.poison_damage
        if poison_damage:
            damage = self.context.modify_incoming_damage(poison_damage)
            self.change_health(-damage.total)
            messanger.add_message('action_battlepve1x1_periodical_poison_damage', actor=self, damage=damage.total)


def make_turn(actor_1, actor_2, messanger):

    if actor_1.context.turn == actor_2.context.turn == 0:

        # initialize contexts on first turn
        actor_1.update_context(actor_2)
        actor_2.update_context(actor_1)

        # check first strike
        if actor_1.context.first_strike and not actor_2.context.first_strike:
            return strike(attacker=actor_1, defender=actor_2, messanger=messanger)

        if actor_2.context.first_strike and not actor_1.context.first_strike:
            return strike(attacker=actor_2, defender=actor_1, messanger=messanger)

    actor_1_initiative = random.uniform(0, actor_1.initiative + actor_2.initiative)

    if actor_1_initiative < actor_1.initiative:
        return strike(attacker=actor_1, defender=actor_2, messanger=messanger)
    else:
        return strike(attacker=actor_2, defender=actor_1, messanger=messanger)


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

    if try_companion_block(attacker, defender, messanger):
        return

    ability = attacker.choose_ability()

    if ability.LOGIC_TYPE.is_WITHOUT_CONTACT:
        strike_without_contact(ability, attacker, defender, messanger)
    elif ability.LOGIC_TYPE.is_WITH_CONTACT:
        strike_with_contact(ability, attacker, defender, messanger)

    if attacker.health <= 0 and attacker.context.can_use_last_chance():
        attacker.change_health(-attacker.health+1)
        messanger.add_message('hero_ability_last_chance', actor=attacker)

    if defender.health <= 0 and defender.context.can_use_last_chance():
        defender.change_health(-defender.health+1)
        messanger.add_message('hero_ability_last_chance', actor=defender)


def strike_with_contact(ability, attacker, defender, messanger):

    if attacker.context.should_miss_attack():
        ability.on_miss(messanger, attacker, defender)
        return

    ability.use(messanger, attacker, defender)


def strike_without_contact(ability, attacker, defender, messanger):
    ability.use(messanger, attacker, defender)


def try_companion_block(attacker, defender, messanger):

    if not defender.has_companion:
        return False

    if random.random() > f.companions_defend_in_battle_probability(defender.companion.coherence):
        return False

    if random.random() > c.COMPANIONS_WOUND_ON_DEFEND_PROBABILITY:
        messanger.add_message('companions_block', attacker=attacker, companion_owner=defender, companion=defender.companion)
        return True

    messanger.add_message('companions_wound', attacker=attacker, companion_owner=defender, companion=defender.companion)

    defender.companion.hit()

    if defender.companion.is_dead:
        messanger.add_message('companions_killed', diary=True, attacker=attacker, companion_owner=defender, companion=defender.companion)
        defender.remove_companion()

    return True
