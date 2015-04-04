# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import effects

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin
from the_tale.game.artifacts import relations as artifacts_relations


class UpgradeArtifactTests(CardsTestMixin, testcase.TestCase):
    CARD = effects.UpgradeArtifact

    def setUp(self):
        super(UpgradeArtifactTests, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.assertTrue(len(self.hero.equipment.values()) > 1)

        self.card = self.CARD()


    def test_use(self):

        for rarity in artifacts_relations.RARITY.records[:-1]:
            for artifact in self.hero.equipment.values():
                artifact.rarity = rarity

            result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

            self.assertEqual(len([artifact for artifact in self.hero.equipment.values() if artifact.rarity == rarity]), len(self.hero.equipment.values()) - 1)
            self.assertEqual(len([artifact for artifact in self.hero.equipment.values() if artifact.rarity == artifacts_relations.RARITY(rarity.value+1)]), 1)

    def test_all_epic(self):
        rarity = artifacts_relations.RARITY.records[-1]

        for artifact in self.hero.equipment.values():
            artifact.rarity = rarity

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(len([artifact for artifact in self.hero.equipment.values() if artifact.rarity == rarity]), len(self.hero.equipment.values()))


    def test_no_artifacts(self):
        self.hero.equipment._remove_all()
        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))
