# coding: utf-8
import random

from the_tale.game.balance import constants as c

class Damage(object):

    def __init__(self, physic=0.0, magic=0.0):
        self.physic = physic
        self.magic = magic

    @property
    def total(self): return int(round(self.physic + self.magic))

    def multiply(self, physic_multiplier=1.0, magic_multiplier=1.0):
        self.physic *= physic_multiplier
        self.magic *= magic_multiplier

    def randomize(self):
        self.physic =  self.physic * random.uniform(1-c.DAMAGE_DELTA, 1+c.DAMAGE_DELTA)
        self.magic =  self.magic * random.uniform(1-c.DAMAGE_DELTA, 1+c.DAMAGE_DELTA)

    def __repr__(self): return u'Damage(physic=%f, magic=%f)' % (self.physic, self.magic)

    def __eq__(self, other):
        return (self.physic == other.physic and
                self.magic == other.magic)


class BattleContext(object):

    __slots__ = ('ability_magic_mushroom',
                 'ability_sidestep',
                 'stun_length',
                 'crit_chance',
                 'berserk_damage_modifier',
                 'ninja',
                 'damage_queue_fire',
                 'damage_queue_poison',
                 'initiative_queue',
                 'incoming_magic_damage_modifier',
                 'incoming_physic_damage_modifier',
                 'outcoming_magic_damage_modifier',
                 'outcoming_physic_damage_modifier',
                 'pvp_advantage',
                 'pvp_advantage_used',
                 'pvp_advantage_strike_damage',
                 'first_strike',
                 'turn')

    def __init__(self):
        self.ability_magic_mushroom = []
        self.ability_sidestep = []
        self.stun_length = 0
        self.crit_chance = 0
        self.berserk_damage_modifier = 1.0
        self.ninja = 0
        self.damage_queue_fire = []
        self.damage_queue_poison = []
        self.initiative_queue = []

        self.first_strike = False

        self.incoming_magic_damage_modifier = 1.0
        self.incoming_physic_damage_modifier = 1.0

        self.outcoming_magic_damage_modifier = 1.0
        self.outcoming_physic_damage_modifier = 1.0

        self.pvp_advantage = 0
        self.pvp_advantage_used = False
        self.pvp_advantage_strike_damage = 0
        self.turn = 0

    def use_ability_magic_mushroom(self, damage_factors): self.ability_magic_mushroom = [None] + damage_factors

    def use_ability_sidestep(self, miss_probabilities): self.ability_sidestep = [None] + miss_probabilities

    def use_stun(self, stun_length): self.stun_length = max(self.stun_length, stun_length + 1)

    def use_crit_chance(self, crit_chance): self.crit_chance += crit_chance

    def use_berserk(self, damage_modifier): self.berserk_damage_modifier = damage_modifier

    def use_ninja(self, probability): self.ninja = probability

    def use_first_strike(self): self.first_strike = True

    def use_damage_queue_fire(self, damage_queue):
        self.damage_queue_fire = map(lambda queue, delta: (delta if delta else 0) + (queue if queue else 0), self.damage_queue_fire, [None]+damage_queue) # pylint: disable=W0110

    def use_damage_queue_poison(self, damage_queue):
        self.damage_queue_poison = map(lambda queue, delta: (delta if delta else 0) + (queue if queue else 0), self.damage_queue_poison, [None] + damage_queue) # pylint: disable=W0110

    def use_initiative(self, initiative_queue):
        # do not prefix [None] here, since initiative getted before on_every_turn
        self.initiative_queue = map(lambda initiative, new_initiative: (initiative or 1) * (new_initiative or 1), self.initiative_queue, initiative_queue) # pylint: disable=W0110

    def use_incoming_damage_modifier(self, physic=1.0, magic=1.0):
        self.incoming_magic_damage_modifier *= magic
        self.incoming_physic_damage_modifier *= physic

    def use_outcoming_damage_modifier(self, physic=1.0, magic=1.0):
        self.outcoming_magic_damage_modifier *= magic
        self.outcoming_physic_damage_modifier *= physic

    def use_pvp_advantage(self, advantage):
        self.pvp_advantage = min(1.0, max(-1.0, advantage))

    def use_pvp_advantage_stike_damage(self, damage):
        self.pvp_advantage_strike_damage = damage

    @property
    def is_stunned(self): return (self.stun_length > 0)

    @property
    def fire_damage(self):
        damage = int(round(self.damage_queue_fire[0] if self.damage_queue_fire else 0))
        return damage if damage else None

    @property
    def poison_damage(self):
        damage = int(round(self.damage_queue_poison[0] if self.damage_queue_poison else 0))
        return damage if damage else None

    @property
    def initiative(self):
        return self.initiative_queue[0] if self.initiative_queue else 1.0

    def should_miss_attack(self):
        miss = self.ninja
        if self.ability_sidestep:
            miss = max(miss, self.ability_sidestep[0])
        return (random.uniform(0, 1) < miss)

    def modify_outcoming_damage(self, damage):
        if self.ability_magic_mushroom:
            damage.multiply(self.ability_magic_mushroom[0], self.ability_magic_mushroom[0])
        if random.uniform(0, 1) < self.crit_chance:
            damage.multiply(c.DAMAGE_CRIT_MULTIPLIER, c.DAMAGE_CRIT_MULTIPLIER)
        damage.multiply(self.berserk_damage_modifier, self.berserk_damage_modifier)

        damage.multiply(self.outcoming_physic_damage_modifier, self.outcoming_magic_damage_modifier)

        if self.pvp_advantage > c.PVP_ADVANTAGE_BARIER:
            # make full reset of damage, since it can be really huge delta in damage with different abilities
            damage = Damage(physic=self.pvp_advantage_strike_damage/2.0, magic=self.pvp_advantage_strike_damage/2.0)
            self.pvp_advantage_used = True
        elif self.pvp_advantage > 0:
            advantage_damage_multiplier = 1 + self.pvp_advantage * c.DAMAGE_PVP_ADVANTAGE_MODIFIER
            damage.multiply(advantage_damage_multiplier, advantage_damage_multiplier)

        damage.randomize()
        return damage

    def modify_incoming_damage(self, damage):
        damage.multiply(self.incoming_physic_damage_modifier, self.incoming_magic_damage_modifier)
        return damage

    def _on_every_turn(self):
        if self.damage_queue_fire:
            self.damage_queue_fire.pop(0)
        if self.damage_queue_poison:
            self.damage_queue_poison.pop(0)
        if self.initiative_queue:
            self.initiative_queue.pop(0)

        self.ninja = 0
        self.crit_chance = 0
        self.berserk_damage_modifier = 1.0

        self.incoming_magic_damage_modifier = 1.0
        self.incoming_physic_damage_modifier = 1.0

        self.outcoming_magic_damage_modifier = 1.0
        self.outcoming_physic_damage_modifier = 1.0

        self.pvp_advantage_used = False

        self.turn += 1

    def on_own_turn(self):
        if self.ability_magic_mushroom:
            self.ability_magic_mushroom.pop(0)
        if self.ability_sidestep:
            self.ability_sidestep.pop(0)
        if self.stun_length:
            self.stun_length -= 1

        self._on_every_turn()

    def on_enemy_turn(self):
        self._on_every_turn()

    def serialize(self):
        return { 'ability_magic_mushroom': self.ability_magic_mushroom,
                 'ability_sidestep': self.ability_sidestep,
                 'stun_length': self.stun_length,
                 'crit_chance': self.crit_chance,
                 'berserk_damage_modifier': self.berserk_damage_modifier,
                 'ninja': self.ninja,
                 'damage_queue_fire': self.damage_queue_fire,
                 'damage_queue_poison': self.damage_queue_poison,
                 'initiative_queue': self.initiative_queue,
                 'incoming_magic_damage_modifier': self.incoming_magic_damage_modifier,
                 'incoming_physic_damage_modifier': self.incoming_physic_damage_modifier,
                 'outcoming_magic_damage_modifier': self.outcoming_magic_damage_modifier,
                 'outcoming_physic_damage_modifier': self.outcoming_magic_damage_modifier,

                 'pvp_advantage': self.pvp_advantage,
                 'pvp_advantage_used': self.pvp_advantage_used,
                 'pvp_advantage_strike_damage': self.pvp_advantage_strike_damage,

                 'first_strike': self.first_strike,
                 'turn': self.turn}

    @classmethod
    def deserialize(cls, data):
        context = cls()

        context.ability_magic_mushroom = data.get('ability_magic_mushroom', [])
        context.ability_sidestep = data.get('ability_sidestep', [])
        context.crit_chance = data.get('crit_chance', 0)
        context.berserk_damage_modifier = data.get('berserk_damage_modifier', 1.0)
        context.ninja = data.get('ninja', 0)
        context.damage_queue_fire = data.get('damage_queue_fire', [])
        context.damage_queue_poison = data.get('damage_queue_poison', [])
        context.initiative_queue = data.get('initiative_queue', [])

        context.incoming_magic_damage_modifier = data.get('incoming_magic_damage_modifier', 1.0)
        context.incoming_physic_damage_modifier = data.get('incoming_physic_damage_modifier', 1.0)
        context.outcoming_magic_damage_modifier = data.get('outcoming_magic_damage_modifier', 1.0)
        context.outcoming_physic_damage_modifier = data.get('outcoming_physic_damage_modifier', 1.0)

        context.pvp_advantage = data.get('pvp_advantage', 0)
        context.pvp_advantage_used = data.get('pvp_advantage_used', False)
        context.pvp_advantage_strike_damage = data.get('pvp_advantage_strike_damage', 0)

        context.first_strike = data.get('first_strike', False)
        context.turn = data.get('turn', 0)

        return context


    def __eq__(self, other):
        return (self.ability_magic_mushroom == other.ability_magic_mushroom and
                self.ability_sidestep == other.ability_sidestep and
                self.stun_length == other.stun_length and
                self.crit_chance == other.crit_chance and
                self.berserk_damage_modifier == other.berserk_damage_modifier and
                self.ninja == other.ninja and
                self.damage_queue_fire == other.damage_queue_fire and
                self.damage_queue_poison == other.damage_queue_poison and
                self.initiative_queue == other.initiative_queue and

                self.incoming_magic_damage_modifier == other.incoming_magic_damage_modifier and
                self.incoming_physic_damage_modifier == other.incoming_physic_damage_modifier and
                self.outcoming_magic_damage_modifier == other.outcoming_magic_damage_modifier and
                self.outcoming_physic_damage_modifier == other.outcoming_physic_damage_modifier and

                self.pvp_advantage == other.pvp_advantage and
                self.pvp_advantage_used == other.pvp_advantage_used and
                self.pvp_advantage_strike_damage == other.pvp_advantage_strike_damage and

                self.first_strike == other.first_strike and
                self.turn == other.turn)
