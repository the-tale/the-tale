
from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.cards.tests.helpers import CardsTestMixin


class InstantMonsterKillTests(CardsTestMixin, testcase.TestCase):
    CARD = cards.CARD.INSTANT_MONSTER_KILL

    def setUp(self):
        super(InstantMonsterKillTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

    def test_no_battle(self):
        self.assertFalse(self.hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

    def test_use(self):
        from the_tale.game.actions.prototypes import ActionBattlePvE1x1Prototype
        from the_tale.game.mobs import storage as mobs_storage

        with mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 0):
            ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.mobs.create_mob_for_hero(self.hero))

        self.assertTrue(self.hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1)
        self.assertTrue(self.hero.actions.current_action.mob.health > 0)
        self.assertTrue(self.hero.actions.current_action.percents < 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.actions.current_action.mob.health <= 0)
        self.assertEqual(self.hero.actions.current_action.percents, 1)
