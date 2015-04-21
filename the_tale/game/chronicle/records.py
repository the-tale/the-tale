# coding: utf-8

from the_tale.game.prototypes import TimePrototype

from the_tale.game.chronicle.relations import RECORD_TYPE, ACTOR_ROLE
from the_tale.game.chronicle.exceptions import ChronicleException
from the_tale.game.chronicle.prototypes import RecordPrototype, create_external_actor

class RecordBase(object):
    TYPE = None
    IGNORE_ACTORS_CHECK = False
    ACTORS = frozenset()
    SUBSTITUTIONS = frozenset()
    TEXGEN_ID_BASE = 'chronicle_%s'

    def __init__(self, actors, substitutions, text=None):

        self.text = text

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
        if self.text is not None:
            return self.text

        from the_tale.linguistics.logic import get_text
        text = get_text(self.textgen_id, self.substitutions)

        return text if text is not None else u''

    def create_record(self):
        return RecordPrototype.create(self)

    def __repr__(self): return '<Chronicle record for %s>' % self.TYPE.text.encode('utf-8')


# change place name
class _PlaceChangeName(RecordBase):
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL]

class PlaceChangeNameBillSuccessed(_PlaceChangeName):
    TYPE = RECORD_TYPE.PLACE_CHANGE_NAME_BILL_SUCCESSED

# change place description
class _PlaceChangeDescription(RecordBase):
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL]

class PlaceChangeDescriptionBillSuccessed(_PlaceChangeDescription):
    TYPE = RECORD_TYPE.PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED

# change place modifier
class _PlaceChangeModifier(RecordBase):
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL]

class PlaceChangeModifierBillSuccessed(_PlaceChangeModifier):
    TYPE = RECORD_TYPE.PLACE_CHANGE_MODIFIER_BILL_SUCCESSED


class PlaceLosedModifier(RecordBase):
    TYPE = RECORD_TYPE.PLACE_LOSED_MODIFIER
    ACTORS = [ACTOR_ROLE.PLACE]
    SUBSTITUTIONS = ['place', 'old_modifier']

# person moved out city
class _PersonRemove(RecordBase):
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL, ACTOR_ROLE.PERSON]

class PersonRemoveBillSuccessed(_PersonRemove):
    TYPE = RECORD_TYPE.PERSON_REMOVE_BILL_SUCCESSED


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

class BuildingCreateBillSuccessed(_BuildingBase):
    TYPE = RECORD_TYPE.BUILDING_CREATE_BILL_SUCCESSED

# building destroy
class BuildingDestroyBillSuccessed(_BuildingBase):
    TYPE = RECORD_TYPE.BUILDING_DESTROY_BILL_SUCCESSED


class BuildingDestroyedByAmortization(RecordBase):
    TYPE = RECORD_TYPE.BUILDING_DESTROYED_BY_AMORTIZATION
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.PERSON]
    SUBSTITUTIONS  = ['place', 'person']


# building renaming
class _BuildingRenamingBillBase(_BuildingBase):
    pass

class BuildingRenamingBillSuccessed(_BuildingRenamingBillBase):
    TYPE = RECORD_TYPE.BUILDING_RENAMING_BILL_SUCCESSED


# place resource exchange
class _PlaceResourceExchangeBillBase(RecordBase):
    ACTORS = [ACTOR_ROLE.BILL, ACTOR_ROLE.PLACE, ACTOR_ROLE.PLACE]

class PlaceResourceExchangeBillSuccessed(_PlaceResourceExchangeBillBase):
    TYPE = RECORD_TYPE.PLACE_RESOURCE_EXCHANGE_BILL_SUCCESSED

class PlaceResourceExchangeBillEnded(_PlaceResourceExchangeBillBase):
    TYPE = RECORD_TYPE.PLACE_RESOURCE_EXCHANGE_BILL_ENDED


# bill decline
class _BillDeclineBillBase(RecordBase):
    IGNORE_ACTORS_CHECK = True
    ACTORS = [ACTOR_ROLE.BILL, ACTOR_ROLE.BILL]

class BillDeclineSuccessed(_BillDeclineBillBase):
    TYPE = RECORD_TYPE.BILL_DECLINE_BILL_SUCCESSED


# race
class PlaceChangeRace(RecordBase):
    TYPE = RECORD_TYPE.PLACE_CHANGE_RACE
    ACTORS = [ACTOR_ROLE.PLACE]
    SUBSTITUTIONS  = ['place', 'old_race', 'new_race']


# place resource conversion
class _PlaceResourceConversionBillBase(RecordBase):
    ACTORS = [ACTOR_ROLE.BILL, ACTOR_ROLE.PLACE]

class PlaceResourceConversionBillSuccessed(_PlaceResourceConversionBillBase):
    TYPE = RECORD_TYPE.PLACE_RESOURCE_CONVERSION_BILL_SUCCESSED

class PlaceResourceConversionBillEnded(_PlaceResourceConversionBillBase):
    TYPE = RECORD_TYPE.PLACE_RESOURCE_CONVERSION_BILL_ENDED


#chronicle
class PersonChronicleBillSuccessed(RecordBase):
    TYPE = RECORD_TYPE.PERSON_CHRONICLE_BILL_SUCCESSED
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL, ACTOR_ROLE.PERSON]

class PlaceChronicleBillSuccessed(RecordBase):
    TYPE = RECORD_TYPE.PLACE_CHRONICLE_BILL_SUCCESSED
    ACTORS = [ACTOR_ROLE.PLACE, ACTOR_ROLE.BILL]


RECORDS = {}
for class_name, record_class in globals().items():
    if not isinstance(record_class, type) or not issubclass(record_class, RecordBase):
        continue
    if class_name[0] == '_':
        continue
    if record_class == RecordBase:
        continue

    RECORDS[class_name] = record_class
