# coding: utf-8
import random

from dext.common.utils import s11n

from the_tale.common.utils import bbcode
from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.linguistics import logic as linguistics_logic
from the_tale.linguistics import relations as linguistics_relations

from the_tale.game import names

from the_tale.game.heroes.habilities import AbilitiesPrototype

from the_tale.game.balance import formulas as f
from the_tale.game.balance.power import Damage

from the_tale.game.map import relations as map_relations

from the_tale.game.heroes.habilities import ABILITIES, ABILITY_AVAILABILITY
from the_tale.game.heroes.relations import MODIFIERS as HERO_MODIFIERS

from the_tale.game import relations as game_relations
from the_tale.game.actions import relations as actions_relations

from the_tale.game.artifacts.storage import artifacts_storage

from the_tale.game.mobs import models
from the_tale.game.mobs import relations
from the_tale.game.mobs import exceptions


class MobException(Exception): pass


class MobPrototype(object):

    __slots__ = ('record_id', 'level', 'abilities', 'initiative', 'health_cooficient', 'damage_modifier', 'max_health', 'health', 'is_boss', 'action_type', 'terrain', '_linguistics_restrictions_constants__lazy')

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

        self.initiative = self.abilities.modify_attribute(HERO_MODIFIERS.INITIATIVE, 1)
        self.health_cooficient = self.abilities.modify_attribute(HERO_MODIFIERS.HEALTH, 1)
        self.damage_modifier = self.abilities.modify_attribute(HERO_MODIFIERS.DAMAGE, 1)

        if self.is_boss:
            self.max_health = int(f.boss_hp_to_lvl(level) * self.health_cooficient)
        else:
            self.max_health = int(f.mob_hp_to_lvl(level) * self.health_cooficient)

        self.health = self.max_health if health is None else health

        self.action_type = action_type
        self.terrain = terrain

    @property
    def record(self):
        from the_tale.game.mobs import storage
        return storage.mobs_storage[self.record_id]

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

        terrains = map_logic.get_terrain_linguistics_restrictions(self.terrain)

        return (restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.MOB_TYPE, self.record.type.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.MOB, self.record.id).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARCHETYPE, self.record.archetype.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_VERBAL, self.record.communication_verbal.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_GESTURES, self.record.communication_gestures.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMMUNICATION_TELEPATHIC, self.record.communication_telepathic.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.INTELLECT_LEVEL, self.record.intellect_level.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ACTOR, game_relations.ACTOR.MOB.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ACTION_TYPE, self.action_type.value).id) + terrains

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

        from the_tale.game.mobs.storage import mobs_storage

        record = mobs_storage.get_by_uuid(data['id'])

        level = data['level']

        if record is None or record.state.is_DISABLED:
            record = random.choice(mobs_storage.get_available_mobs_list(level))

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
        return { 'name': self.name,
                 'health': self.health_percents,
                 'is_boss': self.is_boss}


    def __eq__(self, other):
        return (self.id == other.id and
                self.level == other.level and
                self.max_health == other.max_health and
                self.health == other.health and
                self.is_boss == other.is_boss and
                self.abilities == other.abilities)



