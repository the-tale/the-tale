# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin

from the_tale.game.heroes.relations import ITEMS_OF_EXPENDITURE


class ChangeHeroSpendingsCommonTests(testcase.TestCase):
    CARD = None

    def setUp(self):
        super(ChangeHeroSpendingsCommonTests, self).setUp()

    def test_no_new_spendigns(self):
        items = []

        for card in prototypes.CARDS.values():
            if hasattr(card, 'ITEM'):
                items.append(card.ITEM)

        items.append(ITEMS_OF_EXPENDITURE.USELESS)
        items.append(ITEMS_OF_EXPENDITURE.IMPACT)

        self.assertEqual(len(items), len(ITEMS_OF_EXPENDITURE.records))
        self.assertEqual(set(items), set(ITEMS_OF_EXPENDITURE.records))


class ChangeHeroSpendingsMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(ChangeHeroSpendingsMixin, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()


    def test_use(self):

        # sure that quests will be loaded and not cal mark_updated
        self.hero.quests.mark_updated()

        for item in ITEMS_OF_EXPENDITURE.records:
            if item == self.CARD.ITEM:
                continue

            self.hero.next_spending = item

            with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
                result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

            self.assertEqual(mark_updated.call_count, 1)

            self.assertEqual(self.hero.next_spending, self.CARD.ITEM)

            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


    def test_equal(self):
        self.hero.next_spending = self.CARD.ITEM

        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual(mark_updated.call_count, 0)

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))



class ChangeHeroSpendingsToInstantHealTests(ChangeHeroSpendingsMixin, testcase.TestCase):
    CARD = prototypes.ChangeHeroSpendingsToInstantHeal

class ChangeHeroSpendingsToBuyingArtifactTests(ChangeHeroSpendingsMixin, testcase.TestCase):
    CARD = prototypes.ChangeHeroSpendingsToBuyingArtifact

class ChangeHeroSpendingsToSharpeingArtifactTests(ChangeHeroSpendingsMixin, testcase.TestCase):
    CARD = prototypes.ChangeHeroSpendingsToSharpeingArtifact

class ChangeHeroSpendingsToRepairingArtifactTests(ChangeHeroSpendingsMixin, testcase.TestCase):
    CARD = prototypes.ChangeHeroSpendingsToRepairingArtifact

class ChangeHeroSpendingsToExperienceTests(ChangeHeroSpendingsMixin, testcase.TestCase):
    CARD = prototypes.ChangeHeroSpendingsToExperience
