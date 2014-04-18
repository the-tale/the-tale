# coding: utf-8
import random

from textgen.words import Noun

from dext.utils import s11n

from the_tale.common.utils import bbcode
from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f
from the_tale.game.balance.power import Power


from the_tale.game.artifacts import exceptions
from the_tale.game.artifacts.models import ArtifactRecord
from the_tale.game.artifacts import relations


class ArtifactPrototype(object):

    __slots__ = ('record', 'power', 'level', 'bag_uuid', 'max_integrity', 'integrity')

    def __init__(self, record=None, power=None, bag_uuid=None, level=0, max_integrity=c.ARTIFACT_MAX_INTEGRITY, integrity=c.ARTIFACT_MAX_INTEGRITY):
        self.record = record
        self.power = power
        self.level = level

        self.max_integrity = max_integrity
        self.integrity = integrity

        self.bag_uuid = bag_uuid


    @property
    def id(self): return self.record.uuid

    @property
    def type(self): return self.record.type

    @property
    def name(self): return self.record.name

    @property
    def normalized_name(self): return self.record.name_forms

    @property
    def min_lvl(self): return self.record.min_lvl

    @property
    def max_lvl(self): return self.record.max_lvl

    @property
    def is_useless(self): return self.record.is_useless

    @property
    def can_be_equipped(self): return not self.type.is_USELESS

    def set_bag_uuid(self, uuid): self.bag_uuid = uuid

    def absolute_sell_price(self):

        if self.is_useless:
            gold_amount = 1 + int(f.normal_loot_cost_at_lvl(self.level))
        else:
            gold_amount = 1 + int(f.sell_artifact_price(self.level))

        return gold_amount


    def get_sell_price(self):
        multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
        return int(self.absolute_sell_price() * multiplier)


    def serialize(self):
        return {'id': self.id,
                'power': self.power.serialize(),
                'bag_uuid': self.bag_uuid,
                'integrity': self.integrity,
                'max_integrity': self.max_integrity,
                'level': self.level}


    @classmethod
    def deserialize(cls, data):
        # if artifact record is desabled or deleted, get another random record
        from the_tale.game.artifacts.storage import artifacts_storage

        record = artifacts_storage.get_by_uuid(data['id'])

        if record is None or record.state.is_DISABLED:
            record = random.choice(artifacts_storage.artifacts)

        return cls(record=record,
                   power=Power.deserialize(data['power']),
                   bag_uuid=data['bag_uuid'],
                   max_integrity=data.get('max_integrity', c.ARTIFACT_MAX_INTEGRITY),
                   integrity=data.get('integrity', c.ARTIFACT_MAX_INTEGRITY),
                   level=data.get('level', 1))

    @classmethod
    def _preference_rating(cls, power, distribution):
        return power.physic * distribution.physic + power.magic * distribution.magic

    def preference_rating(self, distribution):
        return self._preference_rating(self.power, distribution)

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
        self.integrity = max(0, self.integrity - 1)

    def can_be_broken(self):
        return self.integrity < self.max_integrity * (1.0 - c.ARTIFACT_INTEGRITY_SAFE_BARRIER)

    def break_it(self):
        self.power = Power(physic=max(0, int(self.power.physic * (1 - random.uniform(*c.ARTIFACT_BREAK_POWER_FRACTIONS)) - 1)),
                           magic=max(0, int(self.power.magic * (1 - random.uniform(*c.ARTIFACT_BREAK_POWER_FRACTIONS)) - 1)) )
        self.max_integrity = int(self.max_integrity * (1 - random.uniform(*c.ARTIFACT_BREAK_INTEGRITY_FRACTIONS)))
        self.integrity = min(self.integrity, self.max_integrity)

    def repair_it(self):
        self.integrity = self.max_integrity

    def ui_info(self):
        return {'type': self.type.value,
                'id': self.record.id,
                'equipped': self.can_be_equipped,
                'name': self.name,
                'integrity': self.integrity,
                'max_integrity': self.max_integrity,
                'power': self.power.ui_info()}

    def __eq__(self, other):
        return (self.record.id == other.record.id and
                self.power == other.power and
                self.level == other.level and
                self.integrity == other.integrity and
                self.max_integrity == other.max_integrity and
                self.bag_uuid == other.bag_uuid)


class ArtifactRecordPrototype(BasePrototype):
    _model_class = ArtifactRecord
    _readonly = ('id', 'editor_id', 'mob_id')
    _bidirectional = ('level', 'uuid', 'name', 'description', 'type', 'state', 'power_type')
    _get_by = ('id', )

    def get_name_forms(self):
        if not hasattr(self, '_name_forms'):
            self._name_forms = Noun.deserialize(s11n.from_json(self._model.name_forms))
        return self._name_forms
    def set_name_forms(self, word):
        self._name_forms = word
        self._model.name = word.normalized
        self._model.name_forms = s11n.to_json(word.serialize())
    name_forms = property(get_name_forms, set_name_forms)

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
    def create(cls, uuid, level, name, description, type_, power_type, mob=None, editor=None, state=relations.ARTIFACT_RECORD_STATE.DISABLED, name_forms=None):

        from the_tale.game.artifacts.storage import artifacts_storage

        if name_forms is None:
            name_forms = Noun(normalized=name,
                              forms=[name] * Noun.FORMS_NUMBER,
                              properties=(u'мр',))

        model = ArtifactRecord.objects.create(uuid=uuid,
                                              level=level,
                                              name=name,
                                              name_forms=s11n.to_json(name_forms.serialize()),
                                              description=description,
                                              mob=mob._model if mob else None,
                                              type=type_,
                                              power_type=power_type,
                                              state=state,
                                              editor=editor._model if editor else None)

        prototype = cls(model)

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
        return cls.create(uuid, level=level, name=name, description='description of %s' % name, mob=mob, type_=type_, power_type=power_type, state=state)

    def update_by_creator(self, form, editor):

        self.name = form.c.name
        self.level = form.c.level
        self.type = form.c.type
        self.power_type = form.c.power_type
        self.description = form.c.description
        self.editor = editor._model
        self.mob = form.c.mob

        self.save()

    def update_by_moderator(self, form, editor=None):
        from the_tale.game.logic import DEFAULT_HERO_EQUIPMENT

        if self.uuid in DEFAULT_HERO_EQUIPMENT._ALL: # pylint: disable=E0203
            if self.uuid != form.c.uuid:  # pylint: disable=E0203
                raise exceptions.ChangeDefaultEquipmentUIDError(old_uid=self.uuid, new_uid=form.c.uuid)
            if not form.c.approved:
                raise exceptions.DisableDefaultEquipmentError(artifact=self.uuid)

        self.name_forms = form.c.name_forms
        self.level = form.c.level
        self.type = form.c.type
        self.power_type = form.c.power_type
        self.description = form.c.description
        self.editor = editor._model if editor else None
        self.mob = form.c.mob

        self.uuid = form.c.uuid
        self.state = relations.ARTIFACT_RECORD_STATE.ENABLED if form.c.approved else relations.ARTIFACT_RECORD_STATE.DISABLED

        self.save()


    def save(self):
        from the_tale.game.artifacts.storage import artifacts_storage

        if id(self) != id(artifacts_storage[self.id]):
            raise exceptions.SaveNotRegisteredArtifactError(mob=self.id)

        self._model.save()

        artifacts_storage.update_cached_data(self)
        artifacts_storage.update_version()

    def create_artifact(self, level, power):
        return ArtifactPrototype(record=self,
                                 power=power,
                                 level=level)
