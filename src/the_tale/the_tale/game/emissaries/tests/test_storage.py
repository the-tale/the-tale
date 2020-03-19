
import smart_imports

smart_imports.all()


class EmissariesStorageTest(utils_testcase.TestCase,
                            clans_helpers.ClansTestsMixin,
                            helpers.EmissariesTestsMixin):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=clans_conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

        self.storage = storage.EmissariesStorage()
        self.storage.sync()

    def test_initialization(self):
        _storage = storage.EmissariesStorage()
        self.assertEqual(_storage._data, {})
        self.assertEqual(_storage._version, None)

    def test_sync(self):

        emissaries = [self.create_emissary(clan=self.clan,
                                           initiator=self.account,
                                           place_id=random.choice(self.places).id)
                      for i in range(3)]

        emissaries.sort(key=lambda emissary: emissary.id)

        logic._remove_emissary(emissaries[1].id, reason=relations.REMOVE_REASON.KILLED)

        self.storage.sync(force=True)

        self.assertIn(emissaries[0].id, self.storage)
        self.assertNotIn(emissaries[1].id, self.storage)
        self.assertIn(emissaries[2].id, self.storage)

    def test_get_or_load(self):
        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=random.choice(self.places).id)

        logic._remove_emissary(emissary.id, reason=relations.REMOVE_REASON.KILLED)

        self.storage.sync(force=True)

        self.assertNotIn(emissary.id, self.storage)

        self.assertEqual(self.storage.get_or_load(emissary.id),
                         logic.load_emissary(emissary.id))


class EventsStorageTest(utils_testcase.TestCase,
                        clans_helpers.ClansTestsMixin,
                        helpers.EmissariesTestsMixin):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=clans_conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

        self.storage = storage.EventsStorage()
        self.storage.sync()

    def test_initialization(self):
        _storage = storage.EventsStorage()
        self.assertEqual(_storage._data, {})
        self.assertEqual(_storage._version, None)

    def test_sync(self):

        account_2 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(owner=account_2, uid=2)

        emissaries = [self.create_emissary(clan=self.clan,
                                           initiator=self.account,
                                           place_id=random.choice(self.places).id),
                      self.create_emissary(clan=clan_2,
                                           initiator=account_2,
                                           place_id=random.choice(self.places).id),
                      self.create_emissary(clan=self.clan,
                                           initiator=self.account,
                                           place_id=random.choice(self.places).id)]

        emissaries.sort(key=lambda emissary: emissary.id)

        event_0_1 = logic.create_event(initiator=self.account,
                                       emissary=emissaries[0],
                                       concrete_event=events.Rest(raw_ability_power=100500),
                                       days=1)

        event_0_2 = logic.create_event(initiator=self.account,
                                       emissary=emissaries[0],
                                       concrete_event=events.Rest(raw_ability_power=100500),
                                       days=1)

        event_1_1 = logic.create_event(initiator=self.account,
                                       emissary=emissaries[1],
                                       concrete_event=events.Rest(raw_ability_power=100500),
                                       days=1)

        event_1_2 = logic.create_event(initiator=self.account,
                                       emissary=emissaries[1],
                                       concrete_event=events.Dismiss(raw_ability_power=100500),
                                       days=1)

        event_2_1 = logic.create_event(initiator=self.account,
                                       emissary=emissaries[2],
                                       concrete_event=events.Rest(raw_ability_power=100500),
                                       days=1)

        logic.finish_event(event_0_1)

        self.storage.sync(force=True)

        self.assertNotIn(event_0_1.id, self.storage)
        self.assertIn(event_1_1.id, self.storage)
        self.assertIn(event_1_2.id, self.storage)
        self.assertIn(event_2_1.id, self.storage)

        self.assertCountEqual(self.storage.emissary_events(emissaries[0].id), [event_0_2])
        self.assertCountEqual(self.storage.emissary_events(emissaries[1].id), [event_1_1, event_1_2])
        self.assertCountEqual(self.storage.emissary_events(emissaries[2].id), [event_2_1])

        self.assertCountEqual(self.storage.clan_events(self.clan.id), [event_0_2, event_2_1])
        self.assertCountEqual(self.storage.clan_events(clan_2.id), [event_1_1, event_1_2])

    def test_get_or_load(self):
        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=random.choice(self.places).id)

        event = logic.create_event(initiator=self.account,
                                   emissary=emissary,
                                   concrete_event=events.Rest(raw_ability_power=100500),
                                   days=1)

        logic.finish_event(event)

        self.storage.sync(force=True)

        self.assertNotIn(event.id, self.storage)

        self.assertEqual(self.storage.get_or_load(event.id),
                         logic.load_event(event.id))
