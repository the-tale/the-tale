# coding: utf-8

from game.prototypes import TimePrototype

from game.text_generation import get_text

from game.chronicle.relations import RECORD_TYPE, ACTOR_ROLE
from game.chronicle.exceptions import ChronicleException
from game.chronicle.prototypes import RecordPrototype, create_external_actor

class RecordBase(object):
    TYPE = None
    IGNORE_ACTORS_CHECK = False
    ACTORS = frozenset()
    SUBSTITUTIONS = frozenset()
    TEXGEN_ID_BASE = 'chronicle_%s'

    def __init__(self, actors, substitutions):

        self.actors = [ (role, create_external_actor(actor)) for role, actor in actors ]
        self.substitutions = substitutions

        if not self.IGNORE_ACTORS_CHECK and sorted(zip(*self.actors)[0]) != sorted(self.ACTORS):
            raise ChronicleException('wrong actors for chronicle record %r versus %r' % (zip(*self.actors)[0], self.ACTORS))
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

    def __repr__(self): return '<Chronicle record for %s>' % self.TYPE.text.encode('utf-8')


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


# building create
class _BuildingBase(RecordBase):
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL, ACTOR_ROLE.PERSON]
    SUBSTITUTIONS = ['place', 'person', 'bill']

class BuildingCreateBillStarted(_BuildingBase):
    TYPE = RECORD_TYPE.BUILDING_CREATE_BILL_STARTED

class BuildingCreateBillSuccessed(_BuildingBase):
    TYPE = RECORD_TYPE.BUILDING_CREATE_BILL_SUCCESSED

class BuildingCreateBillFailed(_BuildingBase):
    TYPE = RECORD_TYPE.BUILDING_CREATE_BILL_FAILED

# building destroy
class BuildingDestroyBillStarted(_BuildingBase):
    TYPE = RECORD_TYPE.BUILDING_DESTROY_BILL_STARTED

class BuildingDestroyBillSuccessed(_BuildingBase):
    TYPE = RECORD_TYPE.BUILDING_DESTROY_BILL_SUCCESSED

class BuildingDestroyBillFailed(_BuildingBase):
    TYPE = RECORD_TYPE.BUILDING_DESTROY_BILL_FAILED


class BuildingDestroyedByAmortization(RecordBase):
    TYPE = RECORD_TYPE.BUILDING_DESTROYED_BY_AMORTIZATION
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.PERSON]
    SUBSTITUTIONS  = ['place', 'person']


# building renaming
class _BuildingRenamingBillBase(_BuildingBase):
    SUBSTITUTIONS = _BuildingBase.SUBSTITUTIONS + ['old_name', 'new_name']

class BuildingRenamingBillStarted(_BuildingRenamingBillBase):
    TYPE = RECORD_TYPE.BUILDING_RENAMING_BILL_STARTED

class BuildingRenamingBillSuccessed(_BuildingRenamingBillBase):
    TYPE = RECORD_TYPE.BUILDING_RENAMING_BILL_SUCCESSED

class BuildingRenamingBillFailed(_BuildingRenamingBillBase):
    TYPE = RECORD_TYPE.BUILDING_RENAMING_BILL_FAILED


# place resource exchange
class _PlaceResourceExchangeBillBase(RecordBase):
    ACTORS = [ACTOR_ROLE.BILL, ACTOR_ROLE.PLACE, ACTOR_ROLE.PLACE]
    SUBSTITUTIONS = ['place_1', 'place_2', 'resource_1', 'resource_2', 'bill']

class PlaceResourceExchangeStarted(_PlaceResourceExchangeBillBase):
    TYPE = RECORD_TYPE.PLACE_RESOURCE_EXCHANGE_BILL_STARTED

class PlaceResourceExchangeSuccessed(_PlaceResourceExchangeBillBase):
    TYPE = RECORD_TYPE.PLACE_RESOURCE_EXCHANGE_BILL_SUCCESSED

class PlaceResourceExchangeFailed(_PlaceResourceExchangeBillBase):
    TYPE = RECORD_TYPE.PLACE_RESOURCE_EXCHANGE_BILL_FAILED

class PlaceResourceExchangeEnded(_PlaceResourceExchangeBillBase):
    TYPE = RECORD_TYPE.PLACE_RESOURCE_EXCHANGE_BILL_ENDED


# bill decline
class _BillDeclineBillBase(RecordBase):
    IGNORE_ACTORS_CHECK = True
    ACTORS = [ACTOR_ROLE.BILL, ACTOR_ROLE.BILL]
    SUBSTITUTIONS = ['bill', 'declined_bill']

class BillDeclineStarted(_BillDeclineBillBase):
    TYPE = RECORD_TYPE.BILL_DECLINE_BILL_STARTED

class BillDeclineSuccessed(_BillDeclineBillBase):
    TYPE = RECORD_TYPE.BILL_DECLINE_BILL_SUCCESSED

class BillDeclineFailed(_BillDeclineBillBase):
    TYPE = RECORD_TYPE.BILL_DECLINE_BILL_FAILED


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
