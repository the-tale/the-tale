# coding: utf-8
import random

from textgen.words import Noun

from dext.utils import s11n

from common.utils import bbcode
from common.utils.prototypes import BasePrototype

from game.heroes.habilities import AbilitiesPrototype

from game.balance import formulas as f
from game.game_info import ATTRIBUTES

from game.map.relations import TERRAIN

from game.heroes.habilities import ABILITIES, ABILITY_AVAILABILITY, ABILITY_TYPE

from game.artifacts.storage import artifacts_storage

from game.mobs.models import MobRecord, MOB_RECORD_STATE

class MobException(Exception): pass


class MobPrototype(object):

    def __init__(self, record=None, level=None, health=None, abilities=None):

        self.record = record
        self.level = level

        self.abilities = self._produce_abilities(record, level) if abilities is None else abilities

        self.initiative = self.abilities.modify_attribute(ATTRIBUTES.INITIATIVE, 1)
        self.health_cooficient = self.abilities.modify_attribute(ATTRIBUTES.HEALTH, 1)
        self.damage_modifier = self.abilities.modify_attribute(ATTRIBUTES.DAMAGE, 1)

        self.max_health = int(f.mob_hp_to_lvl(level) * self.health_cooficient)

        self.health = self.max_health if health is None else health

    @staticmethod
    def _produce_abilities(record, level):
        abilities = AbilitiesPrototype()
        for ability_id in record.abilities:
            abilities.add(ability_id, level=1)
        abilities.randomized_level_up(f.max_ability_points_number(level)-len(record.abilities))
        return abilities

    @property
    def id(self): return self.record.uuid

    @property
    def name(self): return self.record.name

    @property
    def normalized_name(self): return self.record.name_forms

    @property
    def health_percents(self): return float(self.health) / self.max_health

    @property
    def basic_damage(self): return f.expected_damage_to_hero_per_hit(self.level) * self.damage_modifier

    def strike_by(self, percents):
        self.health = max(0, self.health - self.max_health * percents)

    def kill(self):
        pass

    def get_loot(self): return artifacts_storage.generate_loot(self)

    def serialize(self):
        return {'level': self.level,
                'id': self.id,
                'health': self.health}

    @classmethod
    def deserialize(cls, data):
        # we do not save abilities and after load, mob can has differen abilities levels
        # if mob record is desabled or deleted, get another random record

        from game.mobs.storage import mobs_storage

        record = mobs_storage.get_by_uuid(data['id'])

        level = data['level']

        if record is None or record.state.is_disabled:
            record = random.choice(mobs_storage.get_available_mobs_list(level))

        abilities = cls._produce_abilities(record, level)

        return cls(record=record,
                   level=level,
                   health=data['health'],
                   abilities=abilities)

    def ui_info(self):
        return { 'name': self.name,
                 'health': self.health_percents }


    def __eq__(self, other):
        return (self.id == other.id and
                self.level == other.level and
                self.max_health == other.max_health and
                self.health == other.health and
                self.abilities == other.abilities)



class MobRecordPrototype(BasePrototype):
    _model_class = MobRecord
    _readonly = ('id', 'editor_id')
    _bidirectional = ('level', 'uuid', 'name', 'description')
    _get_by = ('id', )

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = MOB_RECORD_STATE(self._model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self._model.state = self.state.value
    state = property(get_state, set_state)

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

    def get_abilities_names(self):
        return sorted([ABILITIES[ability_id].NAME for ability_id in self.abilities])

    def get_terrains(self):
        if not hasattr(self, '_terrains'):
            self._terrains = frozenset(s11n.from_json(self._model.terrains))
        return self._terrains
    def set_terrains(self, value):
        self._terrains = frozenset(value)
        self._model.terrains = s11n.to_json(list(value))
    terrains = property(get_terrains, set_terrains)

    def get_terrain_names(self):
        return sorted([TERRAIN._ID_TO_TEXT[terrain_id] for terrain_id in self.terrains])

    @property
    def artifacts(self): return artifacts_storage.get_mob_artifacts(self.id)

    @property
    def loot(self): return artifacts_storage.get_mob_loot(self.id)

    @classmethod
    def create(cls, uuid, level, name, description, abilities, terrains, editor=None, state=MOB_RECORD_STATE.DISABLED, name_forms=None):

        from game.mobs.storage import mobs_storage

        if name_forms is None:
            name_forms = Noun(normalized=name,
                              forms=[name] * Noun.FORMS_NUMBER,
                              properties=(u'мр',))

        model = MobRecord.objects.create(uuid=uuid,
                                         level=level,
                                         name=name,
                                         name_forms=s11n.to_json(name_forms.serialize()),
                                         description=description,
                                         abilities=s11n.to_json(list(abilities)),
                                         terrains=s11n.to_json(list(terrains)),
                                         state=state,
                                         editor=editor._model if editor else None)

        prototype = cls(model)

        mobs_storage.add_item(prototype.id, prototype)
        mobs_storage.update_version()

        return prototype

    @classmethod
    def get_available_abilities(cls):
        return filter(lambda a: a.TYPE == ABILITY_TYPE.BATTLE and a.AVAILABILITY & ABILITY_AVAILABILITY.FOR_MONSTERS, # pylint: disable=W0110
                      ABILITIES.values())

    def create_mob(self, hero):
        return MobPrototype(record=self, level=hero.level)

    @classmethod
    def create_random(cls, uuid, level=1, abilities_number=3, terrains=TERRAIN._ALL, state=MOB_RECORD_STATE.ENABLED): # pylint: disable=W0102

        name = u'mob_'+uuid.lower()

        battle_abilities = cls.get_available_abilities()
        battle_abilities = set([a.get_id() for a in battle_abilities])

        abilities = set(['hit'])

        for i in xrange(abilities_number-1): # pylint: disable=W0612
            abilities.add(random.choice(list(battle_abilities-abilities)))

        return cls.create(uuid, level=level, name=name, description='description of %s' % name, abilities=abilities, terrains=terrains, state=state)

    def update_by_creator(self, form, editor):
        self.name = form.c.name
        self.description = form.c.description
        self.level = form.c.level
        self.terrains = form.c.terrains
        self.abilities = form.c.abilities
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
        self.editor = editor._model if editor is not None else None

        self.save()

    def save(self):
        from game.mobs.storage import mobs_storage

        self._model.save()

        mobs_storage.update_cached_data(self)
        mobs_storage.update_version()
