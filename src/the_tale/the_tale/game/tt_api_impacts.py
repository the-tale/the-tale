
import uuid
import math
import time
import datetime

from rels.django import DjangoEnum

from django.conf import settings as project_settings

from tt_protocol.protocol import impacts_pb2

from the_tale.common.utils import tt_api

from . import conf


class OBJECT_TYPE(DjangoEnum):
    records = (('ACCOUNT', 0, 'игрок'),
               ('HERO', 1, 'герой'),
               ('PERSON', 2, 'мастер'),
               ('PLACE', 3, 'город'),
               ('BILL', 4, 'запись Книги Судеб'),
               ('JOB_PLACE_POSITIVE', 5, 'полезные проект города'),
               ('JOB_PLACE_NEGATIVE', 6, 'вредный проект города'),
               ('JOB_PERSON_POSITIVE', 7, 'полезный проект мастера'),
               ('JOB_PERSON_NEGATIVE', 8, 'вредный проект мастер'))


class IMPACT_TYPE(DjangoEnum):
    records = (('INNER_CIRCLE', 0, 'от ближнего круга'),
               ('OUTER_CIRCLE', 1, 'от народа'),
               ('JOB', 2, 'проекты'),
               ('FAME', 3, 'известность'))


class _Impact:
    __slots__ = ('transaction', 'actor_type', 'actor_id', 'target_type', 'target_id', 'amount', 'turn', 'time')

    def __init__(self, actor_type, actor_id, target_type, target_id, amount, turn=None, time=None, transaction=None):
        self.transaction = transaction
        self.actor_type = actor_type
        self.actor_id = actor_id
        self.target_type = target_type
        self.target_id = target_id
        self.amount = amount
        self.turn = turn
        self.time = time

    def tt_object(self):
        return impacts_pb2.Impact(actor=impacts_pb2.Object(type=self.actor_type.value, id=self.actor_id),
                                  target=impacts_pb2.Object(type=self.target_type.value, id=self.target_id),
                                  amount=int(math.ceil(self.amount)),
                                  transaction=self.transaction.hex,
                                  turn=self.turn,
                                  time=time.mktime(self.time.timetuple())+self.time.microsecond / 1000000 if self.time else None)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.transaction == other.transaction and
                self.actor_type == other.actor_type and
                self.actor_id == other.actor_id and
                self.target_type == other.target_type and
                self.target_id == other.target_id and
                self.amount == other.amount and
                self.turn == other.turn and
                self.time == other.time)

    def __ne__(self, other):
        return not self.__eq__(other)


class PowerImpact(_Impact):
    __slots__ = ('type',)

    def __init__(self, type, **kwargs):
        super().__init__(**kwargs)
        self.type = type

    def __eq__(self, other):
        return (super().__eq__(other) and
                self.type == other.type)

    @classmethod
    def from_tt_object(cls, type, tt_impact):
        return cls(type=type,
                   actor_type=OBJECT_TYPE(tt_impact.actor.type),
                   actor_id=tt_impact.actor.id,
                   target_type=OBJECT_TYPE(tt_impact.target.type),
                   target_id=tt_impact.target.id,
                   amount=tt_impact.amount,
                   transaction=uuid.UUID(tt_impact.transaction),
                   turn=tt_impact.turn,
                   time=datetime.datetime.fromtimestamp(tt_impact.time))

    @classmethod
    def hero_2_person(cls, type, hero_id, person_id, amount, turn=None, transaction=None):
        return cls(type=type,
                   actor_type=OBJECT_TYPE.HERO,
                   actor_id=hero_id,
                   target_type=OBJECT_TYPE.PERSON,
                   target_id=person_id,
                   amount=amount,
                   turn=turn,
                   transaction=transaction)

    @classmethod
    def hero_2_place(cls, type, hero_id, place_id, amount, turn=None, transaction=None):
        return cls(type=type,
                   actor_type=OBJECT_TYPE.HERO,
                   actor_id=hero_id,
                   target_type=OBJECT_TYPE.PLACE,
                   target_id=place_id,
                   amount=amount,
                   turn=turn,
                   transaction=transaction)


