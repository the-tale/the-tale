# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.balance import formulas as f
from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class AddExperienceTestMixin(CardsTestMixin):
    CARD = None

    def setUp(self):
        super(AddExperienceTestMixin, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.experience_modifier', 1.0)
    def test_use(self):
        self.assertEqual(self.hero.experience, 0)
        self.assertEqual(self.hero.level, 1)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.experience !=0 or self.hero.level != 1)

        self.assertEqual(self.hero.experience + f.total_exp_to_lvl(self.hero.level-1), self.CARD.EXPERIENCE)


class AddExperienceUncommonTests(AddExperienceTestMixin, testcase.TestCase):
    CARD = prototypes.AddExperienceUncommon


class AddExperienceRareTests(AddExperienceTestMixin, testcase.TestCase):
    CARD = prototypes.AddExperienceRare


class AddExperienceEpicTests(AddExperienceTestMixin, testcase.TestCase):
    CARD = prototypes.AddExperienceEpic
