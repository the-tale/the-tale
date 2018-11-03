
import time

from aiohttp import test_utils

from tt_protocol.protocol import events_log_pb2

from tt_web import s11n

from .. import objects
from .. import protobuf
from .. import operations

from . import helpers


class AddEventTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        response = await self.client.post('/add-event', data=events_log_pb2.AddEventRequest(tags=[1, 13, 666],
                                                                                            data='{"a": "b"}',
                                                                                            turn=666,
                                                                                            time=time.time()).SerializeToString())
        await self.check_success(response, events_log_pb2.AddEventResponse)

        events = await operations.get_all_events(page=1, records_on_page=10)

        self.assertEqual(len(events), 1)

        self.assertEqual(events[0], objects.Event(id=events[0].id,
                                                  tags={1, 13, 666},
                                                  data={'a': 'b'},
                                                  created_at=events[0].created_at,
                                                  created_at_turn=666))


class GetEvents(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_events(self):
        response = await self.client.post('/get-events', data=events_log_pb2.GetEventsRequest(tags=[1, 13, 666],
                                                                                              page=1,
                                                                                              records_on_page=3).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetEventsResponse)

        self.assertEqual(list(data.events), [])
        self.assertEqual(data.page, 1)
        self.assertEqual(data.total_records, 0)

    async def prepair_data(self):
        for i, tags in enumerate([(1, 2),
                                  (1, 3),
                                  (1, 2),
                                  (1, 3),
                                  (1, 2),
                                  (1, 3),
                                  (1, 4)]):
            await helpers.add_event(tags=tags, turn=i)

        return await operations.get_all_events(page=1, records_on_page=100)

    @test_utils.unittest_run_loop
    async def test_serialization(self):
        events = await self.prepair_data()

        response = await self.client.post('/get-events', data=events_log_pb2.GetEventsRequest(tags=[],
                                                                                              page=1,
                                                                                              records_on_page=1).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetEventsResponse)

        event = data.events[0]

        self.assertEqual(event.id, events[0].id)
        self.assertEqual(s11n.from_json(event.data), {'turn': 0})
        self.assertEqual(set(event.tags), {1, 2})
        self.assertEqual(event.turn, 0)
        self.assertEqual(event.time, time.mktime(events[0].created_at.timetuple())+events[0].created_at.microsecond / 1000000)

    @test_utils.unittest_run_loop
    async def test_pages__zero(self):
        events = await self.prepair_data()

        response = await self.client.post('/get-events', data=events_log_pb2.GetEventsRequest(tags=[],
                                                                                              page=0,
                                                                                              records_on_page=3).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetEventsResponse)

        self.assertEqual(list(data.events), [protobuf.from_event(events[0]),
                                             protobuf.from_event(events[1]),
                                             protobuf.from_event(events[2])])
        self.assertEqual(data.page, 1)
        self.assertEqual(data.total_records, 7)

    @test_utils.unittest_run_loop
    async def test_page(self):
        events = await self.prepair_data()

        response = await self.client.post('/get-events', data=events_log_pb2.GetEventsRequest(tags=[],
                                                                                              page=2,
                                                                                              records_on_page=3).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetEventsResponse)

        self.assertEqual(list(data.events), [protobuf.from_event(events[3]),
                                             protobuf.from_event(events[4]),
                                             protobuf.from_event(events[5])])
        self.assertEqual(data.page, 2)
        self.assertEqual(data.total_records, 7)

    @test_utils.unittest_run_loop
    async def test_pages__large_page(self):
        events = await self.prepair_data()

        response = await self.client.post('/get-events', data=events_log_pb2.GetEventsRequest(tags=[],
                                                                                              page=100,
                                                                                              records_on_page=3).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetEventsResponse)

        self.assertEqual(list(data.events), [protobuf.from_event(events[6])])
        self.assertEqual(data.page, 3)
        self.assertEqual(data.total_records, 7)

    @test_utils.unittest_run_loop
    async def test_filter(self):
        events = await self.prepair_data()

        response = await self.client.post('/get-events', data=events_log_pb2.GetEventsRequest(tags=[2],
                                                                                              page=1,
                                                                                              records_on_page=2).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetEventsResponse)

        self.assertEqual(list(data.events), [protobuf.from_event(events[0]),
                                             protobuf.from_event(events[2])])
        self.assertEqual(data.page, 1)
        self.assertEqual(data.total_records, 3)

        response = await self.client.post('/get-events', data=events_log_pb2.GetEventsRequest(tags=[2],
                                                                                              page=2,
                                                                                              records_on_page=2).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetEventsResponse)

        self.assertEqual(list(data.events), [protobuf.from_event(events[4])])
        self.assertEqual(data.page, 2)
        self.assertEqual(data.total_records, 3)


class GetLastEvents(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_events(self):
        response = await self.client.post('/get-last-events',
                                          data=events_log_pb2.GetLastEventsRequest(tags=[1, 13, 666],
                                                                                   number=3).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetLastEventsResponse)

        self.assertEqual(list(data.events), [])
        self.assertEqual(data.total_records, 0)

    async def prepair_data(self):
        for i, tags in enumerate([(1, 2),
                                  (1, 3),
                                  (1, 2),
                                  (1, 3),
                                  (1, 2),
                                  (1, 3),
                                  (1, 4)]):
            await helpers.add_event(tags=tags, turn=i)

        return await operations.get_all_last_events(number=100)

    @test_utils.unittest_run_loop
    async def test_serialization(self):
        events = await self.prepair_data()

        response = await self.client.post('/get-last-events',
                                          data=events_log_pb2.GetLastEventsRequest(tags=[],
                                                                                   number=1).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetLastEventsResponse)

        event = data.events[0]

        self.assertEqual(event.id, events[-1].id)
        self.assertEqual(s11n.from_json(event.data), {'turn': 6})
        self.assertEqual(set(event.tags), {1, 4})
        self.assertEqual(event.turn, 6)
        self.assertEqual(event.time, time.mktime(events[-1].created_at.timetuple())+events[-1].created_at.microsecond / 1000000)

    @test_utils.unittest_run_loop
    async def test_filter(self):
        events = await self.prepair_data()

        response = await self.client.post('/get-last-events',
                                          data=events_log_pb2.GetLastEventsRequest(tags=[2],
                                                                                   number=2).SerializeToString())

        data = await self.check_success(response, events_log_pb2.GetLastEventsResponse)

        self.assertEqual(list(data.events), [protobuf.from_event(events[2]),
                                             protobuf.from_event(events[4])])
        self.assertEqual(data.total_records, 3)
