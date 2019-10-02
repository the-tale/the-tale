
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
