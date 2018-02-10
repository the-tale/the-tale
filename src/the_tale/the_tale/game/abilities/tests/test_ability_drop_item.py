
from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.artifacts import storage as artifacts_storage
from the_tale.game.artifacts.relations import RARITY

from the_tale.game.abilities.deck import DropItem


from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game.abilities.tests.helpers import UseAbilityTaskMixin


class DropItemAbilityTest(UseAbilityTaskMixin, testcase.TestCase):
    PROCESSOR = DropItem

    def setUp(self):
        super(DropItemAbilityTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.ability = self.PROCESSOR()

    @property
    def use_attributes(self):
        return super(DropItemAbilityTest, self).use_attributes(hero=self.hero, storage=self.storage)

    def test_no_items(self):
        self.assertEqual(self.hero.bag.occupation, 0)
        self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

    def test_success(self):
        self.hero.bag.put_artifact(artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts, self.hero.level, rarity=RARITY.NORMAL))

        with self.check_delta(lambda: self.hero.bag.occupation, -1):
                self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    @mock.patch('the_tale.game.heroes.objects.Hero.might_crit_chance', 1)
    def test_success__critical(self):
        self.hero.bag.put_artifact(artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts, self.hero.level, rarity=RARITY.NORMAL))

        old_money_stats = self.hero.statistics.money_earned_from_help

        self.assertEqual(self.hero.bag.occupation, 1)

        self.assertEqual(self.ability.use(**self.use_attributes), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.bag.occupation, 0)

        self.assertTrue(old_money_stats < self.hero.statistics.money_earned_from_help)
