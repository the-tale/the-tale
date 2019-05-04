import smart_imports

smart_imports.all()


class ACCEPT_BATTLE_RESULT(rels_django.DjangoEnum):
    records = (('SUCCESS', 0, 'битва создана'),
               ('NO_BATTLE_REQUEST', 1, 'вызов на битву не обнаружен'),
               ('ALREADY_IN_BATTLE', 2, 'один из бойцов уже сражается'),)


class CREATE_BATTLE_RESULT(rels_django.DjangoEnum):
    records = (('SUCCESS', 0, 'битва создана'),
               ('ALREADY_IN_BATTLE', 2, 'один из бойцов уже сражается'),)


class Client(client.Client):

    def protobuf_to_battle_request(self, pb_battle_request):
        raise NotImplementedError

    def protobuf_to_battle(self, pb_battle):
        raise NotImplementedError

    def cmd_create_battle_request(self, matchmaker_type, initiator_id):
        answer = operations.sync_request(url=self.url('create-battle-request'),
                                         data=tt_protocol_matchmaker_pb2.CreateBattleRequestRequest(matchmaker_type=matchmaker_type.value,
                                                                                                    initiator_id=initiator_id),
                                         AnswerType=tt_protocol_matchmaker_pb2.CreateBattleRequestResponse)
        return answer.battle_request_id

    def cmd_cancel_battle_request(self, battle_request_id):
        operations.sync_request(url=self.url('cancel-battle-request'),
                                data=tt_protocol_matchmaker_pb2.CancelBattleRequestRequest(battle_request_id=battle_request_id),
                                AnswerType=tt_protocol_matchmaker_pb2.CancelBattleRequestResponse)

    def cmd_accept_battle_request(self, battle_request_id, acceptor_id):
        try:
            answer = operations.sync_request(url=self.url('accept-battle-request'),
                                             data=tt_protocol_matchmaker_pb2.AcceptBattleRequestRequest(battle_request_id=battle_request_id,
                                                                                                        acceptor_id=acceptor_id),
                                             AnswerType=tt_protocol_matchmaker_pb2.AcceptBattleRequestResponse)
        except exceptions.TTAPIUnexpectedAPIStatus as e:
            if e.arguments['code'] == 'matchmaker.accept_battle_request.no_battle_request_found':
                return ACCEPT_BATTLE_RESULT.NO_BATTLE_REQUEST, None, None

            if e.arguments['code'] == 'matchmaker.accept_battle_request.participants_intersection':
                return ACCEPT_BATTLE_RESULT.ALREADY_IN_BATTLE, None, None

            raise

        return ACCEPT_BATTLE_RESULT.SUCCESS, answer.battle_id, set(answer.participants_ids)

    def cmd_create_battle(self, matchmaker_type, participants_ids):
        try:
            answer = operations.sync_request(url=self.url('create-battle'),
                                             data=tt_protocol_matchmaker_pb2.CreateBattleRequest(matchmaker_type=matchmaker_type.value,
                                                                                                 participants_ids=participants_ids),
                                             AnswerType=tt_protocol_matchmaker_pb2.CreateBattleResponse)
        except exceptions.TTAPIUnexpectedAPIStatus as e:
            if e.arguments['code'] == 'matchmaker.create_battle.participants_intersection':
                return CREATE_BATTLE_RESULT.ALREADY_IN_BATTLE, None

            raise

        return CREATE_BATTLE_RESULT.SUCCESS, answer.battle_id

    def cmd_get_battle_requests(self, battle_requests_ids):

        answer = operations.sync_request(url=self.url('get-battle-requests'),
                                         data=tt_protocol_matchmaker_pb2.GetBattleRequestsRequest(battle_requests_ids=battle_requests_ids),
                                         AnswerType=tt_protocol_matchmaker_pb2.GetBattleRequestsResponse)

        return [self.protobuf_to_battle_request(request) for request in answer.battle_requests]

    def cmd_get_info(self, matchmaker_types):

        raw_types = [type.value for type in matchmaker_types]

        answer = operations.sync_request(url=self.url('get-info'),
                                         data=tt_protocol_matchmaker_pb2.GetInfoRequest(matchmaker_types=raw_types),
                                         AnswerType=tt_protocol_matchmaker_pb2.GetInfoResponse)

        active_battles = {matchmaker_type: answer.active_battles[matchmaker_type.value] for matchmaker_type in matchmaker_types}

        battle_requests = [self.protobuf_to_battle_request(request) for request in answer.battle_requests]

        return battle_requests, active_battles

    def cmd_finish_battle(self, battle_id):
        operations.sync_request(url=self.url('finish-battle'),
                                data=tt_protocol_matchmaker_pb2.FinishBattleRequest(battle_id=battle_id),
                                AnswerType=tt_protocol_matchmaker_pb2.FinishBattleResponse)

    def cmd_get_battles_by_participants(self, participants_ids):
        answer = operations.sync_request(url=self.url('get-battles-by-participants'),
                                         data=tt_protocol_matchmaker_pb2.GetBattlesByParticipantsRequest(participants_ids=participants_ids),
                                         AnswerType=tt_protocol_matchmaker_pb2.GetBattlesByParticipantsResponse)
        return [self.protobuf_to_battle(battle) for battle in answer.battles]

    def cmd_debug_clear_service(self):
        if django_settings.TESTS_RUNNING:
            operations.sync_request(url=self.url('debug-clear-service'),
                                    data=tt_protocol_matchmaker_pb2.DebugClearServiceRequest(),
                                    AnswerType=tt_protocol_matchmaker_pb2.DebugClearServiceResponse)