class TTImpacts:
    __slots__ = ('entry_point', 'impact_type')

    def __init__(self, entry_point, impact_type):
        self.entry_point = entry_point
        self.impact_type = impact_type

    def cmd_add_power_impacts(self, impacts):
        impacts = [impact.tt_object()
                   for impact in impacts
                   if impact.amount <= -1 or 1 <= impact.amount]

        if not impacts:
            return

        api_request = tt_api.sync_request if project_settings.TESTS_RUNNING else tt_api.async_request
        api_request(url=self.entry_point + 'add-impacts',
                    data=impacts_pb2.AddImpactsRequest(impacts=impacts))

    def cmd_get_last_power_impacts(self,
                                   limit,
                                   actor_type=None,
                                   actor_id=None,
                                   target_type=None,
                                   target_id=None):

        filter_type = impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('NONE')

        if actor_type is not None:
            if target_type is not None:
                filter_type = impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('BOTH')
            else:
                filter_type = impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_ACTOR')
        elif target_type is not None:
            filter_type = impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_TARGET')

        data = impacts_pb2.GetImpactsHistoryRequest(filter=filter_type,
                                                    actor=impacts_pb2.Object(type=actor_type.value if actor_type else None,
                                                                             id=actor_id),
                                                    target=impacts_pb2.Object(type=target_type.value if target_type else None,
                                                                              id=target_id),
                                                    limit=limit)

        answer = tt_api.sync_request(url=self.entry_point+'get-impacts-history',
                                     data=data,
                                     AnswerType=impacts_pb2.GetImpactsHistoryResponse)

        return [PowerImpact.from_tt_object(type=self.impact_type, tt_impact=impact) for impact in answer.impacts]

    def cmd_get_targets_impacts(self, targets):
        data = impacts_pb2.GetTargetsImpactsRequest(targets=[impacts_pb2.Object(type=target_type.value, id=target_id)
                                                             for target_type, target_id in targets])

        answer = tt_api.sync_request(url=self.entry_point + 'get-targets-impacts',
                                     data=data,
                                     AnswerType=impacts_pb2.GetTargetsImpactsResponse)

        return [PowerImpact(type=self.impact_type,
                            actor_type=None,
                            actor_id=None,
                            target_type=OBJECT_TYPE(impact.target.type),
                            target_id=impact.target.id,
                            amount=impact.amount)
                for impact in answer.impacts]

    def cmd_get_actor_impacts(self, actor_type, actor_id, target_types):
        data = impacts_pb2.GetActorImpactsRequest(actor=impacts_pb2.Object(type=actor_type.value, id=actor_id),
                                                  target_types=[target_type.value for target_type in target_types])

        answer = tt_api.sync_request(url=self.entry_point + 'get-actor-impacts',
                                     data=data,
                                     AnswerType=impacts_pb2.GetActorImpactsResponse)

        return [PowerImpact(type=self.impact_type,
                            actor_type=actor_type,
                            actor_id=actor_id,
                            target_type=OBJECT_TYPE(impact.target.type),
                            target_id=impact.target.id,
                            amount=impact.amount)
                for impact in answer.impacts]

    def cmd_get_impacters_ratings(self, targets, actor_types, limit):
        data = impacts_pb2.GetImpactersRatingsRequest(targets=[impacts_pb2.Object(type=target_type.value, id=target_id)
                                                               for target_type, target_id in targets],
                                                       actor_types=[actor_type.value for actor_type in actor_types],
                                                       limit=limit)

        answer = tt_api.sync_request(url=self.entry_point + 'get-impacters-ratings',
                                     data=data,
                                     AnswerType=impacts_pb2.GetImpactersRatingsResponse)

        ratings = {}

        for answer_rating in answer.ratings:
            target = (OBJECT_TYPE(answer_rating.target.type), answer_rating.target.id)
            rating = [PowerImpact(type=self.impact_type,
                                  actor_type=OBJECT_TYPE(record.actor.type),
                                  actor_id=record.actor.id,
                                  target_type=target[0],
                                  target_id=target[1],
                                  amount=record.amount)
                      for record in answer_rating.records]

            ratings[target] = rating

        return ratings

    def cmd_scale_impacts(self, target_types, scale):
        data = impacts_pb2.ScaleImpactsRequest(target_types=[target_type.value for target_type in target_types],
                                               scale=scale)

        tt_api.sync_request(url=self.entry_point + 'scale-impacts',
                            data=data,
                            AnswerType=impacts_pb2.ScaleImpactsResponse)

    def cmd_debug_clear_service(self):
        if not project_settings.TESTS_RUNNING:
            return

        tt_api.sync_request(url=self.entry_point + 'debug-clear-service',
                            data=impacts_pb2.DebugClearServiceRequest(),
                            AnswerType=impacts_pb2.DebugClearServiceResponse)


personal_impacts = TTImpacts(entry_point=conf.game_settings.TT_IMPACTS_PERSONAL, impact_type=IMPACT_TYPE.INNER_CIRCLE)
crowd_impacts = TTImpacts(entry_point=conf.game_settings.TT_IMPACTS_CROWD, impact_type=IMPACT_TYPE.OUTER_CIRCLE)
job_impacts = TTImpacts(entry_point=conf.game_settings.TT_IMPACTS_JOB, impact_type=IMPACT_TYPE.JOB)
fame_impacts = TTImpacts(entry_point=conf.game_settings.TT_IMPACTS_FAME, impact_type=IMPACT_TYPE.FAME)


def debug_clear_service():
    if not project_settings.TESTS_RUNNING:
        return

    personal_impacts.cmd_debug_clear_service()
    crowd_impacts.cmd_debug_clear_service()
    job_impacts.cmd_debug_clear_service()
    fame_impacts.cmd_debug_clear_service()
