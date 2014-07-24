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


class InstantMonsterKillTests(CardsTestMixin, testcase.TestCase):
    CARD = prototypes.InstantMonsterKill

    def setUp(self):
        super(InstantMonsterKillTests, self).setUp()
        create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        self.card = self.CARD()

    def test_no_battle(self):
        self.assertFalse(self.hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

    def test_use(self):
        from the_tale.game.actions.prototypes import ActionBattlePvE1x1Prototype
        from the_tale.game.heroes.logic import create_mob_for_hero

        with mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 0):
            ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=create_mob_for_hero(self.hero))

        self.assertTrue(self.hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1)
        self.assertTrue(self.hero.actions.current_action.mob.health > 0)
        self.assertTrue(self.hero.actions.current_action.percents < 1)

        result, step, postsave_actions = self.card.use(**self.use_attributes(storage=self.storage, hero_id=self.hero.id))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.actions.current_action.mob.health <= 0)
        self.assertEqual(self.hero.actions.current_action.percents, 1)
