
import asyncio

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import operations
from .. import exceptions

from . import helpers


class CreateBattleRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_new_request(self):
        battle_request_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)

        result = await db.sql('SELECT * FROM battle_requests')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], battle_request_id)
        self.assertEqual(result[0]['initiator'], 666)
        self.assertEqual(result[0]['matchmaker_type'], 1)
        self.assertEqual(result[0]['created_at'], result[0]['updated_at'])

    @test_utils.unittest_run_loop
    async def test_duplicate_request(self):
        battle_request_1_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)
        battle_request_2_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)

        self.assertEqual(battle_request_1_id, battle_request_2_id)

        result = await db.sql('SELECT * FROM battle_requests')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], battle_request_1_id)
        self.assertEqual(result[0]['initiator'], 666)
        self.assertEqual(result[0]['matchmaker_type'], 1)

        self.assertLess(result[0]['created_at'], result[0]['updated_at'])

    @test_utils.unittest_run_loop
    async def test_not_duplicate_types(self):
        battle_request_1_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)
        battle_request_2_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=777)
        battle_request_3_id = await operations.create_battle_request(matchmaker_type=2, initiator_id=777)

        result = await db.sql('SELECT * FROM battle_requests ORDER BY created_at')

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0]['id'], battle_request_1_id)
        self.assertEqual(result[0]['initiator'], 666)
        self.assertEqual(result[0]['matchmaker_type'], 1)

        self.assertEqual(result[1]['id'], battle_request_2_id)
        self.assertEqual(result[1]['initiator'], 777)
        self.assertEqual(result[1]['matchmaker_type'], 1)

        self.assertEqual(result[2]['id'], battle_request_3_id)
        self.assertEqual(result[2]['initiator'], 777)
        self.assertEqual(result[2]['matchmaker_type'], 2)


class CancelBattleRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_requests(self):
        battle_request_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)

        await operations.cancel_battle_request(battle_request_id+1)

        result = await db.sql('SELECT * FROM battle_requests ORDER BY created_at')

        self.assertEqual(len(result), 1)

    @test_utils.unittest_run_loop
    async def test_cancel(self):
        battle_request_1_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)
        battle_request_2_id = await operations.create_battle_request(matchmaker_type=2, initiator_id=666)
        battle_request_3_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=777)

        await operations.cancel_battle_request(battle_request_2_id)

        result = await db.sql('SELECT id FROM battle_requests ORDER BY created_at')

        self.assertEqual({row['id'] for row in result}, {battle_request_1_id, battle_request_3_id})


class CreateBattleTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_create(self):
        battle_id = await operations.create_battle(matchmaker_type=1, participants_ids=(666, 777, 888))

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['matchmaker_type'], 1)

        result = await db.sql('SELECT * FROM battles_participants ORDER BY participant')

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0]['battle'], battle_id)
        self.assertEqual(result[0]['participant'], 666)

        self.assertEqual(result[1]['battle'], battle_id)
        self.assertEqual(result[1]['participant'], 777)

        self.assertEqual(result[2]['battle'], battle_id)
        self.assertEqual(result[2]['participant'], 888)

    @test_utils.unittest_run_loop
    async def test_participants_intersection(self):
        battle_id = await operations.create_battle(matchmaker_type=1, participants_ids=(666, 777, 888))

        with self.assertRaises(exceptions.BattleParticipantsIntersection):
            await operations.create_battle(matchmaker_type=1, participants_ids=(888, 999))

        with self.assertRaises(exceptions.BattleParticipantsIntersection):
            await operations.create_battle(matchmaker_type=2, participants_ids=(888, 999))

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['matchmaker_type'], 1)

        result = await db.sql('SELECT * FROM battles_participants ORDER BY participant')

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0]['battle'], battle_id)
        self.assertEqual(result[0]['participant'], 666)

        self.assertEqual(result[1]['battle'], battle_id)
        self.assertEqual(result[1]['participant'], 777)

        self.assertEqual(result[2]['battle'], battle_id)
        self.assertEqual(result[2]['participant'], 888)

    @test_utils.unittest_run_loop
    async def test_parallel_execution(self):
        tasks = [operations.create_battle(matchmaker_type=1, participants_ids=(666, 777, 888)),
                 operations.create_battle(matchmaker_type=1, participants_ids=(777, 888, 999))]

        battles_ids = await asyncio.gather(*tasks, return_exceptions=True)

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        self.assertIn(result[0]['id'], battles_ids)

        exception = [element for element in battles_ids if element != result[0]['id']][0]

        self.assertTrue(isinstance(exception, exceptions.BattleParticipantsIntersection))

    @test_utils.unittest_run_loop
    async def test_duplicate_participants(self):
        with self.assertRaises(exceptions.DuplicateBattleParticipants):
            await operations.create_battle(matchmaker_type=1, participants_ids=(888, 999, 888))

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 0)


class FinishBattleTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_battle(self):
        battle_id = await operations.create_battle(matchmaker_type=1, participants_ids=(666, 777))

        await operations.finish_battle(battle_id + 1)

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        result = await db.sql('SELECT * FROM battles_participants ORDER BY participant')

        self.assertEqual(len(result), 2)

    @test_utils.unittest_run_loop
    async def test_has_battle(self):
        battle_1_id = await operations.create_battle(matchmaker_type=1, participants_ids=(666, 777))
        battle_2_id = await operations.create_battle(matchmaker_type=1, participants_ids=(888, 999))

        await operations.finish_battle(battle_1_id)

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], battle_2_id)

        result = await db.sql('SELECT * FROM battles_participants ORDER BY participant')

        self.assertEqual(len(result), 2)

        self.assertEqual({row['participant'] for row in result}, {888, 999})


class ListBattleRequestsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_requests(self):
        requests = await operations.list_battle_requests(matchmaker_types=(1, 2))
        self.assertEqual(requests, [])

    @test_utils.unittest_run_loop
    async def test_construct_battle(self):
        battle_request_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)

        requests = await operations.list_battle_requests(matchmaker_types=(1,))

        result = await db.sql('SELECT * FROM battle_requests')

        self.assertEqual(len(requests), 1)
        self.assertEqual(len(result), 1)

        self.assertEqual(requests[0].id, battle_request_id)
        self.assertEqual(requests[0].initiator_id, 666)
        self.assertEqual(requests[0].matchmaker_type, 1)
        self.assertEqual(requests[0].created_at, result[0]['created_at'])
        self.assertEqual(requests[0].updated_at, result[0]['updated_at'])

    @test_utils.unittest_run_loop
    async def test_no_battles(self):
        battle_request_1_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)
        battle_request_2_id = await operations.create_battle_request(matchmaker_type=2, initiator_id=666)
        battle_request_3_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=777)

        await operations.create_battle_request(matchmaker_type=3, initiator_id=777)

        requests = await operations.list_battle_requests(matchmaker_types=(1, 2))

        self.assertEqual(len(requests), 3)

        self.assertEqual({request.id for request in requests}, {battle_request_1_id, battle_request_2_id, battle_request_3_id})

    @test_utils.unittest_run_loop
    async def test_has_battles(self):
        battle_request_1_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)
        battle_request_2_id = await operations.create_battle_request(matchmaker_type=2, initiator_id=666)
        battle_request_3_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=777)
        battle_request_4_id = await operations.create_battle_request(matchmaker_type=3, initiator_id=777)

        await operations.create_battle(matchmaker_type=1, participants_ids=(777, 888))

        requests = await operations.list_battle_requests(matchmaker_types=(1, 2))

        self.assertEqual(len(requests), 2)

        self.assertEqual({request.id for request in requests}, {battle_request_1_id, battle_request_2_id})


class LoadBattleRequestsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_requests(self):
        requests = await operations.load_battle_requests(battle_requests_ids=(10, 11, 12))
        self.assertEqual(requests, [])

    @test_utils.unittest_run_loop
    async def test_has_requests(self):
        battle_request_1_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)
        battle_request_2_id = await operations.create_battle_request(matchmaker_type=2, initiator_id=666)
        battle_request_3_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=777)
        battle_request_4_id = await operations.create_battle_request(matchmaker_type=3, initiator_id=777)

        requests = await operations.load_battle_requests(battle_requests_ids=(battle_request_2_id,
                                                                              battle_request_3_id,
                                                                              battle_request_4_id + 1))

        requests.sort(key=lambda request: request.created_at)

        self.assertEqual(len(requests), 2)

        self.assertEqual(requests[0].id, battle_request_2_id)
        self.assertEqual(requests[0].initiator_id, 666)
        self.assertEqual(requests[0].matchmaker_type, 2)

        self.assertEqual(requests[1].id, battle_request_3_id)
        self.assertEqual(requests[1].initiator_id, 777)
        self.assertEqual(requests[1].matchmaker_type, 1)


class AcceptBattleRequestTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_requests(self):
        battle_request_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)

        with self.assertRaises(exceptions.NoBattleRequestFound):
            await operations.accept_battle_request(battle_request_id=battle_request_id + 1,
                                                   acceptor_id=777)

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 0)

    @test_utils.unittest_run_loop
    async def test_has_requests(self):
        battle_request_1_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=666)
        battle_request_2_id = await operations.create_battle_request(matchmaker_type=2, initiator_id=666)
        battle_request_3_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=777)
        battle_request_4_id = await operations.create_battle_request(matchmaker_type=3, initiator_id=777)
        battle_request_5_id = await operations.create_battle_request(matchmaker_type=1, initiator_id=888)

        battle_id, participants_ids = await operations.accept_battle_request(battle_request_id=battle_request_2_id,
                                                                             acceptor_id=777)

        self.assertEqual(set(participants_ids), {666, 777})

        result = await db.sql('SELECT * FROM battles')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], battle_id)
        self.assertEqual(result[0]['matchmaker_type'], 2)

        result = await db.sql('SELECT * FROM battles_participants ORDER BY participant')

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['battle'], battle_id)
        self.assertEqual(result[0]['participant'], 666)

        self.assertEqual(result[1]['battle'], battle_id)
        self.assertEqual(result[1]['participant'], 777)

        result = await db.sql('SELECT * FROM battle_requests')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['initiator'], 888)


class ActiveBattlesNumberTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_battles(self):
        battles_number = await operations.active_battles_number(matchmaker_types=(1, 2))

        self.assertEqual(battles_number, {1: 0, 2: 0})

    @test_utils.unittest_run_loop
    async def test_has_battles(self):
        await operations.create_battle(matchmaker_type=1, participants_ids=(666, 777))
        await operations.create_battle(matchmaker_type=2, participants_ids=(888, 999))
        await operations.create_battle(matchmaker_type=1, participants_ids=(111, 222))
        await operations.create_battle(matchmaker_type=4, participants_ids=(333, 444))

        battles_number = await operations.active_battles_number(matchmaker_types=(1, 2, 3))

        self.assertEqual(battles_number, {1: 2, 2: 1, 3: 0})


class LoadBattlesByParticipantsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_battles(self):

        battles = await operations.load_battles_by_participants(participants_ids=())
        self.assertEqual(battles, [])

        battles = await operations.load_battles_by_participants(participants_ids=(1, 2))
        self.assertEqual(battles, [])

    @test_utils.unittest_run_loop
    async def test_load(self):
        battle_id = await operations.create_battle(matchmaker_type=1, participants_ids=(666, 777))

        battles = await operations.load_battles_by_participants(participants_ids=())
        self.assertEqual(battles, [])

        battles = await operations.load_battles_by_participants(participants_ids=(777,))

        self.assertEqual(len(battles), 1)

        self.assertEqual(battles[0].id, battle_id)
        self.assertEqual(battles[0].matchmaker_type, 1)
        self.assertEqual(set(battles[0].participants_ids), {666, 777})

        battles = await operations.load_battles_by_participants(participants_ids=(666, 777))

        self.assertEqual(len(battles), 1)

    @test_utils.unittest_run_loop
    async def test_load_multiple(self):
        battle_1_id = await operations.create_battle(matchmaker_type=1, participants_ids=(666, 777))
        battle_2_id = await operations.create_battle(matchmaker_type=2, participants_ids=(888, 999, 111))
        battle_3_id = await operations.create_battle(matchmaker_type=1, participants_ids=(222, 333))

        battles = await operations.load_battles_by_participants(participants_ids=(222, 888))

        self.assertEqual(len(battles), 2)

        battles.sort(key=lambda battle: battle.created_at)

        self.assertEqual(battles[0].id, battle_2_id)
        self.assertEqual(battles[0].matchmaker_type, 2)
        self.assertEqual(set(battles[0].participants_ids), {888, 999, 111})

        self.assertEqual(battles[1].id, battle_3_id)
        self.assertEqual(battles[1].matchmaker_type, 1)
        self.assertEqual(set(battles[1].participants_ids), {222, 333})

        self.assertTrue(battles[0].created_at < battles[1].created_at)
