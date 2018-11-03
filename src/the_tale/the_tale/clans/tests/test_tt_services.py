
import smart_imports

smart_imports.all()


class ClansChronicleClientTests(utils_testcase.TestCase,
                                helpers.ClansTestsMixin):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

    def test_add_get(self):

        tt_services.chronicle.cmd_debug_clear_service()

        events_types = []

        for text in ('x', 'y', 'z'):
            events_types.append(relations.EVENT.random())
            tt_services.chronicle.cmd_add_event(clan=self.clan,
                                                event=events_types[-1],
                                                tags=[self.account.meta_object().tag],
                                                message=text)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=2)

        self.assertEqual(total_events, 3)
        self.assertEqual(len(events), 2)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          events_types[-1].meta_object().tag,
                          self.account.meta_object().tag})

        self.assertEqual(set(events[1].tags),
                         {self.clan.meta_object().tag,
                          events_types[-2].meta_object().tag,
                          self.account.meta_object().tag})

        page, total_records, events = tt_services.chronicle.cmd_get_events(clan=self.clan,
                                                                           page=1,
                                                                           tags=(),
                                                                           records_on_page=2)

        self.assertEqual(page, 1)
        self.assertEqual(total_records, 3)
        self.assertEqual(len(events), 2)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          events_types[-2].meta_object().tag,
                          self.account.meta_object().tag})

        self.assertEqual(set(events[1].tags),
                         {self.clan.meta_object().tag,
                          events_types[-3].meta_object().tag,
                          self.account.meta_object().tag})

    def test_no_intersections(self):

        account_2 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(owner=account_2, uid=2)

        tt_services.chronicle.cmd_debug_clear_service()

        for text in ('x', 'y', 'z'):
            tt_services.chronicle.cmd_add_event(clan=self.clan,
                                                event=relations.EVENT.random(),
                                                tags=[self.account.meta_object().tag],
                                                message=text)

        for text in ('x_2', 'y_2', 'z_2'):
            tt_services.chronicle.cmd_add_event(clan=clan_2,
                                                event=relations.EVENT.random(),
                                                tags=[account_2.meta_object().tag],
                                                message=text)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(total_events, 3)
        self.assertEqual({event.message for event in events}, {'x', 'y', 'z'})

        total_events, events = tt_services.chronicle.cmd_get_last_events(clan_2, tags=(), number=1000)

        self.assertEqual(total_events, 3)
        self.assertEqual({event.message for event in events}, {'x_2', 'y_2', 'z_2'})
