# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class HelpPlaceMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(HelpPlaceMixin, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()


    def test_use(self):
        with self.check_delta(lambda: self.hero.places_history._get_places_statisitcs().get(self.place_1.id, 0), self.CARD.HELPS):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id, place_id=self.place_1.id))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_wrong_place(self):
        with self.check_not_changed(lambda: self.hero.places_history._get_places_statisitcs().get(self.place_1.id, 0)):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id, place_id=666))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class HelpPlaceUncommonTests(HelpPlaceMixin, testcase.TestCase):
    CARD = prototypes.HelpPlaceUncommon

class HelpPlaceRareTests(HelpPlaceMixin, testcase.TestCase):
    CARD = prototypes.HelpPlaceRare

class HelpPlaceEpicTests(HelpPlaceMixin, testcase.TestCase):
    CARD = prototypes.HelpPlaceEpic

class HelpPlaceLegendaryTests(HelpPlaceMixin, testcase.TestCase):
    CARD = prototypes.HelpPlaceLegendary
