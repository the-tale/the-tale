
import smart_imports

smart_imports.all()


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
        return storage.mobs[self.record_id]

    @staticmethod
    def _produce_abilities(record, level):
        abilities = heroes_abilities.AbilitiesPrototype()
        for ability_id in record.abilities:
            abilities.add(ability_id, level=1)
        abilities.randomized_mob_level_up(f.max_ability_points_number(level) - len(record.abilities))
        return abilities

    additional_abilities = ()

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
        return power.Damage(physic=raw_damage * distribution.physic, magic=raw_damage * distribution.magic)

    @property
    def mob_type(self): return self.record.type

    @property
    def is_eatable(self): return self.record.is_eatable

    @utils_decorators.lazy_property
    def linguistics_restrictions_constants(self):
        terrains = map_logic.get_terrain_linguistics_restrictions(self.terrain)

        restrictions = [linguistics_restrictions.get(self.record.type),
                        linguistics_restrictions.get_raw('MOB', self.record.id),
                        linguistics_restrictions.get(self.record.archetype),
                        linguistics_restrictions.get(self.record.communication_verbal),
                        linguistics_restrictions.get(self.record.communication_gestures),
                        linguistics_restrictions.get(self.record.communication_telepathic),
                        linguistics_restrictions.get(self.record.intellect_level),
                        linguistics_restrictions.get(game_relations.ACTOR.MOB),
                        linguistics_restrictions.get(self.action_type),
                        linguistics_restrictions.get(companions_relations.COMPANION_EXISTENCE.HAS_NO),
                        linguistics_restrictions.get(self.record.structure),
                        linguistics_restrictions.get(self.record.movement),
                        linguistics_restrictions.get(self.record.body),
                        linguistics_restrictions.get(self.record.size),
                        linguistics_restrictions.get(self.record.orientation)]

        for feature in self.record.features:
            restrictions.append(linguistics_restrictions.get(feature))

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

        record = storage.mobs.get_by_uuid(data['id'])

        level = data['level']

        if record is None or record.state.is_DISABLED:
            record = random.choice(storage.mobs.get_all_mobs_for_level(level))

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


class MobRecord(game_names.ManageNameMixin2):
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
                 'abilities',
                 'terrains',
                 'utg_name',

                 'structure',
                 'features',
                 'movement',
                 'body',
                 'size',
                 'orientation',
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
                 abilities,
                 terrains,

                 structure,
                 features,
                 movement,
                 body,
                 size,
                 orientation,
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
        self.abilities = abilities
        self.terrains = terrains

        self.structure = structure
        self.features = features
        self.movement = movement
        self.body = body
        self.size = size
        self.orientation = orientation
        self.weapons = weapons

        self.utg_name = utg_name

        if not self.weapons:
            raise exceptions.NoWeaponsError(mob_id=self.id)

    @property
    def description_html(self): return bbcode_renderers.default.render(self.description)

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
        abilities = [heroes_abilities.ABILITIES[ability_id] for ability_id in self.abilities]
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

    def meta_object(self):
        return meta_relations.Mob.create_from_object(self)