class MobRecordPrototype(BasePrototype, names.ManageNameMixin):
    _model_class = models.MobRecord
    _readonly = ('id', 'editor_id')
    _bidirectional = ('level',
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
                      'is_eatable')
    _get_by = ('id', )

    @lazy_property
    def data(self): return s11n.from_json(self._model.data)

    def get_global_action_probability(self): return self.data.get('global_action_probability', 0)
    def set_global_action_probability(self, probability): self.data['global_action_probability'] = probability
    global_action_probability = property(get_global_action_probability, set_global_action_probability)

    @property
    def description_html(self): return bbcode.render(self._model.description)

    def get_abilities(self):
        if not hasattr(self, '_abilities'):
            self._abilities = frozenset(s11n.from_json(self._model.abilities))
        return self._abilities
    def set_abilities(self, value):
        self._abilities = frozenset(value)
        self._model.abilities = s11n.to_json(list(value))
    abilities = property(get_abilities, set_abilities)

    def get_abilities_objects(self):
        return sorted([ABILITIES[ability_id] for ability_id in self.abilities])

    def get_terrains(self):
        if not hasattr(self, '_terrains'):
            self._terrains = frozenset(map_relations.TERRAIN(terrain) for terrain in s11n.from_json(self._model.terrains))
        return self._terrains
    def set_terrains(self, value):
        self._terrains = frozenset(value)
        self._model.terrains = s11n.to_json([terrain.value for terrain in value])
    terrains = property(get_terrains, set_terrains)

    def get_terrain_names(self):
        return sorted([terrain.text for terrain in self.terrains])

    @property
    def artifacts(self): return artifacts_storage.get_mob_artifacts(self.id)

    @property
    def loot(self): return artifacts_storage.get_mob_loot(self.id)

    @classmethod
    def create(cls, uuid, level, utg_name, description, abilities, terrains, type,
               archetype=game_relations.ARCHETYPE.NEUTRAL,
               editor=None,
               state=relations.MOB_RECORD_STATE.DISABLED,
               global_action_probability=0,
               communication_verbal=game_relations.COMMUNICATION_VERBAL.CAN_NOT,
               communication_gestures=game_relations.COMMUNICATION_GESTURES.CAN_NOT,
               communication_telepathic=game_relations.COMMUNICATION_TELEPATHIC.CAN_NOT,
               intellect_level=game_relations.INTELLECT_LEVEL.NONE,
               is_mercenary=True,
               is_eatable=True):

        from the_tale.game.mobs.storage import mobs_storage

        model = models.MobRecord.objects.create(uuid=uuid,
                                                level=level,
                                                name=utg_name.normal_form(),
                                                type=type,
                                                archetype=archetype,
                                                data=s11n.to_json({'name': utg_name.serialize(),
                                                                   'global_action_probability': global_action_probability}),
                                                description=description,
                                                abilities=s11n.to_json(list(abilities)),
                                                terrains=s11n.to_json([terrain.value for terrain in terrains]),
                                                state=state,
                                                editor=editor._model if editor else None,
                                                communication_verbal=communication_verbal,
                                                communication_gestures=communication_gestures,
                                                communication_telepathic=communication_telepathic,
                                                intellect_level=intellect_level,
                                                is_mercenary=is_mercenary,
                                                is_eatable=is_eatable)

        prototype = cls(model)

        linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.MOB,
                                           external_id=prototype.id,
                                           name=prototype.name)

        mobs_storage.add_item(prototype.id, prototype)
        mobs_storage.update_version()

        return prototype

    @classmethod
    def get_available_abilities(cls):
        return filter(lambda a: a.TYPE.is_BATTLE and a.AVAILABILITY.value & ABILITY_AVAILABILITY.FOR_MONSTERS.value, # pylint: disable=W0110
                      ABILITIES.values())

    def create_mob(self, hero, is_boss=False):
        return MobPrototype(record_id=self.id, level=hero.level, is_boss=is_boss)

    @classmethod
    def create_random(cls, uuid, type=game_relations.BEING_TYPE.CIVILIZED, level=1, abilities_number=3, terrains=map_relations.TERRAIN.records, state=relations.MOB_RECORD_STATE.ENABLED, global_action_probability=0, is_mercenary=True, is_eatable=True): # pylint: disable=W0102

        name = u'mob_'+uuid.lower()

        utg_name = names.generator.get_test_name(name=name)

        battle_abilities = cls.get_available_abilities()
        battle_abilities = set([a.get_id() for a in battle_abilities])

        abilities = set(['hit'])

        for i in xrange(abilities_number-1): # pylint: disable=W0612
            abilities.add(random.choice(list(battle_abilities-abilities)))

        return cls.create(uuid,
                          level=level,
                          type=type,
                          utg_name=utg_name,
                          description='description of %s' % name,
                          abilities=abilities,
                          terrains=terrains,
                          state=state,
                          global_action_probability=global_action_probability,
                          is_mercenary=is_mercenary,
                          is_eatable=is_eatable)

    def update_by_creator(self, form, editor):
        self.set_utg_name(form.c.name)

        self.description = form.c.description
        self.level = form.c.level
        self.terrains = form.c.terrains
        self.abilities = form.c.abilities
        self.type = form.c.type
        self.archetype = form.c.archetype
        self.global_action_probability = form.c.global_action_probability
        self.editor = editor._model
        self.is_mercenary = form.c.is_mercenary
        self.is_eatable = form.c.is_eatable

        self.communication_verbal = form.c.communication_verbal
        self.communication_gestures = form.c.communication_gestures
        self.communication_telepathic = form.c.communication_telepathic
        self.intellect_level = form.c.intellect_level

        self.save()

    def update_by_moderator(self, form, editor=None):
        self.set_utg_name(form.c.name)

        self.description = form.c.description
        self.level = form.c.level
        self.terrains = form.c.terrains
        self.abilities = form.c.abilities
        self.state = relations.MOB_RECORD_STATE.ENABLED if form.c.approved else relations.MOB_RECORD_STATE.DISABLED
        self.type = form.c.type
        self.archetype = form.c.archetype
        self.global_action_probability = form.c.global_action_probability
        self.editor = editor._model if editor is not None else None
        self.is_mercenary = form.c.is_mercenary
        self.is_eatable = form.c.is_eatable

        self.communication_verbal = form.c.communication_verbal
        self.communication_gestures = form.c.communication_gestures
        self.communication_telepathic = form.c.communication_telepathic
        self.intellect_level = form.c.intellect_level

        self.save()

    def save(self):
        from the_tale.game.mobs.storage import mobs_storage

        if id(self) != id(mobs_storage[self.id]):
            raise exceptions.SaveNotRegisteredMobError(mob=self.id)

        self._model.data = s11n.to_json(self.data)
        self._model.save()

        linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.MOB,
                                           external_id=self.id,
                                           name=self.name)

        mobs_storage._update_cached_data(self)
        mobs_storage.update_version()
