from aiohttp import test_utils

from tt_protocol.protocol import matchmaker_pb2

from tt_web import postgresql as db

from .. import operations

from . import helpers


class CreateBattleRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):

        data = matchmaker_pb2.CreateBattleRequestRequest(initiator_id=666,
                                                         matchmaker_type=1).SerializeToString()

        request = await self.client.post('/create-battle-request', data=data)
        answer = await self.check_success(request, matchmaker_pb2.CreateBattleRequestResponse)

        result = await db.sql('SELECT * FROM battle_requests')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], answer.battle_request_id)
        self.assertEqual(result[0]['initiator'], 666)
        self.assertEqual(result[0]['matchmaker_type'], 1)


class CancelBattleRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_battle_request_exists(self):
        battle_request_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=1)

        data = matchmaker_pb2.CancelBattleRequestRequest(battle_request_id=battle_request_id).SerializeToString()
        request = await self.client.post('/cancel-battle-request', data=data)
        await self.check_success(request, matchmaker_pb2.CancelBattleRequestResponse)

        result = await db.sql('SELECT * FROM battle_requests')

        self.assertEqual(len(result), 0)

    @test_utils.unittest_run_loop
    async def test_battle_request_not_exists(self):
        battle_request_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=1)

        data = matchmaker_pb2.CancelBattleRequestRequest(battle_request_id=battle_request_id+1).SerializeToString()
        request = await self.client.post('/cancel-battle-request', data=data)
        await self.check_success(request, matchmaker_pb2.CancelBattleRequestResponse)

        result = await db.sql('SELECT * FROM battle_requests')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], battle_request_id)


class AcceptBattleRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        battle_request_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=1)

        data = matchmaker_pb2.AcceptBattleRequestRequest(battle_request_id=battle_request_id,
                                                         acceptor_id=777).SerializeToString()
        request = await self.client.post('/accept-battle-request', data=data)
        answer = await self.check_success(request, matchmaker_pb2.AcceptBattleRequestResponse)

        self.assertEqual(set(answer.participants_ids), {666, 777})

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], answer.battle_id)
        self.assertEqual(result[0]['matchmaker_type'], 1)

        result = await db.sql('SELECT * FROM battles_participants ORDER BY participant')

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['battle'], answer.battle_id)
        self.assertEqual(result[0]['participant'], 666)

        self.assertEqual(result[1]['battle'], answer.battle_id)
        self.assertEqual(result[1]['participant'], 777)

    @test_utils.unittest_run_loop
    async def test_no_battle_request(self):
        battle_request_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=1)

        data = matchmaker_pb2.AcceptBattleRequestRequest(battle_request_id=battle_request_id + 1,
                                                         acceptor_id=777).SerializeToString()
        request = await self.client.post('/accept-battle-request', data=data)
        await self.check_error(request, error='matchmaker.accept_battle_request.no_battle_request_found')

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 0)

    @test_utils.unittest_run_loop
    async def test_initiator_already_in_battle(self):
        battle_request_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=1)

        battle_id = await operations.create_battle(matchmaker_type=1, participants_ids=(666, 888))

        battle_request_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=1)

        data = matchmaker_pb2.AcceptBattleRequestRequest(battle_request_id=battle_request_id,
                                                         acceptor_id=777).SerializeToString()
        request = await self.client.post('/accept-battle-request', data=data)
        await self.check_error(request, error='matchmaker.accept_battle_request.participants_intersection')

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], battle_id)

    @test_utils.unittest_run_loop
    async def test_acceptor_already_in_battle(self):
        battle_request_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=1)

        battle_id = await operations.create_battle(matchmaker_type=1, participants_ids=(777, 888))

        data = matchmaker_pb2.AcceptBattleRequestRequest(battle_request_id=battle_request_id,
                                                         acceptor_id=777).SerializeToString()
        request = await self.client.post('/accept-battle-request', data=data)
        await self.check_error(request, error='matchmaker.accept_battle_request.participants_intersection')

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], battle_id)

    @test_utils.unittest_run_loop
    async def test_duplicate_participants(self):
        battle_request_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=1)

        data = matchmaker_pb2.AcceptBattleRequestRequest(battle_request_id=battle_request_id,
                                                         acceptor_id=666).SerializeToString()
        request = await self.client.post('/accept-battle-request', data=data)
        await self.check_error(request, error='matchmaker.accept_battle_request.duplicate_participants')

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 0)


class CreateBattleTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        data = matchmaker_pb2.CreateBattleRequest(matchmaker_type=2,
                                                  participants_ids=(666, 777)).SerializeToString()
        request = await self.client.post('/create-battle', data=data)
        answer = await self.check_success(request, matchmaker_pb2.CreateBattleResponse)

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], answer.battle_id)
        self.assertEqual(result[0]['matchmaker_type'], 2)

        result = await db.sql('SELECT * FROM battles_participants ORDER BY participant')

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['battle'], answer.battle_id)
        self.assertEqual(result[0]['participant'], 666)

        self.assertEqual(result[1]['battle'], answer.battle_id)
        self.assertEqual(result[1]['participant'], 777)

    @test_utils.unittest_run_loop
    async def test_participant_already_in_battle(self):
        battle_id = await operations.create_battle(matchmaker_type=1, participants_ids=(666, 888))

        data = matchmaker_pb2.CreateBattleRequest(matchmaker_type=2,
                                                  participants_ids=(666, 777)).SerializeToString()
        request = await self.client.post('/create-battle', data=data)
        await self.check_error(request, error='matchmaker.create_battle.participants_intersection')

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], battle_id)

    @test_utils.unittest_run_loop
    async def test_duplicate_participants(self):
        data = matchmaker_pb2.CreateBattleRequest(matchmaker_type=2,
                                                  participants_ids=(666, 777, 666)).SerializeToString()
        request = await self.client.post('/create-battle', data=data)
        await self.check_error(request, error='matchmaker.create_battle.duplicate_participants')

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 0)


class InfoTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_activity(self):
        data = matchmaker_pb2.GetInfoRequest(matchmaker_types=[1, 2]).SerializeToString()
        request = await self.client.post('/get-info', data=data)
        answer = await self.check_success(request, matchmaker_pb2.GetInfoResponse)

        self.assertEqual(answer.active_battles, {1: 0, 2: 0})
        self.assertEqual(list(answer.battle_requests), [])

    @test_utils.unittest_run_loop
    async def test_battle_requests(self):
        battle_request_1_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=1)
        battle_request_2_id = await operations.create_battle_request(initiator_id=777, matchmaker_type=1)
        battle_request_3_id = await operations.create_battle_request(initiator_id=888, matchmaker_type=3)
        battle_request_4_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=2)
        battle_request_5_id = await operations.create_battle_request(initiator_id=666, matchmaker_type=3)

        data = matchmaker_pb2.GetInfoRequest(matchmaker_types=[1, 2]).SerializeToString()
        request = await self.client.post('/get-info', data=data)
        answer = await self.check_success(request, matchmaker_pb2.GetInfoResponse)

        self.assertEqual(answer.active_battles, {1: 0, 2: 0})

        requests = list(answer.battle_requests)
        requests.sort(key=lambda request: request.id)

        self.assertEqual([(request.id, request.initiator_id, request.matchmaker_type)
                          for request in answer.battle_requests],
                         [(battle_request_1_id, 666, 1),
                          (battle_request_2_id, 777, 1),
                          (battle_request_4_id, 666, 2)])

    @test_utils.unittest_run_loop
    async def test_battles(self):

        await operations.create_battle(matchmaker_type=1, participants_ids=(111, 222))
        await operations.create_battle(matchmaker_type=2, participants_ids=(333, 444))
        await operations.create_battle(matchmaker_type=3, participants_ids=(555, 666))
        await operations.create_battle(matchmaker_type=1, participants_ids=(777, 888))

        data = matchmaker_pb2.GetInfoRequest(matchmaker_types=[1, 2]).SerializeToString()
        request = await self.client.post('/get-info', data=data)
        answer = await self.check_success(request, matchmaker_pb2.GetInfoResponse)

        self.assertEqual(answer.active_battles, {1: 2, 2: 1})
        self.assertEqual(list(answer.battle_requests), [])


class BatleRequestsInfoTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_activity(self):
        data = matchmaker_pb2.GetBattleRequestsRequest(battle_requests_ids=[1, 2]).SerializeToString()
        request = await self.client.post('/get-battle-requests', data=data)
        answer = await self.check_success(request, matchmaker_pb2.GetBattleRequestsResponse)

        self.assertEqual(list(answer.battle_requests), [])

    @test_utils.unittest_run_loop
    async def test_battle_requests(self):
        battle_request_1_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)
        battle_request_2_id = await operations.create_battle_request(matchmaker_type=2, initiator_id=666)
        battle_request_3_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=777)
        battle_request_4_id = await operations.create_battle_request(matchmaker_type=3, initiator_id=777)

        data = matchmaker_pb2.GetBattleRequestsRequest(battle_requests_ids=[battle_request_2_id,
                                                                            battle_request_3_id,
                                                                            battle_request_4_id + 1]).SerializeToString()
        request = await self.client.post('/get-battle-requests', data=data)
        answer = await self.check_success(request, matchmaker_pb2.GetBattleRequestsResponse)

        requests = list(answer.battle_requests)
        requests.sort(key=lambda request: request.id)

        self.assertEqual([(request.id, request.initiator_id, request.matchmaker_type)
                          for request in answer.battle_requests],
                         [(battle_request_2_id, 666, 2),
                          (battle_request_3_id, 777, 1)])


class FinishBattleTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_battle(self):
        battle_id = await operations.create_battle(matchmaker_type=1, participants_ids=(111, 222))

        data = matchmaker_pb2.FinishBattleRequest(battle_id=battle_id + 1).SerializeToString()
        request = await self.client.post('/finish-battle', data=data)
        await self.check_success(request, matchmaker_pb2.FinishBattleResponse)

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

    @test_utils.unittest_run_loop
    async def test_success(self):
        battle_id = await operations.create_battle(matchmaker_type=1, participants_ids=(111, 222))

        data = matchmaker_pb2.FinishBattleRequest(battle_id=battle_id).SerializeToString()
        request = await self.client.post('/finish-battle', data=data)
        await self.check_success(request, matchmaker_pb2.FinishBattleResponse)

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 0)


class GetBattlesByParticipantsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_battle(self):
        data = matchmaker_pb2.GetBattlesByParticipantsRequest(participants_ids=(666,)).SerializeToString()
        request = await self.client.post('/get-battles-by-participants', data=data)
        data = await self.check_success(request, matchmaker_pb2.GetBattlesByParticipantsResponse)

        self.assertEqual(len(data.battles), 0)

    @test_utils.unittest_run_loop
    async def test_has_battle(self):
        battle_1_id = await operations.create_battle(matchmaker_type=1, participants_ids=(666, 777))
        battle_2_id = await operations.create_battle(matchmaker_type=2, participants_ids=(888, 999, 111))
        battle_3_id = await operations.create_battle(matchmaker_type=1, participants_ids=(222, 333))

        data = matchmaker_pb2.GetBattlesByParticipantsRequest(participants_ids=(222, 888)).SerializeToString()
        request = await self.client.post('/get-battles-by-participants', data=data)
        data = await self.check_success(request, matchmaker_pb2.GetBattlesByParticipantsResponse)

        battles = list(data.battles)

        self.assertEqual(len(battles), 2)

        battles.sort(key=lambda battle: battle.created_at)

        self.assertEqual(battles[0].id, battle_2_id)
        self.assertEqual(battles[0].matchmaker_type, 2)
        self.assertEqual(set(battles[0].participants_ids), {888, 999, 111})

        self.assertEqual(battles[1].id, battle_3_id)
        self.assertEqual(battles[1].matchmaker_type, 1)
        self.assertEqual(set(battles[1].participants_ids), {222, 333})
