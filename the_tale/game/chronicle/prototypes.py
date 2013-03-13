# coding: utf-8

from dext.utils.decorators import nested_commit_on_success

from common.utils.prototypes import BasePrototype

from game.prototypes import TimePrototype

from game.chronicle.models import Record, Actor, RecordToActor
from game.chronicle.exceptions import ChronicleException


class RecordPrototype(BasePrototype):
    _model_class = Record
    _readonly = ('id', 'text')

    @property
    def game_time(self):
        return TimePrototype(self._model.created_at_turn).game_time

    @classmethod
    @nested_commit_on_success
    def create(cls, record):

        model = Record.objects.create(type=record.TYPE.value,
                                      text=record.get_text(),
                                      created_at_turn=record.created_at_turn)

        prototype = cls(model)

        for role, actor in record.actors.items():
            RecordToActorPrototype.create(role, prototype, actor)

        return prototype

    @classmethod
    def get_actor_records_query(cls, external_actor_prototype):
        external_actor = create_external_actor(external_actor_prototype)
        return Record.objects.filter(actors__uid=external_actor.uid)

    @classmethod
    def get_last_actor_records(cls, external_actor_prototype, number):
        return [cls(record) for record in cls.get_actor_records_query(external_actor_prototype).order_by('-created_at')[:number]]

    @classmethod
    def get_last_records(cls, number):
        return [cls(record) for record in Record.objects.all().order_by('-created_at')[:number]]


class RecordToActorPrototype(BasePrototype):

    @classmethod
    def create(cls, role, record, external_actor):

        actor = ActorPrototype.get_by_uid(external_actor.uid)

        if actor is None:
            actor = ActorPrototype.create(external_actor)

        model = RecordToActor.objects.create(role=role.value,
                                             record=record._model,
                                             actor=actor._model)
        return cls(model)



class ExternalActorBase(object):

    def __init__(self, object):
        self.object = object
        self.bill = None
        self.place = None
        self.person = None


class ExternalBill(ExternalActorBase):

    def __init__(self, *argv, **kwargs):
        super(ExternalBill, self).__init__(*argv, **kwargs)
        self.uid = 'bill_%d' % self.object.id
        self.bill = self.object

class ExternalPlace(ExternalActorBase):

    def __init__(self, *argv, **kwargs):
        super(ExternalPlace, self).__init__(*argv, **kwargs)
        self.uid = 'place_%d' % self.object.id
        self.place = self.object

class ExternalPerson(ExternalActorBase):

    def __init__(self, *argv, **kwargs):
        super(ExternalPerson, self).__init__(*argv, **kwargs)
        self.uid = 'person_%d' % self.object.id
        self.person = self.object

def create_external_actor(actor):
    from game.bills.prototypes import BillPrototype
    from game.map.places.prototypes import PlacePrototype
    from game.persons.prototypes import PersonPrototype

    if isinstance(actor, BillPrototype): return ExternalBill(actor)
    if isinstance(actor, PersonPrototype): return ExternalPerson(actor)
    if isinstance(actor, PlacePrototype): return ExternalPlace(actor)

    raise ChronicleException('can not create external actor: unknown actor type: %r' % actor)

class ActorPrototype(BasePrototype):
    _model_class = Actor
    _get_by = ('uid',)

    @classmethod
    def create(cls, external_object):

        model = Actor.objects.create(uid=external_object.uid,
                                     bill=external_object.bill._model if external_object.bill else None,
                                     place=external_object.place._model if external_object.place else None,
                                     person=external_object.person._model if external_object.person else None)

        return cls(model)
