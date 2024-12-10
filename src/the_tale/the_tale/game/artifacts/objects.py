
import smart_imports

smart_imports.all()


class Artifact(object):

    __slots__ = ('record_id', 'power', 'level', 'bag_uuid', 'max_integrity', 'integrity', 'rarity')

    def __init__(self, record_id=None, power=None, bag_uuid=None, level=0, max_integrity=None, integrity=None, rarity=relations.RARITY.NORMAL):
        self.record_id = record_id
        self.power = power
        self.level = level
        self.rarity = rarity

        self.max_integrity = int(max_integrity
                                 if max_integrity is not None
                                 else rarity.max_integrity * random.uniform(1 - c.ARTIFACT_MAX_INTEGRITY_DELTA, 1 + c.ARTIFACT_MAX_INTEGRITY_DELTA))
        self.integrity = integrity if integrity is not None else self.max_integrity

        self.bag_uuid = bag_uuid

    @property
    def record(self):
        return storage.artifacts[self.record_id]

    @property
    def id(self): return self.record.uuid

    @property
    def type(self): return self.record.type

    @property
    def name(self): return self.record.name

    @property
    def utg_name(self): return self.record.utg_name

    @property
    def utg_name_form(self): return self.record.utg_name_form

    @property
    def min_lvl(self): return self.record.min_lvl

    @property
    def max_lvl(self): return self.record.max_lvl

    @property
    def is_useless(self): return self.record.is_useless

    @property
    def can_be_equipped(self): return not self.type.is_USELESS

    def set_bag_uuid(self, uuid): self.bag_uuid = uuid

    def linguistics_restrictions(self):
        restrictions = [linguistics_restrictions.get(self.type),
                        linguistics_restrictions.get(self.record.power_type),
                        linguistics_restrictions.get(self.rarity),
                        linguistics_restrictions.get(self._effect().TYPE),
                        linguistics_restrictions.get_raw('ARTIFACT', self.record.id),
                        linguistics_restrictions.get(self.record.weapon_type),
                        linguistics_restrictions.get(self.record.material)]

        for damage_type in self.record.weapon_type.damage_types:
            restrictions.append(linguistics_restrictions.get(damage_type))

        return restrictions

    def absolute_sell_price(self):

        if self.is_useless:
            gold_amount = 1 + int(f.normal_loot_cost_at_lvl(self.level))
        else:
            gold_amount = 1 + int(f.sell_artifact_price(self.level) * self.rarity.cost)

        return gold_amount

    def get_sell_price(self):
        return int(self.absolute_sell_price())

    def _effect(self):
        if self.rarity.is_NORMAL:
            return effects.NoEffect
        elif self.rarity.is_RARE:
            return effects.EFFECTS[self.record.rare_effect]
        elif self.rarity.is_EPIC:
            return effects.EFFECTS[self.record.epic_effect]
        else:
            raise exceptions.UnknownRarityType(type=self.rarity)

    def special_effect(self):
        return effects.EFFECTS[self.record.special_effect]

    def all_effects(self):
        return (self._effect(), self.special_effect())

    def modify_attribute(self, type_, value):
        for effect in self.all_effects():
            value = effect.modify_attribute(type_, value)
        return value

    def serialize(self):
        return {'id': self.id,
                'power': self.power.serialize(),
                'bag_uuid': self.bag_uuid,
                'integrity': (self.integrity, self.max_integrity),
                'rarity': self.rarity.value,
                'level': self.level}

    @classmethod
    def deserialize(cls, data):
        # if artifact record is disabled or deleted, get another random record
        record = storage.artifacts.get_by_uuid(data['id'])

        if record is None or record.state.is_DISABLED:
            record = random.choice([artifact for artifact in storage.artifacts.artifacts if artifact.state.is_ENABLED])

        integrity = data.get('integrity', [c.ARTIFACT_MAX_INTEGRITY, c.ARTIFACT_MAX_INTEGRITY])

        return cls(record_id=record.id,
                   power=power.Power.deserialize(data['power']),
                   bag_uuid=data['bag_uuid'],
                   integrity=integrity[0],
                   max_integrity=integrity[1],
                   rarity=relations.RARITY.index_value[data.get('rarity', relations.RARITY.NORMAL.value)],
                   level=data.get('level', 1))

    @classmethod
    def _preference_rating(cls, rarity, power, distribution):
        return (power.physic * distribution.physic + power.magic * distribution.magic) * rarity.preference_rating

    def preference_rating(self, distribution):
        return self._preference_rating(self.rarity, self.power, distribution)

    def make_better_than(self, artifact, distribution):
        while self.preference_rating(distribution) <= artifact.preference_rating(distribution):
            if random.uniform(0, 1) < distribution.physic:
                self.power.physic += 1
            else:
                self.power.magic += 1

    def sharp(self, distribution, max_power, force=False):
        choices = []

        if force or self.power.physic < max_power.physic:
            choices.append(('physic', distribution.physic))

        if force or self.power.magic < max_power.magic:
            choices.append(('magic', distribution.magic))

        if not choices:
            return False

        if utils_logic.random_value_by_priority(choices) == 'physic':
            self.power.physic += 1
        else:
            self.power.magic += 1

        max_integrity_delta = int(self.max_integrity * c.ARTIFACT_SHARP_MAX_INTEGRITY_LOST_FRACTION)

        if max_integrity_delta == 0:
            max_integrity_delta = 1

        self.max_integrity -= max_integrity_delta

        if self.max_integrity < 1:
            self.max_integrity = 1

        self.integrity = min(self.integrity, self.max_integrity)

        return True

    @property
    def integrity_fraction(self):
        if self.max_integrity == 0:
            return 0
        return float(self.integrity) / self.max_integrity

    def damage_integrity(self, delta):
        self.integrity = max(0, self.integrity - delta)

    def can_be_broken(self):
        return self.integrity < self.max_integrity * (1.0 - c.ARTIFACT_INTEGRITY_SAFE_BARRIER)

    def break_it(self):
        self.power = power.Power(physic=max(1, int(self.power.physic * (1 - random.uniform(*c.ARTIFACT_BREAK_POWER_FRACTIONS)) - 1)),
                                 magic=max(1, int(self.power.magic * (1 - random.uniform(*c.ARTIFACT_BREAK_POWER_FRACTIONS)) - 1)))

        self.max_integrity = int(self.max_integrity * (1 - random.uniform(*c.ARTIFACT_BREAK_INTEGRITY_FRACTIONS)))
        self.integrity = min(self.integrity, self.max_integrity)

    def repair_it(self):
        self.integrity = self.max_integrity

    def ui_info(self, hero):
        effect = self._effect().TYPE
        special_effect = self.special_effect().TYPE

        return {'type': self.type.value,
                'id': self.record.id,
                'equipped': self.can_be_equipped,
                'name': self.name,
                'integrity': (int(self.integrity) if not self.type.is_USELESS else None,
                              self.max_integrity if not self.type.is_USELESS else None),
                'rarity': self.rarity.value if not self.type.is_USELESS else None,
                'effect': effect.value,
                'special_effect': special_effect.value,
                'preference_rating': self.preference_rating(hero.preferences.archetype.power_distribution) if not self.type.is_USELESS else None,
                'power': self.power.ui_info() if not self.type.is_USELESS else None}

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.record.id == other.record.id and
                self.power == other.power and
                self.level == other.level and
                self.integrity == other.integrity and
                self.max_integrity == other.max_integrity and
                self.bag_uuid == other.bag_uuid)

    NORMAL_ARTIFACT_LABEL = '<span class="normal-artifact-label">%s</span> <span class="physic-label">%d</span> <span class="magic-label">%d</span>'
    RARE_ARTIFACT_LABEL = '<span class="rare-artifact-label">%s</span> <span class="physic-label">%d</span> <span class="magic-label">%d</span>'
    EPIC_ARTIFACT_LABEL = '<span class="epic-artifact-label">%s</span> <span class="physic-label">%d</span> <span class="magic-label">%d</span>'

    def html_label(self):
        if self.is_useless:
            return self.name
        if self.rarity.is_NORMAL:
            return self.NORMAL_ARTIFACT_LABEL % (self.name, self.power.physic, self.power.magic)
        if self.rarity.is_RARE:
            return self.RARE_ARTIFACT_LABEL % (self.name, self.power.physic, self.power.magic)
        if self.rarity.is_EPIC:
            return self.EPIC_ARTIFACT_LABEL % (self.name, self.power.physic, self.power.magic)


