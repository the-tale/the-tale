# coding: utf-8
import math

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class ExperienceToEnergyMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(ExperienceToEnergyMixin, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()

    @mock.patch('the_tale.game.heroes.objects.Hero.experience_modifier', 1.0)
    def test_use(self):
        self.hero.add_experience(39)
        self.assertEqual(self.hero.experience, 39)

        with self.check_delta(lambda: self.hero.experience, -39):
            with self.check_delta(lambda: self.hero.energy_bonus, int(math.ceil(39.0 / self.CARD.EXPERIENCE))):
                result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_use__no_exp(self):
        self.assertEqual(self.hero.experience, 0)

        with self.check_not_changed(lambda: self.hero.experience):
            with self.check_not_changed(lambda: self.hero.energy_bonus):
                result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))


class ExperienceToEnergyUncommon(ExperienceToEnergyMixin, testcase.TestCase):
    CARD = effects.ExperienceToEnergyUncommon

class ExperienceToEnergyRare(ExperienceToEnergyMixin, testcase.TestCase):
    CARD = effects.ExperienceToEnergyRare

class ExperienceToEnergyEpic(ExperienceToEnergyMixin, testcase.TestCase):
    CARD = effects.ExperienceToEnergyEpic

class ExperienceToEnergyLegendary(ExperienceToEnergyMixin, testcase.TestCase):
    CARD = effects.ExperienceToEnergyLegendary
