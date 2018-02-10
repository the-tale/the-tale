
import random

from the_tale.common.utils import bbcode
from the_tale.common.utils.decorators import lazy_property

from the_tale.game import names

from the_tale.game.heroes.habilities import AbilitiesPrototype

from the_tale.game.balance import formulas as f
from the_tale.game.balance.power import Damage

from the_tale.game.map import relations as map_relations

from the_tale.game.heroes import relations as heroes_relations
from the_tale.game.heroes import habilities

from the_tale.game import relations as game_relations
from the_tale.game.actions import relations as actions_relations

from the_tale.game.artifacts import storage as artifacts_storage


class Mob(object):
    __slots__ = ('record_id',
                 'level',
                 'abilities',
                 'initiative',
                 'health_cooficient',
                 'damage_modifier',
                 'max_health',
                 'health',
                 'is_boss',
                 'action_type',
                 'terrain',
                 '_linguistics_restrictions_constants__lazy')

    def __init__(self,
                 record_id=None,
                 level=None,
                 health=None,
                 abilities=None,
                 is_boss=False,
                 action_type=actions_relations.ACTION_TYPE.BATTLE_PVE_1X1,
                 terrain=map_relations.TERRAIN.PLANE_GRASS):

        self.record_id = record_id
        self.level = level
        self.is_boss = is_boss

        self.abilities = self._produce_abilities(self.record, level) if abilities is None else abilities

        self.initiative = self.abilities.modify_attribute(heroes_relations.MODIFIERS.INITIATIVE, 1)
        self.health_cooficient = self.abilities.modify_attribute(heroes_relations.MODIFIERS.HEALTH, 1)
        self.damage_modifier = self.abilities.modify_attribute(heroes_relations.MODIFIERS.DAMAGE, 1)

        if self.is_boss:
            self.max_health = int(f.boss_hp_to_lvl(level) * self.health_cooficient)
        else:
            self.max_health = int(f.mob_hp_to_lvl(level) * self.health_cooficient)

        self.health = self.max_health if health is None else health

        self.action_type = action_type
        self.terrain = terrain

    @property
    def record(self):
        from . import storage
        return storage.mobs[self.record_id]

    @staticmethod
    def _produce_abilities(record, level):
        abilities = AbilitiesPrototype()
        for ability_id in record.abilities:
            abilities.add(ability_id, level=1)
        abilities.randomized_mob_level_up(f.max_ability_points_number(level)-len(record.abilities))
        return abilities

    additional_abilities = []

    @property
    def id(self): return self.record.uuid

    @property
    def name(self): return self.record.name

    @property
    def utg_name(self): return self.record.utg_name

    @property
    def utg_name_form(self): return self.record.utg_name_form

    def linguistics_variables(self):
        return [('weapon', random.choice(self.record.weapons))]

    @property
    def health_percents(self): return float(self.health) / self.max_health

    @property
    def basic_damage(self):
        distribution = self.record.archetype.power_distribution
        raw_damage = f.expected_damage_to_hero_per_hit(self.level) * self.damage_modifier
        return Damage(physic=raw_damage * distribution.physic, magic=raw_damage * distribution.magic)

    @property
    def mob_type(self): return self.record.type

    @property
    def is_eatable(self): return self.record.is_eatable

    @lazy_property
    def linguistics_restrictions_constants(self):
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage
        from the_tale.game.map import logic as map_logic

        from the_tale.game.companions import relations as companion_relations

        terrains = map_logic.get_terrain_linguistics_restrictions(self.terrain)

        restrictions = [restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.MOB_TYPE, self.record.type.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.MOB, self.record.id).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARCHETYPE, self.record.archetype.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_VERBAL, self.record.communication_verbal.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_GESTURES, self.record.communication_gestures.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_TELEPATHIC, self.record.communication_telepathic.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.INTELLECT_LEVEL, self.record.intellect_level.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ACTOR, game_relations.ACTOR.MOB.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ACTION_TYPE, self.action_type.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION_EXISTENCE, companion_relations.COMPANION_EXISTENCE.HAS_NO.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.BEING_STRUCTURE, self.record.structure.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.BEING_MOVEMENT, self.record.movement.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.BEING_BODY, self.record.body.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.BEING_SIZE, self.record.size.value).id]

        for feature in self.record.features:
            restrictions.append(restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.BEING_FEATURE, feature.value).id)

        restrictions.extend(terrains)

        return restrictions

    def linguistics_restrictions(self): return self.linguistics_restrictions_constants

    def damage_percents_to_health(self, percents):
        old_health = self.health
        health = max(0, self.health - self.max_health * percents)
        return old_health - health

    def kill(self):
        pass

    def serialize(self):
        return {'level': self.level,
                'id': self.id,
                'is_boss': self.is_boss,
                'health': self.health,
                'action_type': self.action_type.value,
                'terrain': self.terrain.value}

    @classmethod
    def deserialize(cls, data):
        # we do not save abilities and after load, mob can has differen abilities levels
        # if mob record is desabled or deleted, get another random record

        from . import storage

        record = storage.mobs.get_by_uuid(data['id'])

        level = data['level']

        if record is None or record.state.is_DISABLED:
            record = random.choice(storage.mobs.get_available_mobs_list(level))

        abilities = cls._produce_abilities(record, level)

        return cls(record_id=record.id,
                   level=level,
                   health=data['health'],
                   is_boss=data.get('is_boss', False),
                   abilities=abilities,
                   action_type=actions_relations.ACTION_TYPE(data['action_type']) if 'action_type' in data else actions_relations.ACTION_TYPE.BATTLE_PVE_1X1,
                   terrain=map_relations.TERRAIN(data['terrain']) if 'terrain' in data else map_relations.TERRAIN.PLANE_GRASS)

    def update_context(self, actor, enemy):
        self.abilities.update_context(actor, enemy)

    def ui_info(self):
        return {'name': self.name,
                'health': self.health_percents,
                'is_boss': self.is_boss}

    def __eq__(self, other):
        return (self.id == other.id and
                self.level == other.level and
                self.max_health == other.max_health and
                self.health == other.health and
                self.is_boss == other.is_boss and
                self.abilities == other.abilities)


