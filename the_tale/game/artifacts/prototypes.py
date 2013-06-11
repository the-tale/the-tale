# coding: utf-8
import random

from textgen.words import Noun

from dext.utils import s11n

from common.utils import bbcode
from common.utils.prototypes import BasePrototype

from game.balance import constants as c, formulas as f

from game.artifacts.exceptions import ArtifactsException
from game.artifacts.models import ArtifactRecord, ARTIFACT_RECORD_STATE, RARITY_TYPE, ARTIFACT_TYPE, RARITY_TYPE_2_PRIORITY


class ArtifactPrototype(object):

    def __init__(self, record=None, power=None, quest=False, quest_uuid=None, bag_uuid=None, level=0):
        self.record = record
        self.quest = quest
        self.power = power
        self.level = level

        self.quest_uuid = quest_uuid
        self.bag_uuid = bag_uuid


    @property
    def id(self): return self.record.uuid

    @property
    def type(self): return self.record.type

    @property
    def rarity(self): return self.record.rarity

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
    def can_be_equipped(self): return not self.type.is_useless

    def set_quest_uuid(self, uuid): self.quest_uuid = uuid

    def set_bag_uuid(self, uuid): self.bag_uuid = uuid

    def get_sell_price(self):

        multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)

        if self.is_useless:
            if self.rarity == RARITY_TYPE.NORMAL:
                gold_amount = 1 + int(f.normal_loot_cost_at_lvl(self.level) * multiplier)
            elif self.rarity == RARITY_TYPE.RARE:
                gold_amount = 1 + int(f.rare_loot_cost_at_lvl(self.level) * multiplier)
            elif self.rarity == RARITY_TYPE.EPIC:
                gold_amount = 1 + int(f.epic_loot_cost_at_lvl(self.level) * multiplier)
            else:
                raise ArtifactsException('unknown artifact rarity type: %s' % self)
        else:
            gold_amount = 1 + int(f.sell_artifact_price(self.level) * multiplier)

        return gold_amount

    def serialize(self):
        return {'id': self.id,
                'power': self.power,
                'quest': self.quest,
                'quest_uuid': self.quest_uuid,
                'bag_uuid': self.bag_uuid,
                'level': self.level}


    @classmethod
    def deserialize(cls, data):
        # if artifact record is desabled or deleted, get another random record
        from game.artifacts.storage import artifacts_storage

        record = artifacts_storage.get_by_uuid(data['id'])

        if record is None or record.state.is_disabled:
            record = random.choice(artifacts_storage.artifacts)

        return cls(record=record,
                   power=data['power'],
                   quest=data['quest'],
                   quest_uuid=data['quest_uuid'],
                   bag_uuid=data['bag_uuid'],
                   level=data.get('level', 1))

    def ui_info(self):
        return {'type': self.type.value,
                'equipped': self.can_be_equipped,
                'name': self.name,
                'power': self.power,
                'quest': self.quest}

    def __eq__(self, other):
        return (self.record.id == other.record.id and
                self.quest == other.quest and
                self.power == other.power and
                self.level == other.level and
                self.quest_uuid == other.quest_uuid and
                self.bag_uuid == other.bag_uuid)


class ArtifactRecordPrototype(BasePrototype):
    _model_class = ArtifactRecord
    _readonly = ('id', 'editor_id', 'mob_id')
    _bidirectional = ('level', 'uuid', 'name', 'description')
    _get_by = ('id', )

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = ARTIFACT_RECORD_STATE(self._model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self._model.state = self.state.value
    state = property(get_state, set_state)

    def get_rarity(self):
        if not hasattr(self, '_rarity'):
            self._rarity = RARITY_TYPE(self._model.rarity)
        return self._rarity
    def set_rarity(self, value):
        self.rarity.update(value)
        self._model.rarity = self.rarity.value
    rarity = property(get_rarity, set_rarity)

    def get_type(self):
        if not hasattr(self, '_type'):
            self._type = ARTIFACT_TYPE(self._model.type)
        return self._type
    def set_type(self, value):
        self.type.update(value)
        self._model.type = self.type.value
    type = property(get_type, set_type)

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

    def accepted_for_level(self, level): return self.level <= level

    @property
    def is_useless(self): return self.type.is_useless

    @property
    def priority(self): return RARITY_TYPE_2_PRIORITY[self.rarity.value]

    def get_mob(self):
        from game.mobs.storage import mobs_storage
        if self._model.mob_id is None: return None
        return mobs_storage[self._model.mob_id]
    def set_mob(self, value):
        self._model.mob = value._model if value is not None else value
    mob = property(get_mob, set_mob)

    @classmethod
    def create(cls, uuid, level, name, description, type_, rarity, mob=None, editor=None, state=ARTIFACT_RECORD_STATE.DISABLED, name_forms=None):

        from game.artifacts.storage import artifacts_storage

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
                                              rarity=rarity,
                                              state=state,
                                              editor=editor._model if editor else None)

        prototype = cls(model)

        artifacts_storage.add_item(prototype.id, prototype)
        artifacts_storage.update_version()

        return prototype

    @classmethod
    def create_random(cls, uuid, level=1, mob=None, type_=ARTIFACT_TYPE.USELESS, rarity=RARITY_TYPE.NORMAL, state=ARTIFACT_RECORD_STATE.ENABLED):
        name = u'artifact_'+uuid.lower()
        return cls.create(uuid, level=level, name=name, description='description of %s' % name, mob=mob, type_=type_, rarity=rarity, state=state)

    def update_by_creator(self, form, editor):

        self.name = form.c.name
        self.level = form.c.level
        self.type = form.c.type
        self.rarity = form.c.rarity
        self.description = form.c.description
        self.editor = editor._model
        self.mob = form.c.mob

        self.save()

    def update_by_moderator(self, form, editor=None):
        from game.logic import DEFAULT_HERO_EQUIPMENT

        if self.uuid in DEFAULT_HERO_EQUIPMENT._ALL: # pylint: disable=E0203
            if self.uuid != form.c.uuid:  # pylint: disable=E0203
                raise ArtifactsException('we can not change uuid of default hero equipment (%s - > %s)' % (self.uuid, form.c.uuid)) # pylint: disable=E0203
            if not form.c.approved:
                raise ArtifactsException('we can not disable default hero equipment (%s)' % self.uuid) # pylint: disable=E0203

        self.name_forms = form.c.name_forms
        self.level = form.c.level
        self.type = form.c.type
        self.rarity = form.c.rarity
        self.description = form.c.description
        self.editor = editor._model if editor else None
        self.mob = form.c.mob

        self.uuid = form.c.uuid
        self.state = ARTIFACT_RECORD_STATE.ENABLED if form.c.approved else ARTIFACT_RECORD_STATE.DISABLED

        self.save()


    def save(self):
        from game.artifacts.storage import artifacts_storage

        self._model.save()

        artifacts_storage.update_cached_data(self)
        artifacts_storage.update_version()

    def create_artifact(self, level, power=0, quest=False):
        return ArtifactPrototype(record=self,
                                 power=power,
                                 quest=quest,
                                 level=level)
