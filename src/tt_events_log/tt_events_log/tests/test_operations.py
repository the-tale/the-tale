
import datetime

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import objects
from .. import operations

from . import helpers


class AddEventTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        event_id = await operations.add_event(tags={1, 13, 666},
                                              data={'a': 'b'},
                                              turn=100500,
                                              time=now)

        result = await db.sql('SELECT * FROM events')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['data'], {'a': 'b'})
        self.assertEqual(result[0]['created_at'], now)
        self.assertEqual(result[0]['created_at_turn'], 100500)

        result = await db.sql('SELECT * FROM events_tags')

        self.assertEqual(len(result), 3)

        self.assertEqual({row['event'] for row in result}, {event_id})
        self.assertEqual({row['tag'] for row in result}, {1, 13, 666})
        self.assertEqual({row['created_at'] for row in result}, {now})
        self.assertEqual({row['created_at_turn'] for row in result}, {100500})

    @test_utils.unittest_run_loop
    async def test_multiple_saves(self):
        now_1 = datetime.datetime.now(tz=datetime.timezone.utc)
        now_2 = now_1 - datetime.timedelta(days=1)

        event_1_id = await operations.add_event(tags={1, 13},
                                                data={'a': 'b'},
                                                turn=100500,
                                                time=now_1)

        event_2_id = await operations.add_event(tags={13, 666},
                                                data={'a': 'c'},
                                                turn=100499,
                                                time=now_2)

        result = await db.sql('SELECT * FROM events ORDER BY created_at')

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['data'], {'a': 'c'})
        self.assertEqual(result[0]['created_at'], now_2)
        self.assertEqual(result[0]['created_at_turn'], 100499)

        self.assertEqual(result[1]['data'], {'a': 'b'})
        self.assertEqual(result[1]['created_at'], now_1)
        self.assertEqual(result[1]['created_at_turn'], 100500)

        result = await db.sql('SELECT * FROM events_tags WHERE event=%(event)s', {'event': event_1_id})

        self.assertEqual(len(result), 2)

        self.assertEqual({row['event'] for row in result}, {event_1_id})
        self.assertEqual({row['tag'] for row in result}, {1, 13})
        self.assertEqual({row['created_at'] for row in result}, {now_1})
        self.assertEqual({row['created_at_turn'] for row in result}, {100500})

        result = await db.sql('SELECT * FROM events_tags WHERE event=%(event)s', {'event': event_2_id})

        self.assertEqual(len(result), 2)

        self.assertEqual({row['event'] for row in result}, {event_2_id})
        self.assertEqual({row['tag'] for row in result}, {13, 666})
        self.assertEqual({row['created_at'] for row in result}, {now_2})
        self.assertEqual({row['created_at_turn'] for row in result}, {100499})


class EventsNumberTests(helpers.BaseTests):

    async def prepair_data(self):
        await helpers.add_event(tags={1, 13}, turn=100500)
        await helpers.add_event(tags={13, 666}, turn=100499)

    @test_utils.unittest_run_loop
    async def test_no_events(self):
        await self.prepair_data()

        number = await operations.events_number({0})
        self.assertEqual(number, 0)

        number = await operations.events_number({1, 13, 666})
        self.assertEqual(number, 0)

    @test_utils.unittest_run_loop
    async def test_single_event(self):
        await self.prepair_data()

        number = await operations.events_number({1})
        self.assertEqual(number, 1)

        number = await operations.events_number({1, 13})
        self.assertEqual(number, 1)

        number = await operations.events_number({13, 666})
        self.assertEqual(number, 1)

    @test_utils.unittest_run_loop
    async def test_multiple_events(self):
        await self.prepair_data()

        number = await operations.events_number({13})
        self.assertEqual(number, 2)

    @test_utils.unittest_run_loop
    async def test_no_tags(self):
        await self.prepair_data()

        number = await operations.events_number({})
        self.assertEqual(number, 2)


class GetAllEventsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_events(self):
        events = await operations.get_all_events(page=1, records_on_page=5)

        self.assertEqual(events, [])

    @test_utils.unittest_run_loop
    async def test_events_exists(self):
        event_1_id = await helpers.add_event(tags={1, 2}, turn=1)
        event_2_id = await helpers.add_event(tags={2, 3}, turn=2)
        event_3_id = await helpers.add_event(tags={1, 3}, turn=3)

        events = await operations.get_all_events(page=1, records_on_page=5)

        self.assertEqual(events[0], objects.Event(id=event_1_id,
                                                  tags={1, 2},
                                                  data={'turn': 1},
                                                  created_at=events[0].created_at,
                                                  created_at_turn=1))

        self.assertEqual(events[1], objects.Event(id=event_2_id,
                                                  tags={2, 3},
                                                  data={'turn': 2},
                                                  created_at=events[1].created_at,
                                                  created_at_turn=2))

        self.assertEqual(events[2], objects.Event(id=event_3_id,
                                                  tags={1, 3},
                                                  data={'turn': 3},
                                                  created_at=events[2].created_at,
                                                  created_at_turn=3))

    @test_utils.unittest_run_loop
    async def test_events_exists__page(self):
        event_1_id = await helpers.add_event(tags={1, 2}, turn=1)
        event_2_id = await helpers.add_event(tags={2, 3}, turn=2)
        event_3_id = await helpers.add_event(tags={1, 3}, turn=3)

        events = await operations.get_all_events(page=2, records_on_page=2)

        self.assertEqual(events[0], objects.Event(id=event_3_id,
                                                  tags={1, 3},
                                                  data={'turn': 3},
                                                  created_at=events[0].created_at,
                                                  created_at_turn=3))


class GetAllLastEventsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_events(self):
        events = await operations.get_all_last_events(number=5)

        self.assertEqual(events, [])

    @test_utils.unittest_run_loop
    async def test_events_exists(self):
        event_1_id = await helpers.add_event(tags={1, 2}, turn=1)
        event_2_id = await helpers.add_event(tags={2, 3}, turn=2)
        event_3_id = await helpers.add_event(tags={1, 3}, turn=3)

        events = await operations.get_all_last_events(number=2)

        self.assertEqual(len(events), 2)

        self.assertEqual(events[0], objects.Event(id=event_2_id,
                                                  tags={2, 3},
                                                  data={'turn': 2},
                                                  created_at=events[0].created_at,
                                                  created_at_turn=2))

        self.assertEqual(events[1], objects.Event(id=event_3_id,
                                                  tags={1, 3},
                                                  data={'turn': 3},
                                                  created_at=events[1].created_at,
                                                  created_at_turn=3))


class GetEventsByTagsTests(helpers.BaseTests):

    async def check_events(self, tags, page, records_on_page, expected_ids):
        events = await operations.get_events_by_tags(tags=tags, page=page, records_on_page=records_on_page)
        self.assertEqual([event.id for event in events], expected_ids)

    @test_utils.unittest_run_loop
    async def test_load_events(self):
        event_1_id = await helpers.add_event(tags={1, 2}, turn=1)
        event_2_id = await helpers.add_event(tags={2, 3}, turn=2)
        event_3_id = await helpers.add_event(tags={1, 3}, turn=3)

        events = await operations.get_events_by_tags(tags={3}, page=1, records_on_page=5)

        self.assertEqual(events[0], objects.Event(id=event_2_id,
                                                  tags={2, 3},
                                                  data={'turn': 2},
                                                  created_at=events[0].created_at,
                                                  created_at_turn=2))

        self.assertEqual(events[1], objects.Event(id=event_3_id,
                                                  tags={1, 3},
                                                  data={'turn': 3},
                                                  created_at=events[1].created_at,
                                                  created_at_turn=3))

    @test_utils.unittest_run_loop
    async def test_pages(self):
        events_ids = []

        for i in range(12):
            event_id = await helpers.add_event(tags={1, 2}, turn=i)
            events_ids.append(event_id)

        await self.check_events(tags={1, 2}, page=1, records_on_page=5,
                                expected_ids=events_ids[:5])

        await self.check_events(tags={1, 2}, page=2, records_on_page=5,
                                expected_ids=events_ids[5:10])

        await self.check_events(tags={1, 2}, page=3, records_on_page=5,
                                expected_ids=events_ids[10:])

        await self.check_events(tags={1, 2}, page=4, records_on_page=5,
                                expected_ids=[])

    @test_utils.unittest_run_loop
    async def test_filter(self):
        events_ids = []

        for i, tags in enumerate([(1, 2),
                                  (1, 3),
                                  (1, 2),
                                  (1, 3),
                                  (1, 2),
                                  (1, 3),
                                  (1, 4)]):
            event_id = await helpers.add_event(tags=tags, turn=i)
            events_ids.append(event_id)

        await self.check_events(tags={1}, page=1, records_on_page=5,
                                expected_ids=events_ids[:5])

        await self.check_events(tags={2}, page=1, records_on_page=5,
                                expected_ids=[events_ids[0], events_ids[2], events_ids[4]])

        await self.check_events(tags={2}, page=1, records_on_page=2,
                                expected_ids=[events_ids[0], events_ids[2]])

        await self.check_events(tags={2}, page=2, records_on_page=2,
                                expected_ids=[events_ids[4]])

    @test_utils.unittest_run_loop
    async def test_exect_filter(self):
        events_ids = []

        for i, tags in enumerate([(1, 2, 3, 4, 5),
                                  (1, 2, 3, 4),
                                  (1, 2, 3, 5),
                                  (1, 2, 4, 5),
                                  (1, 3, 4, 5),
                                  (2, 3, 4, 5),
                                  (1, 2, 3, 4, 5)]):
            event_id = await helpers.add_event(tags=tags, turn=i)
            events_ids.append(event_id)

        await self.check_events(tags={1, 3, 5}, page=1, records_on_page=5,
                                expected_ids=[events_ids[0], events_ids[2], events_ids[4], events_ids[6]])

        await self.check_events(tags={3, 5}, page=1, records_on_page=5,
                                expected_ids=[events_ids[0], events_ids[2], events_ids[4], events_ids[5], events_ids[6]])

        await self.check_events(tags={3, 5}, page=1, records_on_page=2,
                                expected_ids=[events_ids[0], events_ids[2]])

        await self.check_events(tags={3, 5}, page=2, records_on_page=2,
                                expected_ids=[events_ids[4], events_ids[5]])

        await self.check_events(tags={3, 5}, page=3, records_on_page=2,
                                expected_ids=[events_ids[6]])


