# coding: utf-8
import time

from dext.common.utils import s11n

from the_tale.common.utils import bbcode

from the_tale.game import names

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c
from the_tale.game.balance import power as p

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.companions import relations
from the_tale.game.companions import exceptions

from the_tale.game.companions.abilities import container as abilities_container



class Companion(object):
    __slots__ = ('record_id', 'health', 'coherence', 'experience', 'healed_at', '_hero')

    def __init__(self, record_id, health, coherence, experience, healed_at, _hero=None):
        self.record_id = record_id
        self.health = health
        self.coherence = coherence
        self.experience = experience
        self.healed_at = healed_at
        self._hero = _hero

    @property
    def record(self):
        from the_tale.game.companions import storage
        return storage.companions[self.record_id]

    def serialize(self):
        return {'record': self.record_id,
                'health': self.health,
                'coherence': self.coherence,
                'experience': self.experience,
                'healed_at': self.healed_at}

    @classmethod
    def deserialize(cls, hero, data):
        obj = cls(record_id=data['record'],
                  health=int(data['health']),
                  coherence=data['coherence'],
                  experience=data['experience'],
                  healed_at=data['healed_at'],
                  _hero=hero)
        return obj

    @property
    def name(self): return self.record.name

    @property
    def type(self): return self.record.type

    @property
    def utg_name_form(self): return self.record.utg_name_form

    def linguistics_restrictions(self):
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage

        return [restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION, self.record.id),
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION_TYPE, self.record.type.value),
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION_DEDICATION, self.record.dedication.value),
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION_RARITY, self.record.rarity.value),
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARCHETYPE, self.record.archetype.value)]

    @property
    def defend_in_battle_probability(self):
        return (self.record.dedication.block_multiplier *
                self._hero.preferences.companion_dedication.block_multiplier *
                f.companions_defend_in_battle_probability(self.actual_coherence) *
                self._hero.companion_block_probability_multiplier)

    @property
    def max_health(self):
        return int(self.record.max_health * self._hero.companion_max_health_multiplier)

    def heal(self, delta):
        if delta < 0:
            raise exceptions.HealCompanionForNegativeValueError(delta=delta)
        old_health = self.health
        self.health = int(min(self.health + delta, self.max_health))
        return self.health - old_health

    @property
    def max_coherence(self):
        return self._hero.companion_max_coherence

    def hit(self):
        self.health -= self._hero.companion_damage

    def on_heal_started(self):
        self.healed_at = time.time()

    @property
    def need_heal_in_settlement(self):
        if self.health == self.max_health:
            return False

        heals_in_hour = f.companions_heal_in_hour(self.health / 2, self.max_health)

        return self.healed_at + 60*60 / heals_in_hour < time.time()


    @property
    def need_heal_in_move(self):
        if self.health == self.max_health:
            return False

        heals_in_hour = f.companions_heal_in_hour(self.health, self.max_health)

        return self.healed_at + 60*60 / heals_in_hour < time.time()


    @property
    def is_dead(self): return self.health <= 0


    def add_experience(self, value):
        value = round(self._hero.modify_attribute(heroes_relations.MODIFIERS.COHERENCE_EXPERIENCE, value))

        if self.record.type.is_LIVING:
            value *= self._hero.companion_living_coherence_speed
        elif self.record.type.is_CONSTRUCT:
            value *= self._hero.companion_construct_coherence_speed
        elif self.record.type.is_UNUSUAL:
            value *= self._hero.companion_unusual_coherence_speed

        self.experience += int(value)

        while self.experience_to_next_level <= self.experience:

            if self.coherence >= self.max_coherence:
                self.experience = min(self.experience, self.experience_to_next_level)
                return

            self.experience -= self.experience_to_next_level
            self.coherence += 1

            self._hero.reset_accessors_cache()

    @property
    def actual_coherence(self):
        return min(self.max_coherence, self.coherence)

    def modification_coherence(self, modifier):
        if modifier.is_COMPANION_MAX_COHERENCE:
            return self.coherence
        else:
            return self.actual_coherence

    def modify_attribute(self, modifier, value):
        if modifier.is_COMPANION_ABILITIES_LEVELS:
            return value

        return self.record.abilities.modify_attribute(self.modification_coherence(modifier), self._hero.companion_abilities_levels, modifier, value)

    def check_attribute(self, modifier):
        return self.record.abilities.check_attribute(self.modification_coherence(modifier), modifier)

    @property
    def experience_to_next_level(self):
        return f.companions_coherence_for_level(min(self.coherence + 1, c.COMPANIONS_MAX_COHERENCE))

    @property
    def basic_damage(self):
        distribution = self.record.archetype.power_distribution
        raw_damage = f.expected_damage_to_mob_per_hit(self._hero.level)
        return p.Damage(physic=raw_damage * distribution.physic, magic=raw_damage * distribution.magic)


    def ui_info(self):
        return {'type': self.record.id,
                'name': self.name[0].upper() + self.name[1:],
                'health': self.health,
                'max_health': self.max_health,
                'experience': self.experience,
                'experience_to_level': self.experience_to_next_level,
                'coherence': self.actual_coherence,
                'real_coherence': self.coherence}


class CompanionRecord(names.ManageNameMixin):
    __slots__ = ('id', 'state', 'data', 'type', 'max_health', 'dedication', 'archetype', 'mode', 'abilities')

    def __init__(self,
                 id,
                 state,
                 data,
                 type,
                 max_health,
                 dedication,
                 archetype,
                 mode):
        self.id = id
        self.state = state
        self.type = type
        self.max_health = max_health
        self.dedication = dedication
        self.archetype = archetype
        self.mode = mode

        self.data = data

        self.description = self.data['description']
        self.abilities = abilities_container.Container.deserialize(self.data.get('abilities', {}))


    def rarity_points(self):
        points = [(u'здоровье', float(self.max_health - 50) / 20 * 1)]

        # dedication does not affect rarity ?

        for coherence, ability in self.abilities.all_abilities:
            points.append((ability.text, ability.rarity_delta))

        return points

    @property
    def raw_rarity(self):
        return sum((points for text, points in self.rarity_points()), 0)

    @property
    def rarity(self):
        return relations.RARITY(max(0, min(4, int(round(self.raw_rarity-0.0001))-1)))

    @classmethod
    def from_model(cls, model):
        return cls(id=model.id,
                   state=model.state,
                   data=s11n.from_json(model.data),
                   type=model.type,
                   max_health=model.max_health,
                   dedication=model.dedication,
                   archetype=model.archetype,
                   mode=model.mode)

    @property
    def description_html(self): return bbcode.render(self.description)

    def __eq__(self, other):
        return all(getattr(self, field) == getattr(other, field)
                   for field in self.__slots__)
