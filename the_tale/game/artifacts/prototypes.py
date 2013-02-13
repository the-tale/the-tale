# coding: utf-8
import random
import postmarkup

from textgen.words import Noun

from dext.utils import s11n

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
    def normalized_name(self): return (self.record.normalized_name, self.record.morph)

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
        from game.artifacts.storage import artifacts_storage

        return cls(record=artifacts_storage.get_by_uuid(data['id']),
                   power=data['power'],
                   quest=data['quest'],
                   quest_uuid=data['quest_uuid'],
                   bag_uuid=data['bag_uuid'],
                   level=data.get('level', 1))

    def ui_info(self):
        return {'type': self.type,
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


class ArtifactRecordPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def id(self): return self.model.id

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(ArtifactRecord.objects.get(id=id_))
        except ArtifactRecord.DoesNotExist:
            return None

    @property
    def editor_id(self): return self.model.editor.id if self.model.editor is not None else None

    def get_min_level(self): return self.model.min_level
    def set_min_level(self, value): self.model.min_level = value
    min_level = property(get_min_level, set_min_level)

    def get_max_level(self): return self.model.max_level
    def set_max_level(self, value): self.model.max_level = value
    max_level = property(get_max_level, set_max_level)

    def get_uuid(self): return self.model.uuid
    def set_uuid(self, value): self.model.uuid = value
    uuid = property(get_uuid, set_uuid)

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = ARTIFACT_RECORD_STATE(self.model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self.model.state = self.state.value
    state = property(get_state, set_state)

    def get_rarity(self):
        if not hasattr(self, '_rarity'):
            self._rarity = RARITY_TYPE(self.model.rarity)
        return self._rarity
    def set_rarity(self, value):
        self.rarity.update(value)
        self.model.rarity = self.rarity.value
    rarity = property(get_rarity, set_rarity)

    def get_type(self):
        if not hasattr(self, '_type'):
            self._type = ARTIFACT_TYPE(self.model.type)
        return self._type
    def set_type(self, value):
        self.type.update(value)
        self.model.type = self.type.value
    type = property(get_type, set_type)

    def get_name(self): return self.model.name
    def set_name(self, value): self.model.name = value
    name = property(get_name, set_name)

    def get_name_forms(self):
        if not hasattr(self, '_normalized_name'):
            self._name_forms = Noun.deserialize(s11n.from_json(self.model.name_forms))
        return self._name_forms
    def set_name_forms(self, word):
        self._normalized_name = word
        self.model.name = word.normalized
        self.model.name_forms = s11n.to_json(word.serialize())
    name_forms = property(get_name_forms, set_name_forms)

    def get_description(self): return self.model.description
    def set_description(self, value): self.model.description = value
    description = property(get_description, set_description)

    @property
    def description_html(self): return postmarkup.render_bbcode(self.model.description)

    def accepted_for_level(self, level): return self.min_level <= level <= self.max_level

    @property
    def is_useless(self): return self.type.is_useless

    @property
    def priority(self): return RARITY_TYPE_2_PRIORITY[self.rarity.value]


    @classmethod
    def create(cls, uuid, min_level, max_level, name, description, type_, rarity, editor=None, state=ARTIFACT_RECORD_STATE.DISABLED):

        from game.artifacts.storage import artifacts_storage

        name_forms = Noun(normalized=name,
                          forms=[name] * Noun.FORMS_NUMBER,
                          properties=(u'мр',))

        model = ArtifactRecord.objects.create(uuid=uuid,
                                              min_level=min_level,
                                              max_level=max_level,
                                              name=name,
                                              name_forms=s11n.to_json(name_forms.serialize()),
                                              description=description,
                                              type=type_,
                                              rarity=rarity,
                                              state=state,
                                              editor=editor.model if editor else None)

        artifacts_storage.update_version()

        return cls(model)

    @classmethod
    def create_random(cls, uuid, min_level=1, max_level=9999, type_=ARTIFACT_TYPE.USELESS, rarity=RARITY_TYPE.NORMAL, state=ARTIFACT_RECORD_STATE.ENABLED):
        name = u'artifact_'+uuid.lower()
        return cls.create(uuid, min_level=min_level, max_level=max_level, name=name, description='description of %s' % name, type_=type_, rarity=rarity, state=state)

    def update_by_creator(self, form, editor):
        self.name = form.c.name
        self.min_level = form.c.min_level
        self.max_level = form.c.max_level
        self.type = form.c.type
        self.rarity = form.c.rarity
        self.description = form.c.description
        self.editor = editor.model

        self.save()

    def update_by_moderator(self, form, editor):
        self.name_forms = form.c.name_forms
        self.min_level = form.c.min_level
        self.max_level = form.c.max_level
        self.type = form.c.type
        self.rarity = form.c.rarity
        self.description = form.c.description
        self.editor = editor.model

        self.uuid = form.c.uuid
        self.state = ARTIFACT_RECORD_STATE.ENABLED if form.c.approved else ARTIFACT_RECORD_STATE.DISABLED

        self.save()


    def save(self):
        from game.artifacts.storage import artifacts_storage

        self.model.save()

        artifacts_storage.update_version()
