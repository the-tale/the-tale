# coding: utf-8
import random

from dext.common.utils import s11n

from the_tale.common.utils import bbcode
from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.logic import random_value_by_priority
from the_tale.common.utils.decorators import lazy_property

from the_tale.linguistics import logic as linguistics_logic
from the_tale.linguistics import relations as linguistics_relations

from the_tale.game import names

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f
from the_tale.game.balance.power import Power

from the_tale.game.artifacts import exceptions
from the_tale.game.artifacts.models import ArtifactRecord
from the_tale.game.artifacts import relations
from the_tale.game.artifacts import effects


class ArtifactPrototype(object):

    __slots__ = ('record_id', 'power', 'level', 'bag_uuid', 'max_integrity', 'integrity', 'rarity')

    def __init__(self, record_id=None, power=None, bag_uuid=None, level=0, max_integrity=None, integrity=None, rarity=relations.RARITY.NORMAL):
        self.record_id = record_id
        self.power = power
        self.level = level
        self.rarity = rarity

        self.max_integrity = int(max_integrity
                                 if max_integrity is not None
                                 else rarity.max_integrity * random.uniform(1-c.ARTIFACT_MAX_INTEGRITY_DELTA, 1+c.ARTIFACT_MAX_INTEGRITY_DELTA))
        self.integrity = integrity if integrity is not None else self.max_integrity

        self.bag_uuid = bag_uuid

    @property
    def record(self):
        from the_tale.game.artifacts import storage
        return storage.artifacts_storage[self.record_id]

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
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage
        return (restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARTIFACT_TYPE, self.type.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARTIFACT_POWER_TYPE, self.record.power_type.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARTIFACT_RARITY, self.rarity.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARTIFACT_EFFECT, self._effect().TYPE.value).id,
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.ARTIFACT, self.record.id).id)

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

    def must_be_removed_on_help(self):
        return any(effect.REMOVE_ON_HELP for effect in self.all_effects())

    def is_child_gift(self):
        return any(effect.TYPE.is_CHILD_GIFT for effect in self.all_effects())

    def serialize(self):
        return {'id': self.id,
                'power': self.power.serialize(),
                'bag_uuid': self.bag_uuid,
                'integrity': (self.integrity, self.max_integrity),
                'rarity': self.rarity.value,
                'level': self.level}


    @classmethod
    def deserialize(cls, data):
        # if artifact record is desabled or deleted, get another random record
        from the_tale.game.artifacts.storage import artifacts_storage

        record = artifacts_storage.get_by_uuid(data['id'])

        if record is None or record.state.is_DISABLED:
            record = random.choice(artifacts_storage.artifacts)

        integrity = data.get('integrity', [c.ARTIFACT_MAX_INTEGRITY, c.ARTIFACT_MAX_INTEGRITY])

        return cls(record_id=record.id,
                   power=Power.deserialize(data['power']),
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

        if random_value_by_priority(choices) == 'physic':
            self.power.physic += 1
        else:
            self.power.magic += 1

        self.max_integrity -= int(self.max_integrity * c.ARTIFACT_SHARP_MAX_INTEGRITY_LOST_FRACTION)
        self.integrity = min(self.integrity, self.max_integrity)

        return True

    @property
    def integrity_fraction(self):
        if self.max_integrity == 0:
            return 0
        return float(self.integrity) / self.max_integrity

    def damage_integrity(self):
        self.integrity = max(0, self.integrity - c.ARTIFACT_INTEGRITY_DAMAGE_PER_BATTLE)

    def can_be_broken(self):
        return self.integrity < self.max_integrity * (1.0 - c.ARTIFACT_INTEGRITY_SAFE_BARRIER)

    def break_it(self):
        self.power = Power(physic=max(1, int(self.power.physic * (1 - random.uniform(*c.ARTIFACT_BREAK_POWER_FRACTIONS)) - 1)),
                           magic=max(1, int(self.power.magic * (1 - random.uniform(*c.ARTIFACT_BREAK_POWER_FRACTIONS)) - 1)) )

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
                'integrity': (self.integrity if not self.type.is_USELESS else None,
                              self.max_integrity if not self.type.is_USELESS else None),
                'rarity': self.rarity.value if not self.type.is_USELESS else None,
                'effect': effect.value,
                'special_effect': special_effect.value,
                'preference_rating': self.preference_rating(hero.preferences.archetype.power_distribution) if not self.type.is_USELESS else None,
                'power': self.power.ui_info() if not self.type.is_USELESS else None}

    def __eq__(self, other):
        return (self.record.id == other.record.id and
                self.power == other.power and
                self.level == other.level and
                self.integrity == other.integrity and
                self.max_integrity == other.max_integrity and
                self.bag_uuid == other.bag_uuid)

    NORMAL_ARTIFACT_LABEL = u'<span class="normal-artifact-label">%s</span> <span class="physic-label">%d</span> <span class="magic-label">%d</span>'
    RARE_ARTIFACT_LABEL = u'<span class="rare-artifact-label">%s</span> <span class="physic-label">%d</span> <span class="magic-label">%d</span>'
    EPIC_ARTIFACT_LABEL = u'<span class="epic-artifact-label">%s</span> <span class="physic-label">%d</span> <span class="magic-label">%d</span>'

    def html_label(self):
        if self.is_useless:
            return self.name
        if self.rarity.is_NORMAL:
            return self.NORMAL_ARTIFACT_LABEL % (self.name, self.power.physic, self.power.magic)
        if self.rarity.is_RARE:
            return self.RARE_ARTIFACT_LABEL % (self.name, self.power.physic, self.power.magic)
        if self.rarity.is_EPIC:
            return self.EPIC_ARTIFACT_LABEL % (self.name, self.power.physic, self.power.magic)


