# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class AddBonusEnergyTestMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddBonusEnergyTestMixin, self).setUp()
        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()


    def test_use(self):
        with self.check_delta(lambda: self.hero.energy_bonus, self.CARD.ENERGY):
            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))


class AddBonusEnergyCommonTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = effects.AddBonusEnergyCommon

class AddBonusEnergyUncommonTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = effects.AddBonusEnergyUncommon

class AddBonusEnergyRareTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = effects.AddBonusEnergyRare

class AddBonusEnergyEpicTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = effects.AddBonusEnergyEpic

class AddBonusEnergyLegendaryTests(AddBonusEnergyTestMixin, testcase.TestCase):
    CARD = effects.AddBonusEnergyLegendary
