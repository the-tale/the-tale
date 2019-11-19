
import smart_imports

smart_imports.all()


class EmissariesStorageTest(utils_testcase.TestCase,
                            helpers.ClansTestsMixin):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        self.prepair_forum_for_clans()

    def test_initialization(self):
        _storage = storage.InfosStorage()
        self.assertEqual(_storage._data, {})
        self.assertEqual(_storage._version, None)

    def test_sync(self):

        accounts = []
        clans = []

        for i in range(3):
            account = self.accounts_factory.create_account()
            accounts.append(account)

            with self.check_changed(lambda: storage.infos._version):
                clans.append(self.create_clan(account, uid=i))

        for clan in clans:
            info = storage.infos[clan.id]

            self.assertEqual(info.name, clan.name)
            self.assertEqual(info.id, clan.id)
            self.assertEqual(info.linguistics_name, clan.linguistics_name)
            self.assertEqual(info.abbr, clan.abbr)
            self.assertEqual(info.motto, clan.motto)
