# coding: utf-8
import mock

from questgen.quests.pilgrimage import Pilgrimage
from questgen.quests.hometown import Hometown

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.quests.logic import get_first_quests, NORMAL_QUESTS


class LogicTests(testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')

        account = AccountPrototype.get_by_email('test_user@test.com')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account.id))
        self.hero =self.storage.accounts_to_heroes[account.id]

    def test_get_first_quests__special(self):
        self.hero.preferences.set_place(self.place_1)
        self.assertEqual(get_first_quests(self.hero, special=True), [Hometown.TYPE])

    @mock.patch('the_tale.game.balance.constants.QUESTS_PILGRIMAGE_FRACTION', -1)
    def test_get_first_quests__special__no_quests(self):
        for i in xrange(100):
            self.assertEqual(get_first_quests(self.hero, special=True), NORMAL_QUESTS)


    def test_get_first_quests__pilgrimage(self):
        quests = set()
        for i in xrange(10000):
            quests |= set(get_first_quests(self.hero, special=False))

        self.assertTrue(Pilgrimage.TYPE in quests)
