import smart_imports

smart_imports.all()


class OBJECT_TYPE(rels_django.DjangoEnum):
    records = (('ACCOUNT', 0, 'игрок'),
               ('HERO', 1, 'герой'),
               ('PERSON', 2, 'мастер'),
               ('PLACE', 3, 'город'),
               ('BILL', 4, 'запись Книги Судеб'),
               ('JOB_PLACE_POSITIVE', 5, 'полезные проект города'),
               ('JOB_PLACE_NEGATIVE', 6, 'вредный проект города'),
               ('JOB_PERSON_POSITIVE', 7, 'полезный проект мастера'),
               ('JOB_PERSON_NEGATIVE', 8, 'вредный проект мастера'),
               ('EMISSARY', 9, 'эмиссар'))


class Impact:
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
        return tt_protocol_impacts_pb2.Impact(actor=tt_protocol_impacts_pb2.Object(type=self.actor_type.value, id=self.actor_id),
                                              target=tt_protocol_impacts_pb2.Object(type=self.target_type.value, id=self.target_id),
                                              amount=int(math.ceil(self.amount)),
                                              transaction=self.transaction.hex,
                                              turn=self.turn,
                                              time=time.mktime(self.time.timetuple()) + self.time.microsecond / 1000000 if self.time else None)

    @classmethod
    def from_tt_object(cls, type, tt_impact):
        raise NotImplementedError

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


class Client(client.Client):
    __slots__ = ('impact_type', 'impact_class')

    def __init__(self, impact_type, impact_class, **kwargs):
        super().__init__(**kwargs)
        self.impact_type = impact_type
        self.impact_class = impact_class

    def cmd_add_power_impacts(self, impacts):
        impacts = [impact.tt_object()
                   for impact in impacts
                   if impact.amount <= -1 or 1 <= impact.amount]

        if not impacts:
            return

        operations.async_request(url=self.url('add-impacts'),
                                 data=tt_protocol_impacts_pb2.AddImpactsRequest(impacts=impacts))

    def cmd_get_last_power_impacts(self,
                                   limit,
                                   actor_type=None,
                                   actor_id=None,
                                   target_type=None,
                                   target_id=None):

        filter_type = tt_protocol_impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('NONE')

        if actor_type is not None:
            if target_type is not None:
                filter_type = tt_protocol_impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('BOTH')
            else:
                filter_type = tt_protocol_impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_ACTOR')
        elif target_type is not None:
            filter_type = tt_protocol_impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_TARGET')

        data = tt_protocol_impacts_pb2.GetImpactsHistoryRequest(filter=filter_type,
                                                                actor=tt_protocol_impacts_pb2.Object(type=actor_type.value if actor_type else None,
                                                                                                     id=actor_id),
                                                                target=tt_protocol_impacts_pb2.Object(type=target_type.value if target_type else None,
                                                                                                      id=target_id),
                                                                limit=limit)

        answer = operations.sync_request(url=self.url('get-impacts-history'),
                                         data=data,
                                         AnswerType=tt_protocol_impacts_pb2.GetImpactsHistoryResponse)

        return [self.impact_class.from_tt_object(type=self.impact_type, tt_impact=impact) for impact in answer.impacts]

    def cmd_get_targets_impacts(self, targets):
        data = tt_protocol_impacts_pb2.GetTargetsImpactsRequest(targets=[tt_protocol_impacts_pb2.Object(type=target_type.value,
                                                                                                        id=target_id)
                                                                         for target_type, target_id in targets])

        answer = operations.sync_request(url=self.url('get-targets-impacts'),
                                         data=data,
                                         AnswerType=tt_protocol_impacts_pb2.GetTargetsImpactsResponse)

        return [self.impact_class(type=self.impact_type,
                                  actor_type=None,
                                  actor_id=None,
                                  target_type=OBJECT_TYPE(impact.target.type),
                                  target_id=impact.target.id,
                                  amount=impact.amount)
                for impact in answer.impacts]

    def cmd_get_actor_impacts(self, actor_type, actor_id, target_types):
        data = tt_protocol_impacts_pb2.GetActorImpactsRequest(actor=tt_protocol_impacts_pb2.Object(type=actor_type.value, id=actor_id),
                                                              target_types=[target_type.value for target_type in target_types])

        answer = operations.sync_request(url=self.url('get-actor-impacts'),
                                         data=data,
                                         AnswerType=tt_protocol_impacts_pb2.GetActorImpactsResponse)

        return [self.impact_class(type=self.impact_type,
                                  actor_type=actor_type,
                                  actor_id=actor_id,
                                  target_type=OBJECT_TYPE(impact.target.type),
                                  target_id=impact.target.id,
                                  amount=impact.amount)
                for impact in answer.impacts]

    def cmd_get_impacters_ratings(self, targets, actor_types, limit):
        data = tt_protocol_impacts_pb2.GetImpactersRatingsRequest(targets=[tt_protocol_impacts_pb2.Object(type=target_type.value, id=target_id)
                                                                           for target_type, target_id in targets],
                                                                  actor_types=[actor_type.value for actor_type in actor_types],
                                                                  limit=limit)

        answer = operations.sync_request(url=self.url('get-impacters-ratings'),
                                         data=data,
                                         AnswerType=tt_protocol_impacts_pb2.GetImpactersRatingsResponse)

        ratings = {}

        for answer_rating in answer.ratings:
            target = (OBJECT_TYPE(answer_rating.target.type), answer_rating.target.id)
            rating = [self.impact_class(type=self.impact_type,
                                        actor_type=OBJECT_TYPE(record.actor.type),
                                        actor_id=record.actor.id,
                                        target_type=target[0],
                                        target_id=target[1],
                                        amount=record.amount)
                      for record in answer_rating.records]

            ratings[target] = rating

        return ratings

    def cmd_scale_impacts(self, target_types, scale):
        data = tt_protocol_impacts_pb2.ScaleImpactsRequest(target_types=[target_type.value for target_type in target_types],
                                                           scale=scale)

        operations.sync_request(url=self.url('scale-impacts'),
                                data=data,
                                AnswerType=tt_protocol_impacts_pb2.ScaleImpactsResponse)

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_impacts_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_impacts_pb2.DebugClearServiceResponse)
