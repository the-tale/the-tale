
import smart_imports

smart_imports.all()


class RecordBase(object):
    TYPE = None
    IGNORE_ACTORS_CHECK = False
    ACTORS = frozenset()

    def __init__(self, actors, text=None):

        self.text = text

        self.actors = [(role, prototypes.create_external_actor(actor)) for role, actor in actors]

        if not self.IGNORE_ACTORS_CHECK and set(next(zip(*self.actors))) != set(self.ACTORS):
            raise exceptions.ChronicleException('wrong actors for chronicle record %r versus %r' % (next(zip(*self.actors)), self.ACTORS))

        self.created_at_turn = game_turn.number()

    def get_text(self):
        return self.text if self.text is not None else ''

    def create_record(self):
        return prototypes.RecordPrototype.create(self)

    def __repr__(self): return '<Chronicle record for %s>' % self.TYPE.text.encode('utf-8')


# change place name
class _PlaceChangeName(RecordBase):
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL]


class PlaceChangeNameBillSuccessed(_PlaceChangeName):
    TYPE = relations.RECORD_TYPE.PLACE_CHANGE_NAME_BILL_SUCCESSED

# change place description


class _PlaceChangeDescription(RecordBase):
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL]


class PlaceChangeDescriptionBillSuccessed(_PlaceChangeDescription):
    TYPE = relations.RECORD_TYPE.PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED

# change place modifier


class _PlaceChangeModifier(RecordBase):
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL]


class PlaceChangeModifierBillSuccessed(_PlaceChangeModifier):
    TYPE = relations.RECORD_TYPE.PLACE_CHANGE_MODIFIER_BILL_SUCCESSED

# change place race


class _PlaceChangeRace(RecordBase):
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL]


class PlaceChangeRaceBillSuccessed(_PlaceChangeRace):
    TYPE = relations.RECORD_TYPE.PLACE_CHANGE_RACE

# person move to another place


class PersonMoveBillSuccessed(RecordBase):
    TYPE = relations.RECORD_TYPE.PERSON_MOVE_TO_PLACE
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL, relations.ACTOR_ROLE.PERSON]


class PersonAddSocialConnection(RecordBase):
    TYPE = relations.RECORD_TYPE.PERSON_ADD_SOCIAL_CONNECTION
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL, relations.ACTOR_ROLE.PERSON, relations.ACTOR_ROLE.PERSON]


class PersonRemoveSocialConnection(RecordBase):
    TYPE = relations.RECORD_TYPE.PERSON_REMOVE_SOCIAL_CONNECTION
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL, relations.ACTOR_ROLE.PERSON, relations.ACTOR_ROLE.PERSON]

# building create


class _BuildingBase(RecordBase):
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL, relations.ACTOR_ROLE.PERSON]


class BuildingCreateBillSuccessed(_BuildingBase):
    TYPE = relations.RECORD_TYPE.BUILDING_CREATE_BILL_SUCCESSED

# building destroy


class BuildingDestroyBillSuccessed(_BuildingBase):
    TYPE = relations.RECORD_TYPE.BUILDING_DESTROY_BILL_SUCCESSED


# building renaming
class _BuildingRenamingBillBase(_BuildingBase):
    pass


class BuildingRenamingBillSuccessed(_BuildingRenamingBillBase):
    TYPE = relations.RECORD_TYPE.BUILDING_RENAMING_BILL_SUCCESSED


# place resource exchange
class _PlaceResourceExchangeBillBase(RecordBase):
    ACTORS = [relations.ACTOR_ROLE.BILL, relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.PLACE]


class PlaceResourceExchangeBillSuccessed(_PlaceResourceExchangeBillBase):
    TYPE = relations.RECORD_TYPE.PLACE_RESOURCE_EXCHANGE_BILL_SUCCESSED


# bill decline
class _BillDeclineBillBase(RecordBase):
    IGNORE_ACTORS_CHECK = True
    ACTORS = [relations.ACTOR_ROLE.BILL, relations.ACTOR_ROLE.BILL]


class BillDeclineSuccessed(_BillDeclineBillBase):
    TYPE = relations.RECORD_TYPE.BILL_DECLINE_BILL_SUCCESSED

# place resource conversion


class _PlaceResourceConversionBillBase(RecordBase):
    ACTORS = [relations.ACTOR_ROLE.BILL, relations.ACTOR_ROLE.PLACE]


class PlaceResourceConversionBillSuccessed(_PlaceResourceConversionBillBase):
    TYPE = relations.RECORD_TYPE.PLACE_RESOURCE_CONVERSION_BILL_SUCCESSED


# chronicle
class PersonChronicleBillSuccessed(RecordBase):
    TYPE = relations.RECORD_TYPE.PERSON_CHRONICLE_BILL_SUCCESSED
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL, relations.ACTOR_ROLE.PERSON]


class PlaceChronicleBillSuccessed(RecordBase):
    TYPE = relations.RECORD_TYPE.PLACE_CHRONICLE_BILL_SUCCESSED
    ACTORS = [relations.ACTOR_ROLE.PLACE, relations.ACTOR_ROLE.BILL]


RECORDS = {}
for class_name, record_class in list(globals().items()):
    if not isinstance(record_class, type) or not issubclass(record_class, RecordBase):
        continue
    if class_name[0] == '_':
        continue
    if record_class == RecordBase:
        continue

    RECORDS[class_name] = record_class
