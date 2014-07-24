# coding: utf-8
import random

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import prototypes

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class RepairArtifacsTestMixin(CardsTestMixin):

    def check_all_equipment_repaired(self, result):
        self.assertEqual(all(item.integrity == item.max_integrity for item in self.hero.equipment.values()), result)


class RepairRandomArtifactTests(RepairArtifacsTestMixin, testcase.TestCase):
    CARD = prototypes.RepairRandomArtifact

    def setUp(self):
        super(RepairRandomArtifactTests, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()


    def test_all_repaired(self):
        self.check_all_equipment_repaired(True)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.check_all_equipment_repaired(True)

    def test_use(self):
        self.check_all_equipment_repaired(True)

        items = [item for item in self.hero.equipment.values() if item]
        random.shuffle(items)

        items[0].integrity = 0
        items[1].integrity = 0

        self.check_all_equipment_repaired(False)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.check_all_equipment_repaired(False)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.check_all_equipment_repaired(True)



class RepairAllArtifactsTests(RepairArtifacsTestMixin, testcase.TestCase):
    CARD = prototypes.RepairAllArtifacts

    def setUp(self):
        super(RepairAllArtifactsTests, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()

    def test_all_repaired(self):
        self.check_all_equipment_repaired(True)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.check_all_equipment_repaired(True)

    def test_use(self):
        self.check_all_equipment_repaired(True)

        items = [item for item in self.hero.equipment.values() if item]
        random.shuffle(items)

        items[0].integrity = 0
        items[1].integrity = 0

        self.check_all_equipment_repaired(False)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.check_all_equipment_repaired(True)
