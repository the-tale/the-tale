# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class AddBonusEnergyTestMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddBonusEnergyTestMixin, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()


    def test_use(self):
        with self.check_delta(lambda: self.hero.energy_bonus, self.CARD.ENERGY):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


class AddBonusEnergyCommonTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = prototypes.AddBonusEnergyCommon

class AddBonusEnergyUncommonTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = prototypes.AddBonusEnergyUncommon

class AddBonusEnergyRareTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = prototypes.AddBonusEnergyRare

class AddBonusEnergyEpicTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = prototypes.AddBonusEnergyEpic

class AddBonusEnergyLegendaryTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = prototypes.AddBonusEnergyLegendary