class ArtifactRecord(game_names.ManageNameMixin2):
    __slots__ = ('id',
                 'editor_id',
                 'mob_id',
                 'level',
                 'uuid',
                 'description',
                 'type',
                 'state',
                 'power_type',
                 'rare_effect',
                 'epic_effect',
                 'special_effect',
                 'utg_name',

                 'weapon_type',
                 'material',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')

    def __init__(self,
                 id,
                 editor_id,
                 mob_id,
                 level,
                 uuid,
                 description,
                 type,
                 state,
                 power_type,
                 rare_effect,
                 epic_effect,
                 special_effect,
                 utg_name,
                 weapon_type,
                 material):
        self.id = id
        self.editor_id = editor_id
        self.mob_id = mob_id
        self.level = level
        self.uuid = uuid
        self.description = description
        self.type = type
        self.state = state
        self.power_type = power_type
        self.rare_effect = rare_effect
        self.epic_effect = epic_effect
        self.special_effect = special_effect
        self.utg_name = utg_name
        self.weapon_type = weapon_type
        self.material = material

    @property
    def description_html(self): return bbcode_renderers.default.render(self.description)

    def accepted_for_level(self, level): return self.level <= level

    def damage_types_verbose(self):
        types = list(type.text for type in self.weapon_type.damage_types)
        types.sort()
        return ' / '.join(types)

    @property
    def is_useless(self): return self.type.is_USELESS

    @property
    def mob(self):
        if self.mob_id is None:
            return None

        return mobs_storage.mobs[self.mob_id]

    def create_artifact(self, level, power, rarity=relations.RARITY.NORMAL):
        return Artifact(record_id=self.id,
                        power=power,
                        level=level,
                        rarity=rarity)

    def meta_object(self):
        return meta_relations.Artifact.create_from_object(self)


class Weapon(object):
    __slots__ = ('type', 'material', 'power_type', '_restrictions')

    def __init__(self, weapon, material, power_type):
        self.type = weapon
        self.material = material
        self.power_type = power_type

        restrictions = [linguistics_restrictions.get(relations.ARTIFACT_TYPE.MAIN_HAND),
                        linguistics_restrictions.get(self.power_type),
                        linguistics_restrictions.get(relations.RARITY.NORMAL),
                        linguistics_restrictions.get(relations.ARTIFACT_EFFECT.NO_EFFECT),
                        linguistics_restrictions.get(self.type.weapon_type),
                        linguistics_restrictions.get(self.material)]

        for damage_type in self.type.weapon_type.damage_types:
            restrictions.append(linguistics_restrictions.get(damage_type))

        self._restrictions = restrictions

    @property
    def utg_name_form(self):
        return self.type.utg_name

    def linguistics_restrictions(self):
        return self._restrictions

    def serialize(self):
        return {'weapon': self.type.value,
                'material': self.material.value,
                'power_type': self.power_type.value}

    @classmethod
    def deserialize(cls, data):
        return cls(weapon=relations.STANDARD_WEAPON(data['weapon']),
                   material=tt_artifacts_relations.MATERIAL(data['material']),
                   power_type=relations.ARTIFACT_POWER_TYPE(data['power_type']))

    def verbose(self):
        return '{} (урон: {}; материал: {}; тип силы: {})'.format(self.type.text,
                                                                  ', '.join([damage_type.text for damage_type in self.type.weapon_type.damage_types]),
                                                                  self.material.text,
                                                                  self.power_type.text)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.type == other.type and
                self.material == other.material and
                self.power_type == other.power_type)

    def __ne__(self, other):
        return not self.__eq__(other)
