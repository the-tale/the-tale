# coding: utf-8
import random
from dext.common.utils import s11n

from the_tale.common.utils import bbcode

from the_tale.game import names

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c
from the_tale.game.balance import power as p

from the_tale.game import prototypes as game_prototypes
from the_tale.game import relations as game_relations

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.companions import relations
from the_tale.game.companions import exceptions

from the_tale.game.companions.abilities import container as abilities_container



class Companion(object):
    __slots__ = ('record_id', 'health', 'coherence', 'experience', 'healed_at_turn', '_hero', '_heals_count', '_heals_wounds_count')

    def __init__(self, record_id, health, coherence, experience, healed_at_turn, _hero=None, _heals_count=0, _heals_wounds_count=0):
        self.record_id = record_id
        self.health = health
        self.coherence = coherence
        self.experience = experience
        self.healed_at_turn = healed_at_turn
        self._hero = _hero
        self._heals_count = _heals_count
        self._heals_wounds_count = _heals_wounds_count

    @property
    def record(self):
        from the_tale.game.companions import storage
        return storage.companions[self.record_id]

    def serialize(self):
        return {'record': self.record_id,
                'health': self.health,
                'coherence': self.coherence,
                'experience': self.experience,
                'healed_at_turn': self.healed_at_turn,
                '_heals_count': self._heals_count,
                '_heals_wounds_count': self._heals_wounds_count}

    @classmethod
    def deserialize(cls, data):
        obj = cls(record_id=data['record'],
                  health=int(data['health']),
                  coherence=data['coherence'],
                  experience=data['experience'],
                  healed_at_turn=data.get('healed_at_turn', 0),
                  _heals_count=data.get('_heals_count', 0),
                  _heals_wounds_count=data.get('_heals_wounds_count', 0))
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

        restrictions = [restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION, self.record.id).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ACTOR, game_relations.ACTOR.COMPANION.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION_DEDICATION, self.record.dedication.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARCHETYPE, self.record.archetype.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_VERBAL, self.record.communication_verbal.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_GESTURES, self.record.communication_gestures.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_TELEPATHIC, self.record.communication_telepathic.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.INTELLECT_LEVEL, self.record.intellect_level.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.MOB_TYPE, self.record.type.value).id ]
        if self._hero:
            terrain = self._hero.position.get_terrain()

            restrictions.extend((restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ACTION_TYPE, self._hero.actions.current_action.ui_type.value).id,
                                 restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.TERRAIN, terrain.value).id,
                                 restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.META_TERRAIN, terrain.meta_terrain.value).id,
                                 restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.META_HEIGHT, terrain.meta_height.value).id,
                                 restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.META_VEGETATION, terrain.meta_vegetation.value).id))

        return restrictions

    @property
    def defend_in_battle_probability(self):
        return (self.record.dedication.block_multiplier *
                self._hero.preferences.companion_dedication.block_multiplier *
                f.companions_defend_in_battle_probability(self.actual_coherence) *
                self._hero.companion_block_probability_multiplier)

    @property
    def max_health(self):
        return int(self.record.max_health * self._hero.companion_max_health_multiplier)

    def on_accessors_cache_changed(self):
        self.health = min(self.health, self.max_health)

    def on_settupped(self):
        self.health = self.max_health

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
        old_health = self.health

        self.health -= self._hero.companion_damage

        if random.random() < self._damage_from_heal_probability() / (self._damage_from_heal_probability() + self._hero.companion_damage_probability):
            self._heals_wounds_count += float(c.COMPANIONS_DAMAGE_PER_WOUND) / c.COMPANIONS_HEALTH_PER_HEAL

        return old_health - self.health

    def on_heal_started(self):
        self.healed_at_turn = game_prototypes.TimePrototype.get_current_turn_number()
        self._heals_count += 1

    def _damage_from_heal_probability(self):
        return ( c.COMPANIONS_WOUNDS_IN_HOUR_FROM_HEAL /
                 ( c.BATTLES_PER_HOUR * (c.BATTLE_LENGTH / 2) * self.defend_in_battle_probability ) )

    @property
    def damage_from_heal_probability(self):

        if self._hero.companion_heal_disabled():
            return self._damage_from_heal_probability()

        if self._heals_count < self._heals_wounds_count:
            return 0

        return self._damage_from_heal_probability() * 2

    @property
    def need_heal(self):
        if self.health == self.max_health:
            return False

        return self.healed_at_turn + c.TURNS_IN_HOUR / c.COMPANIONS_HEALS_IN_HOUR <= game_prototypes.TimePrototype.get_current_turn_number()

    @property
    def is_dead(self): return self.health <= 0


    def add_experience(self, value):
        value = round(self._hero.modify_attribute(heroes_relations.MODIFIERS.COHERENCE_EXPERIENCE, value))

        value *= self._hero.companion_coherence_speed

        self.experience += int(value)

        while self.experience_to_next_level <= self.experience:

            if self.coherence >= self.max_coherence:
                self.experience = min(self.experience, self.experience_to_next_level - 1)
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
    __slots__ = ('id',
                 'state',
                 'data',
                 'type',
                 'max_health',
                 'dedication',
                 'archetype',
                 'mode',
                 'abilities',
                 'communication_verbal',
                 'communication_gestures',
                 'communication_telepathic',
                 'intellect_level')

    def __init__(self,
                 id,
                 state,
                 data,
                 type,
                 max_health,
                 dedication,
                 archetype,
                 mode,
                 communication_verbal,
                 communication_gestures,
                 communication_telepathic,
                 intellect_level):
        self.id = id
        self.state = state
        self.type = type
        self.max_health = max_health
        self.dedication = dedication
        self.archetype = archetype
        self.mode = mode

        self.communication_verbal = communication_verbal
        self.communication_gestures = communication_gestures
        self.communication_telepathic = communication_telepathic
        self.intellect_level = intellect_level

        self.data = data

        self.description = self.data['description']
        self.abilities = abilities_container.Container.deserialize(self.data.get('abilities', {}))


    def rarity_points(self):
        points = [(u'здоровье', float(self.max_health - c.COMPANIONS_MEDIUM_HEALTH) / (c.COMPANIONS_MEDIUM_HEALTH - c.COMPANIONS_MIN_HEALTH) * 1)]

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
                   mode=model.mode,
                   communication_verbal=model.communication_verbal,
                   communication_gestures=model.communication_gestures,
                   communication_telepathic=model.communication_telepathic,
                   intellect_level=model.intellect_level)

    @property
    def description_html(self): return bbcode.render(self.description)

    def __eq__(self, other):
        return all(getattr(self, field) == getattr(other, field)
                   for field in self.__slots__)
