# coding: utf-8

from django.db import transaction

from the_tale.common.utils.prototypes import BasePrototype

from the_tale.game.prototypes import TimePrototype

from the_tale.game.chronicle.models import Record, Actor, RecordToActor
from the_tale.game.chronicle import exceptions
from the_tale.game.chronicle import relations


class RecordPrototype(BasePrototype):
    _model_class = Record
    _readonly = ('id', 'text')

    @property
    def game_time(self):
        return TimePrototype(self._model.created_at_turn).game_time

    @classmethod
    @transaction.atomic
    def create(cls, record):

        model = Record.objects.create(type=record.TYPE.value,
                                      text=record.get_text(),
                                      created_at_turn=record.created_at_turn)

        prototype = cls(model)

        for role, actor in record.actors:
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
    _model_class = RecordToActor
    _readonly = ('id', 'role', 'actor_id', 'record_id')

    @classmethod
    def create(cls, role, record, external_actor):

        actor = ActorPrototype.get_by_uid(external_actor.uid)

        if actor is None:
            actor = ActorPrototype.create(external_actor)

        model = RecordToActor.objects.create(role=role.value,
                                             record=record._model,
                                             actor=actor._model)
        return cls(model)

    @classmethod
    def get_actors_for_records(cls, records):
        actors_relations = cls.from_query(cls._db_filter(record_id__in=[r.id for r in records]))

        records_to_actors = {}

        actors_ids = set()

        for relation in actors_relations:
            if relation.record_id not in records_to_actors:
                records_to_actors[relation.record_id] = []

            records_to_actors[relation.record_id].append(relation.actor_id)
            actors_ids.add(relation.actor_id)

        actors = {actor.id: actor for actor in ActorPrototype.from_query(ActorPrototype._db_filter(id__in=actors_ids))}

        records_to_actors = {record_id: [actors[actor_id] for actor_id in record_actors_ids]
                             for record_id, record_actors_ids in records_to_actors.iteritems()}

        return records_to_actors



class ExternalActorBase(object):

    def __init__(self, object): # pylint: disable=W0622
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
    from the_tale.game.bills.prototypes import BillPrototype
    from the_tale.game.map.places.prototypes import PlacePrototype
    from the_tale.game.persons.prototypes import PersonPrototype

    if isinstance(actor, BillPrototype): return ExternalBill(actor)
    if isinstance(actor, PersonPrototype): return ExternalPerson(actor)
    if isinstance(actor, PlacePrototype): return ExternalPlace(actor)

    raise exceptions.ChronicleException('can not create external actor: unknown actor type: %r' % actor)


class ActorPrototype(BasePrototype):
    _model_class = Actor
    _readonly = ('id', 'uid', 'bill_id', 'place_id', 'person_id')
    _get_by = ('uid',)

    @classmethod
    def create(cls, external_object):

        model = Actor.objects.create(uid=external_object.uid,
                                     bill=external_object.bill._model if external_object.bill else None,
                                     place=external_object.place._model if external_object.place else None,
                                     person=external_object.person._model if external_object.person else None)

        return cls(model)

    @property
    def type(self):
        if self.bill_id is not None:
            return relations.ACTOR_ROLE.BILL
        if self.place_id is not None:
            return relations.ACTOR_ROLE.PLACE
        if self.person_id is not None:
            return relations.ACTOR_ROLE.PERSON

    @property
    def name(self):
        from the_tale.game.bills.prototypes import BillPrototype
        from the_tale.game.persons.storage import persons_storage
        from the_tale.game.map.places.storage import places_storage

        if self.bill_id is not None:
            return BillPrototype.get_by_id(self.bill_id).caption
        if self.place_id is not None:
            return places_storage[self.place_id].name
        if self.person_id is not None:
            return persons_storage[self.person_id].name
