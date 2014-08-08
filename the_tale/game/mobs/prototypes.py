# coding: utf-8
import random

from textgen.words import Noun

from dext.common.utils import s11n

from the_tale.common.utils import bbcode
from the_tale.common.utils.prototypes import BasePrototype

from the_tale.game.heroes.habilities import AbilitiesPrototype

from the_tale.game.balance import formulas as f
from the_tale.game.balance.power import Damage

from the_tale.game.map.relations import TERRAIN

from the_tale.game.heroes.habilities import ABILITIES, ABILITY_AVAILABILITY
from the_tale.game.heroes.relations import MODIFIERS as HERO_MODIFIERS
from the_tale.game.heroes.relations import ARCHETYPE

from the_tale.game.artifacts.storage import artifacts_storage

from the_tale.game.mobs.models import MobRecord
from the_tale.game.mobs.relations import MOB_RECORD_STATE, MOB_TYPE
from the_tale.game.mobs import exceptions


class MobException(Exception): pass


class MobPrototype(object):

    __slots__ = ('record', 'level', 'abilities', 'initiative', 'health_cooficient', 'damage_modifier', 'max_health', 'health', 'is_boss')

    def __init__(self, record=None, level=None, health=None, abilities=None, is_boss=False):

        self.record = record
        self.level = level
        self.is_boss = is_boss

        self.abilities = self._produce_abilities(record, level) if abilities is None else abilities

        self.initiative = self.abilities.modify_attribute(HERO_MODIFIERS.INITIATIVE, 1)
        self.health_cooficient = self.abilities.modify_attribute(HERO_MODIFIERS.HEALTH, 1)
        self.damage_modifier = self.abilities.modify_attribute(HERO_MODIFIERS.DAMAGE, 1)

        if self.is_boss:
            self.max_health = int(f.boss_hp_to_lvl(level) * self.health_cooficient)
        else:
            self.max_health = int(f.mob_hp_to_lvl(level) * self.health_cooficient)

        self.health = self.max_health if health is None else health



    @staticmethod
    def _produce_abilities(record, level):
        abilities = AbilitiesPrototype()
        for ability_id in record.abilities:
            abilities.add(ability_id, level=1)
        abilities.randomized_level_up(f.max_ability_points_number(level)-len(record.abilities))
        return abilities

    additional_abilities = []

    @property
    def id(self): return self.record.uuid

    @property
    def name(self): return self.record.name

    @property
    def normalized_name(self): return self.record.name_forms

    @property
    def health_percents(self): return float(self.health) / self.max_health

    @property
    def basic_damage(self):
        distribution = self.record.archetype.power_distribution
        raw_damage = f.expected_damage_to_hero_per_hit(self.level) * self.damage_modifier
        return Damage(physic=raw_damage * distribution.physic, magic=raw_damage * distribution.magic)

    @property
    def mob_type(self): return self.record.type

    def strike_by(self, percents):
        self.health = max(0, self.health - self.max_health * percents)

    def kill(self):
        pass

    def serialize(self):
        return {'level': self.level,
                'id': self.id,
                'is_boss': self.is_boss,
                'health': self.health}

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

        return cls(record=record,
                   level=level,
                   health=data['health'],
                   is_boss=data.get('is_boss', False),
                   abilities=abilities)

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



class MobRecordPrototype(BasePrototype):
    _model_class = MobRecord
    _readonly = ('id', 'editor_id')
    _bidirectional = ('level', 'uuid', 'name', 'description', 'state', 'type', 'archetype')
    _get_by = ('id', )

    def get_name_forms(self):
        if not hasattr(self, '_normalized_name'):
            self._name_forms = Noun.deserialize(s11n.from_json(self._model.name_forms))
        return self._name_forms
    def set_name_forms(self, word):
        self._normalized_name = word
        self._model.name = word.normalized
        self._model.name_forms = s11n.to_json(word.serialize())
    name_forms = property(get_name_forms, set_name_forms)

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
            self._terrains = frozenset(TERRAIN(terrain) for terrain in s11n.from_json(self._model.terrains))
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
    def create(cls, uuid, level, name, description, abilities, terrains, type, archetype=ARCHETYPE.NEUTRAL, editor=None, state=MOB_RECORD_STATE.DISABLED, name_forms=None):

        from the_tale.game.mobs.storage import mobs_storage

        if name_forms is None:
            name_forms = Noun(normalized=name,
                              forms=[name] * Noun.FORMS_NUMBER,
                              properties=(u'мр',))

        model = MobRecord.objects.create(uuid=uuid,
                                         level=level,
                                         name=name,
                                         type=type,
                                         archetype=archetype,
                                         name_forms=s11n.to_json(name_forms.serialize()),
                                         description=description,
                                         abilities=s11n.to_json(list(abilities)),
                                         terrains=s11n.to_json([terrain.value for terrain in terrains]),
                                         state=state,
                                         editor=editor._model if editor else None)

        prototype = cls(model)

        mobs_storage.add_item(prototype.id, prototype)
        mobs_storage.update_version()

        return prototype

    @classmethod
    def get_available_abilities(cls):
        return filter(lambda a: a.TYPE.is_BATTLE and a.AVAILABILITY.value & ABILITY_AVAILABILITY.FOR_MONSTERS.value, # pylint: disable=W0110
                      ABILITIES.values())

    def create_mob(self, hero, is_boss=False):
        return MobPrototype(record=self, level=hero.level, is_boss=is_boss)

    @classmethod
    def create_random(cls, uuid, type=MOB_TYPE.CIVILIZED, level=1, abilities_number=3, terrains=TERRAIN.records, state=MOB_RECORD_STATE.ENABLED): # pylint: disable=W0102

        name = u'mob_'+uuid.lower()

        battle_abilities = cls.get_available_abilities()
        battle_abilities = set([a.get_id() for a in battle_abilities])

        abilities = set(['hit'])

        for i in xrange(abilities_number-1): # pylint: disable=W0612
            abilities.add(random.choice(list(battle_abilities-abilities)))

        return cls.create(uuid, level=level, type=type, name=name, description='description of %s' % name, abilities=abilities, terrains=terrains, state=state)

    def update_by_creator(self, form, editor):
        self.name = form.c.name
        self.description = form.c.description
        self.level = form.c.level
        self.terrains = form.c.terrains
        self.abilities = form.c.abilities
        self.type = form.c.type
        self.archetype = form.c.archetype
        self.editor = editor._model

        self.save()

    def update_by_moderator(self, form, editor=None):
        self.name_forms = form.c.name_forms
        self.description = form.c.description
        self.level = form.c.level
        self.terrains = form.c.terrains
        self.abilities = form.c.abilities
        self.uuid = form.c.uuid
        self.state = MOB_RECORD_STATE.ENABLED if form.c.approved else MOB_RECORD_STATE.DISABLED
        self.type = form.c.type
        self.archetype = form.c.archetype
        self.editor = editor._model if editor is not None else None

        self.save()

    def save(self):
        from the_tale.game.mobs.storage import mobs_storage

        if id(self) != id(mobs_storage[self.id]):
            raise exceptions.SaveNotRegisteredMobError(mob=self.id)

        self._model.save()

        mobs_storage._update_cached_data(self)
        mobs_storage.update_version()
