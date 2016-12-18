# coding: utf-8

from the_tale.common.utils.testcase import TestCase

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import SupervisorTaskPrototype
from the_tale.game import exceptions

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.pvp.prototypes import Battle1x1Prototype
from the_tale.game.pvp.models import Battle1x1, BATTLE_1X1_STATE


class SupervisorTaskTests(TestCase):

    def setUp(self):
        super(SupervisorTaskTests, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

    def test_process_when_not_all_members_captured(self):
        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        self.assertRaises(exceptions.GameError, task.process, bundle_id=666)

    def test_process_arena_pvp_1x1(self):
        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        task.capture_member(self.account_1.id)
        task.capture_member(self.account_2.id)

        battle_1 = Battle1x1Prototype.create(self.account_1)
        battle_1.set_enemy(self.account_2)
        battle_1.save()

        battle_2 = Battle1x1Prototype.create(self.account_2)
        battle_2.set_enemy(self.account_1)
        battle_2.save()

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PREPAIRING).count(), 2)
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSING).count(), 0)

        old_hero = heroes_logic.load_hero(account_id=self.account_1.id)
        old_hero.health = 1
        heroes_logic.save_hero(old_hero)

        task.process(bundle_id=666)

        new_hero = heroes_logic.load_hero(account_id=self.account_1.id)
        new_hero_2 = heroes_logic.load_hero(account_id=self.account_2.id)

        self.assertEqual(new_hero.actions.current_action.bundle_id, new_hero_2.actions.current_action.bundle_id)
        self.assertNotEqual(new_hero.actions.actions_list[0].bundle_id, new_hero.actions.actions_list[1].bundle_id)
        self.assertNotEqual(new_hero_2.actions.actions_list[0].bundle_id, new_hero_2.actions.actions_list[1].bundle_id)

        self.assertNotEqual(old_hero, new_hero)
        self.assertTrue(old_hero.actions.number < new_hero.actions.number)
        self.assertEqual(new_hero.health, new_hero.max_health)

        self.assertEqual(new_hero.actions.number, 2)
        self.assertEqual(new_hero_2.actions.number, 2)

        self.assertEqual(new_hero.actions.current_action.meta_action.serialize(),
                         new_hero_2.actions.current_action.meta_action.serialize())

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PREPAIRING).count(), 0)
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSING).count(), 2)
