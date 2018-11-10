
import smart_imports

smart_imports.all()


events_log_client = events_log.Client(entry_point=chronicle_conf.settings.TT_GAME_CHRONICLE_ENTRY_POINT)


class TTAPiTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()
        events_log_client.cmd_debug_clear_service()

    def test_add_event(self):
        events_log_client.cmd_add_event(tags={1, 2, 3},
                                        message='some.message',
                                        attributes={'attr.1': 1, 'attr.2': 2},
                                        turn=666,
                                        timestamp=777.5)

        page, total_records, events = events_log_client.cmd_get_events(tags=(),
                                                                       page=1,
                                                                       records_on_page=10)
        self.assertEqual(page, 1)
        self.assertEqual(total_records, 1)

        self.assertEqual(events, [events_log.Event(message='some.message',
                                                   attributes={'attr.1': 1, 'attr.2': 2},
                                                   tags=frozenset((1, 2, 3)),
                                                   turn=666,
                                                   created_at=datetime.datetime.fromtimestamp(777.5))])

    def test_add_event__default_arguments(self):

        game_turn.increment(666)

        old_time = datetime.datetime.now()
        old_turn = game_turn.number()

        events_log_client.cmd_add_event(tags={1, 2, 3},
                                        message='some.message',
                                        attributes={'attr.1': 1, 'attr.2': 2})

        game_turn.increment(666)

        page, total_records, events = events_log_client.cmd_get_events(tags=(),
                                                                       page=1,
                                                                       records_on_page=10)
        self.assertEqual(page, 1)
        self.assertEqual(total_records, 1)

        self.assertEqual(events, [events_log.Event(message='some.message',
                                                   attributes={'attr.1': 1, 'attr.2': 2},
                                                   tags=frozenset((1, 2, 3)),
                                                   turn=old_turn,
                                                   created_at=events[0].created_at)])

        self.assertTrue(old_time < events[0].created_at)

    def test_add_event__no_tags(self):
        events_log_client.cmd_add_event(tags=(),
                                        message='some.message',
                                        attributes={'attr.1': 1, 'attr.2': 2})

        page, total_records, events = events_log_client.cmd_get_events(tags=(),
                                                                       page=1,
                                                                       records_on_page=10)
        self.assertEqual(page, 1)
        self.assertEqual(total_records, 1)

        self.assertEqual(events[0].tags, frozenset())

    def test_get_events__no_events(self):
        page, total_records, events = events_log_client.cmd_get_events(tags=(),
                                                                       page=1,
                                                                       records_on_page=10)
        self.assertEqual(page, 1)
        self.assertEqual(total_records, 0)
        self.assertEqual(events, [])

    def prepair_data(self):
        for i, tags in enumerate(((1, 2),
                                  (1, 3),
                                  (1, 2),
                                  (2, 3),
                                  (1, 4),
                                  (2, 4),
                                  (1, 5))):
            events_log_client.cmd_add_event(tags=tags,
                                            message='some.message.{}'.format(i),
                                            attributes={'i': i})

    def test_get_events__has_events(self):
        self.prepair_data()

        page, total_records, events = events_log_client.cmd_get_events(tags=(1,),
                                                                       page=2,
                                                                       records_on_page=2)
        self.assertEqual(page, 2)
        self.assertEqual(total_records, 5)
        self.assertEqual([event.attributes['i'] for event in events], [2, 4])

    def test_get_last_events__has_events(self):
        self.prepair_data()

        total_records, events = events_log_client.cmd_get_last_events(tags=(1,),
                                                                      number=2)
        self.assertEqual(total_records, 5)
        self.assertEqual([event.attributes['i'] for event in events], [4, 6])
