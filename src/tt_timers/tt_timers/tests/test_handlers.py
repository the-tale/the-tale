import datetime

from aiohttp import test_utils

from tt_protocol.protocol import timers_pb2

from tt_web import postgresql as db

from .. import operations

from . import helpers


class CreateTimerTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_new_timer(self):
        request = await self.client.post('/create-timer', data=timers_pb2.CreateTimerRequest(owner_id=667,
                                                                                             entity_id=777,
                                                                                             type=3,
                                                                                             speed=4,
                                                                                             border=500,
                                                                                             resources=66,
                                                                                             callback_data='abc').SerializeToString())
        answer = await self.check_success(request, timers_pb2.CreateTimerResponse)

        queue_timer_id, queue_finish_at = operations.TIMERS_QUEUE.first()

        self.assertEqual(answer.timer.id, queue_timer_id)
        self.assertEqual(datetime.datetime.fromtimestamp(answer.timer.finish_at), queue_finish_at)

        results = await db.sql('SELECT * FROM timers')

        self.assertEqual(len(results), 1)

        self.assertEqual(results[0]['id'], answer.timer.id)
        self.assertEqual(results[0]['owner'], 667)
        self.assertEqual(results[0]['entity'], 777)
        self.assertEqual(results[0]['type'], 3)
        self.assertEqual(results[0]['speed'], 4)
        self.assertEqual(results[0]['border'], 500)
        self.assertEqual(results[0]['resources'], 66)
        self.assertEqual(results[0]['finish_at'].replace(tzinfo=None), datetime.datetime.fromtimestamp(answer.timer.finish_at))
        self.assertEqual(results[0]['data'], {'callback_data': 'abc'})

    @test_utils.unittest_run_loop
    async def test_duplicate_timer(self):
        request = await self.client.post('/create-timer', data=timers_pb2.CreateTimerRequest(owner_id=667,
                                                                                             entity_id=777,
                                                                                             type=3,
                                                                                             speed=4,
                                                                                             border=500,
                                                                                             resources=0,
                                                                                             callback_data='abc').SerializeToString())

        request = await self.client.post('/create-timer', data=timers_pb2.CreateTimerRequest(owner_id=667,
                                                                                             entity_id=777,
                                                                                             type=3,
                                                                                             speed=4,
                                                                                             border=500,
                                                                                             callback_data='abc').SerializeToString())

        await self.check_error(request, error='timers.create_timer.duplicate_timer')

        results = await db.sql('SELECT * FROM timers')
        self.assertEqual(len(results), 1)

    @test_utils.unittest_run_loop
    async def test_undefined_type(self):
        request = await self.client.post('/create-timer', data=timers_pb2.CreateTimerRequest(owner_id=667,
                                                                                             entity_id=777,
                                                                                             type=76574,
                                                                                             speed=4,
                                                                                             border=500,
                                                                                             callback_data='abc').SerializeToString())

        await self.check_error(request, error='timers.create_timer.unknown_type')


class ChangeSpeedTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        request = await self.client.post('/create-timer', data=timers_pb2.CreateTimerRequest(owner_id=667,
                                                                                             entity_id=777,
                                                                                             type=3,
                                                                                             speed=4,
                                                                                             border=500,
                                                                                             resources=66,
                                                                                             callback_data='abc').SerializeToString())

        request = await self.client.post('/change-speed', data=timers_pb2.ChangeSpeedRequest(owner_id=667,
                                                                                             entity_id=777,
                                                                                             type=3,
                                                                                             speed=40).SerializeToString())
        answer = await self.check_success(request, timers_pb2.ChangeSpeedResponse)

        queue_timer_id, queue_finish_at = operations.TIMERS_QUEUE.first()

        self.assertEqual(answer.timer.id, queue_timer_id)
        self.assertEqual(datetime.datetime.fromtimestamp(answer.timer.finish_at), queue_finish_at)

        results = await db.sql('SELECT * FROM timers')

        self.assertEqual(len(results), 1)

        self.assertEqual(results[0]['id'], answer.timer.id)
        self.assertEqual(results[0]['owner'], 667)
        self.assertEqual(results[0]['entity'], 777)
        self.assertEqual(results[0]['type'], 3)
        self.assertEqual(results[0]['speed'], 40)

    @test_utils.unittest_run_loop
    async def test_no_timer_found(self):
        request = await self.client.post('/create-timer', data=timers_pb2.CreateTimerRequest(owner_id=667,
                                                                                             entity_id=777,
                                                                                             type=3,
                                                                                             speed=4,
                                                                                             border=500,
                                                                                             resources=66,
                                                                                             callback_data='abc').SerializeToString())

        request = await self.client.post('/change-speed', data=timers_pb2.ChangeSpeedRequest(owner_id=667,
                                                                                             entity_id=888,
                                                                                             type=3,
                                                                                             speed=40).SerializeToString())
        await self.check_error(request, error='timers.change_speed.timer_not_found')

    @test_utils.unittest_run_loop
    async def test_undefined_type(self):
        request = await self.client.post('/create-timer', data=timers_pb2.CreateTimerRequest(owner_id=667,
                                                                                             entity_id=777,
                                                                                             type=3,
                                                                                             speed=4,
                                                                                             border=500,
                                                                                             callback_data='abc').SerializeToString())

        request = await self.client.post('/change-speed', data=timers_pb2.ChangeSpeedRequest(owner_id=667,
                                                                                             entity_id=777,
                                                                                             type=4,
                                                                                             speed=40).SerializeToString())
        await self.check_error(request, error='timers.change_speed.unknown_type')
