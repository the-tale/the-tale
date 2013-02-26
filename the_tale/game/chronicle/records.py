# coding: utf-8

from game.prototypes import TimePrototype

from game.text_generation import get_text

from game.chronicle.relations import RECORD_TYPE, ACTOR_ROLE
from game.chronicle.exceptions import ChronicleException
from game.chronicle.prototypes import RecordPrototype, create_external_actor

class RecordBase(object):
    TYPE = None
    ACTORS = frozenset()
    SUBSTITUTIONS = frozenset()
    TEXGEN_ID_BASE = 'chronicle_%s'

    def __init__(self, actors, substitutions):
        self.actors = { role:create_external_actor(actor) for role, actor in actors.items() }
        self.substitutions = substitutions

        if set(self.actors.keys()) != set(self.ACTORS):
            raise ChronicleException('wrong actors for chronicle record %r' % set(self.actors.keys()).symmetric_difference(self.ACTORS))
        if set(self.substitutions.keys()) != set(self.SUBSTITUTIONS):
            raise ChronicleException('wrong substitutions for chronicle record %r' % set(self.substitutions.keys()).symmetric_difference(self.SUBSTITUTIONS))

        self.created_at_turn = TimePrototype.get_current_turn_number()

    @property
    def textgen_id(self): return self.TEXGEN_ID_BASE  % self.TYPE.name.lower()

    def get_text(self):
        text = get_text('chronicle:get_text', self.textgen_id, self.substitutions)
        return text if text is not None else u''

    def create_record(self):
        return RecordPrototype.create(self)

    def __repr__(self): return '<Chronicle record for %s>' % RECORD_TYPE._ID_TO_STR[self.TYPE]


# change place name
class _PlaceChangeName(RecordBase):
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL]
    SUBSTITUTIONS = ['bill', 'old_name', 'new_name']

class PlaceChangeNameBillStarted(_PlaceChangeName):
    TYPE = RECORD_TYPE.PLACE_CHANGE_NAME_BILL_STARTED

class PlaceChangeNameBillSuccessed(_PlaceChangeName):
    TYPE = RECORD_TYPE.PLACE_CHANGE_NAME_BILL_SUCCESSED

class PlaceChangeNameBillFailed(_PlaceChangeName):
    TYPE = RECORD_TYPE.PLACE_CHANGE_NAME_BILL_FAILED

# change place description
class _PlaceChangeDescription(RecordBase):
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL]
    SUBSTITUTIONS = ['place', 'bill']

class PlaceChangeDescriptionBillStarted(_PlaceChangeDescription):
    TYPE = RECORD_TYPE.PLACE_CHANGE_DESCRIPTION_BILL_STARTED

class PlaceChangeDescriptionBillSuccessed(_PlaceChangeDescription):
    TYPE = RECORD_TYPE.PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED

class PlaceChangeDescriptionBillFailed(_PlaceChangeDescription):
    TYPE = RECORD_TYPE.PLACE_CHANGE_DESCRIPTION_BILL_FAILED

# change place modifier
class _PlaceChangeModifier(RecordBase):
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL]
    SUBSTITUTIONS = ['place', 'bill', 'old_modifier', 'new_modifier']

    def __init__(self, **kwargs):
        super(_PlaceChangeModifier, self).__init__(**kwargs)

        if self.substitutions['old_modifier'] is None:
            del self.substitutions['old_modifier']

    @property
    def textgen_id(self):
        if 'old_modifier' not in self.substitutions:
            return self.TEXGEN_ID_BASE  % self.TYPE.name.lower() + '_without_old_modifier'
        else:
            return self.TEXGEN_ID_BASE  % self.TYPE.name.lower() + '_with_old_modifier'

class PlaceChangeModifierBillStarted(_PlaceChangeModifier):
    TYPE = RECORD_TYPE.PLACE_CHANGE_MODIFIER_BILL_STARTED

class PlaceChangeModifierBillSuccessed(_PlaceChangeModifier):
    TYPE = RECORD_TYPE.PLACE_CHANGE_MODIFIER_BILL_SUCCESSED

class PlaceChangeModifierBillFailed(_PlaceChangeModifier):
    TYPE = RECORD_TYPE.PLACE_CHANGE_MODIFIER_BILL_FAILED

class PlaceLosedModifier(RecordBase):
    TYPE = RECORD_TYPE.PLACE_LOSED_MODIFIER
    ACTORS = [ACTOR_ROLE.PLACE]
    SUBSTITUTIONS = ['place', 'old_modifier']

# person moved out city
class _PersonRemove(RecordBase):
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL, ACTOR_ROLE.PERSON]
    SUBSTITUTIONS = ['place', 'person', 'bill']

class PersonRemoveBillStarted(_PersonRemove):
    TYPE = RECORD_TYPE.PERSON_REMOVE_BILL_STARTED

class PersonRemoveBillSuccessed(_PersonRemove):
    TYPE = RECORD_TYPE.PERSON_REMOVE_BILL_SUCCESSED

class PersonRemoveBillFailed(_PersonRemove):
    TYPE = RECORD_TYPE.PERSON_REMOVE_BILL_FAILED

class PersonLeftPlace(RecordBase):
    TYPE = RECORD_TYPE.PERSON_LEFT_PLACE
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.PERSON]
    SUBSTITUTIONS  = ['place', 'person']

class PersonArrivedToPlace(RecordBase):
    TYPE = RECORD_TYPE.PERSON_ARRIVED_TO_PLACE
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.PERSON]
    SUBSTITUTIONS  = ['place', 'person']

# race
class PlaceChangeRace(RecordBase):
    TYPE = RECORD_TYPE.PLACE_CHANGE_RACE
    ACTORS = [ACTOR_ROLE.PLACE]
    SUBSTITUTIONS  = ['place', 'old_race', 'new_race']

RECORDS = {}
for class_name, record_class in globals().items():
    if not isinstance(record_class, type) or not issubclass(record_class, RecordBase):
        continue
    if class_name[0] == '_':
        continue
    if record_class == RecordBase:
        continue

    RECORDS[class_name] = record_class