class GetLastEventsByTagsTests(helpers.BaseTests):

    async def check_events(self, tags, number, expected_ids):
        events = await operations.get_last_events_by_tags(tags=tags, number=number)
        self.assertEqual([event.id for event in events], expected_ids)

    @test_utils.unittest_run_loop
    async def test_load_events(self):
        event_1_id = await helpers.add_event(tags={1, 2}, turn=1)
        event_2_id = await helpers.add_event(tags={2, 3}, turn=2)
        event_3_id = await helpers.add_event(tags={1, 3}, turn=3)

        events = await operations.get_last_events_by_tags(tags={3}, number=5)

        self.assertEqual(events[0], objects.Event(id=event_2_id,
                                                  tags={2, 3},
                                                  data={'turn': 2},
                                                  created_at=events[0].created_at,
                                                  created_at_turn=2))

        self.assertEqual(events[1], objects.Event(id=event_3_id,
                                                  tags={1, 3},
                                                  data={'turn': 3},
                                                  created_at=events[1].created_at,
                                                  created_at_turn=3))

    @test_utils.unittest_run_loop
    async def test_filter(self):
        events_ids = []

        for i, tags in enumerate([(1, 2),
                                  (1, 3),
                                  (1, 2),
                                  (1, 3),
                                  (1, 2),
                                  (1, 3),
                                  (1, 4)]):
            event_id = await helpers.add_event(tags=tags, turn=i)
            events_ids.append(event_id)

        await self.check_events(tags={1},
                                number=5,
                                expected_ids=events_ids[-5:])

        await self.check_events(tags={2},
                                number=5,
                                expected_ids=[events_ids[0], events_ids[2], events_ids[4]])

        await self.check_events(tags={2},
                                number=2,
                                expected_ids=[events_ids[2], events_ids[4]])

    @test_utils.unittest_run_loop
    async def test_exect_filter(self):
        events_ids = []

        for i, tags in enumerate([(1, 2, 3, 4, 5),
                                  (1, 2, 3, 4),
                                  (1, 2, 3, 5),
                                  (1, 2, 4, 5),
                                  (1, 3, 4, 5),
                                  (2, 3, 4, 5),
                                  (1, 2, 3, 4, 5)]):
            event_id = await helpers.add_event(tags=tags, turn=i)
            events_ids.append(event_id)

        await self.check_events(tags={1, 3, 5},
                                number=3,
                                expected_ids=[events_ids[2], events_ids[4], events_ids[6]])

        await self.check_events(tags={3, 5},
                                number=4,
                                expected_ids=[events_ids[2], events_ids[4], events_ids[5], events_ids[6]])

        await self.check_events(tags={3, 5},
                                number=2,
                                expected_ids=[events_ids[5], events_ids[6]])