class ArtifactRecordPrototype(BasePrototype, names.ManageNameMixin):
    _model_class = ArtifactRecord
    _readonly = ('id', 'editor_id', 'mob_id')
    _bidirectional = ('level', 'uuid', 'description', 'type', 'state', 'power_type', 'rare_effect', 'epic_effect', 'special_effect')
    _get_by = ('id', )

    @lazy_property
    def data(self):
        return s11n.from_json(self._model.data)

    @property
    def description_html(self): return bbcode.render(self._model.description)

    def accepted_for_level(self, level): return self.level <= level

    @property
    def is_useless(self): return self.type.is_USELESS

    def get_mob(self):
        from the_tale.game.mobs.storage import mobs_storage
        if self._model.mob_id is None: return None
        return mobs_storage[self._model.mob_id]
    def set_mob(self, value):
        self._model.mob = value._model if value is not None else value
    mob = property(get_mob, set_mob)

    @classmethod
    def create(cls, uuid,
               level,
               utg_name,
               description,
               type_,
               power_type,
               mob=None,
               editor=None,
               state=relations.ARTIFACT_RECORD_STATE.DISABLED,
               rare_effect=relations.ARTIFACT_EFFECT.NO_EFFECT,
               epic_effect=relations.ARTIFACT_EFFECT.NO_EFFECT,
               special_effect=relations.ARTIFACT_EFFECT.NO_EFFECT):

        from the_tale.game.artifacts.storage import artifacts_storage

        model = ArtifactRecord.objects.create(uuid=uuid,
                                              level=level,
                                              name=utg_name.normal_form(),
                                              description=description,
                                              data=s11n.to_json({'name': utg_name.serialize()}),
                                              mob=mob._model if mob else None,
                                              type=type_,
                                              power_type=power_type,
                                              rare_effect=rare_effect,
                                              epic_effect=epic_effect,
                                              special_effect=special_effect,
                                              state=state,
                                              editor=editor._model if editor else None)

        prototype = cls(model)

        linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT,
                                           external_id=prototype.id,
                                           name=prototype.name)

        artifacts_storage.add_item(prototype.id, prototype)
        artifacts_storage.update_version()

        return prototype

    @classmethod
    def create_random(cls, uuid,
                      level=1,
                      mob=None,
                      type_=relations.ARTIFACT_TYPE.USELESS,
                      power_type=relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                      state=relations.ARTIFACT_RECORD_STATE.ENABLED):
        name = u'artifact_'+uuid.lower()
        utg_name = names.generator.get_test_name(name=name)
        return cls.create(uuid, level=level, utg_name=utg_name, description='description of %s' % name, mob=mob, type_=type_, power_type=power_type, state=state)

    def update_by_creator(self, form, editor):
        self.set_utg_name(form.c.name)

        self.level = form.c.level
        self.type = form.c.type
        self.power_type = form.c.power_type
        self.rare_effect = form.c.rare_effect
        self.epic_effect = form.c.epic_effect
        self.special_effect = form.c.special_effect
        self.description = form.c.description
        self.editor = editor._model
        self.mob = form.c.mob

        self.save()

    def update_by_moderator(self, form, editor=None):
        from the_tale.game.heroes import relations as heroes_relations

        if self.uuid in heroes_relations.EQUIPMENT_SLOT.index_default: # pylint: disable=E0203
            if not form.c.approved:
                raise exceptions.DisableDefaultEquipmentError(artifact=self.uuid)

        self.set_utg_name(form.c.name)

        self.level = form.c.level
        self.type = form.c.type
        self.power_type = form.c.power_type
        self.rare_effect = form.c.rare_effect
        self.epic_effect = form.c.epic_effect
        self.special_effect = form.c.special_effect
        self.description = form.c.description
        self.editor = editor._model if editor else None
        self.mob = form.c.mob

        self.state = relations.ARTIFACT_RECORD_STATE.ENABLED if form.c.approved else relations.ARTIFACT_RECORD_STATE.DISABLED

        self.save()


    def save(self):
        from the_tale.game.artifacts.storage import artifacts_storage

        if id(self) != id(artifacts_storage[self.id]):
            raise exceptions.SaveNotRegisteredArtifactError(mob=self.id)

        linguistics_logic.sync_restriction(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.ARTIFACT,
                                           external_id=self.id,
                                           name=self.name)

        self._model.data = s11n.to_json(self.data)
        self._model.save()

        artifacts_storage._update_cached_data(self)
        artifacts_storage.update_version()


    def create_artifact(self, level, power, rarity=relations.RARITY.NORMAL):
        return ArtifactPrototype(record_id=self.id,
                                 power=power,
                                 level=level,
                                 rarity=rarity)