class MobRecord(names.ManageNameMixin2):
    __slots__ = ('id',
                 'editor_id',
                 'level',
                 'uuid',
                 'description',
                 'state',
                 'type',
                 'archetype',
                 'communication_verbal',
                 'communication_gestures',
                 'communication_telepathic',
                 'intellect_level',
                 'is_mercenary',
                 'is_eatable',
                 'global_action_probability',
                 'abilities',
                 'terrains',
                 'utg_name',

                 'structure',
                 'features',
                 'movement',
                 'body',
                 'size',
                 'weapons',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')

    def __init__(self,
                 id,
                 editor_id,
                 level,
                 uuid,
                 description,
                 state,
                 type,
                 archetype,
                 communication_verbal,
                 communication_gestures,
                 communication_telepathic,
                 intellect_level,
                 is_mercenary,
                 is_eatable,
                 global_action_probability,
                 abilities,
                 terrains,

                 structure,
                 features,
                 movement,
                 body,
                 size,
                 weapons,

                 utg_name):
        self.id = id
        self.editor_id = editor_id
        self.level = level
        self.uuid = uuid
        self.description = description
        self.state = state
        self.type = type
        self.archetype = archetype
        self.communication_verbal = communication_verbal
        self.communication_gestures = communication_gestures
        self.communication_telepathic = communication_telepathic
        self.intellect_level = intellect_level
        self.is_mercenary = is_mercenary
        self.is_eatable = is_eatable
        self.global_action_probability = global_action_probability
        self.abilities = abilities
        self.terrains = terrains

        self.structure = structure
        self.features = features
        self.movement = movement
        self.body = body
        self.size = size
        self.weapons = weapons

        self.utg_name = utg_name

    @property
    def description_html(self): return bbcode.render(self.description)

    def features_verbose(self):
        features = [feature.verbose_text for feature in self.features]
        features.sort()
        return ', '.join(features)

    def weapons_verbose(self):
        weapons = []

        for weapon in self.weapons:
            weapons.append(weapon.verbose())

        weapons.sort()

        return weapons

    def get_abilities_objects(self):
        abilities = [habilities.ABILITIES[ability_id] for ability_id in self.abilities]
        abilities.sort(key=lambda a: a.NAME)
        return abilities

    def get_terrain_names(self):
        return sorted([terrain.text for terrain in self.terrains])

    @property
    def artifacts(self): return artifacts_storage.artifacts.get_mob_artifacts(self.id)

    @property
    def loot(self): return artifacts_storage.artifacts.get_mob_loot(self.id)

    def create_mob(self, hero, is_boss=False):
        return Mob(record_id=self.id, level=hero.level, is_boss=is_boss)
