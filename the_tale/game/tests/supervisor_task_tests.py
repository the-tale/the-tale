# coding: utf-8

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.actions.models import Action, MetaAction

from game.logic import create_test_map
from game.prototypes import SupervisorTaskPrototype
from game.exceptions import GameException

from game.heroes.prototypes import HeroPrototype

from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.models import Battle1x1, BATTLE_1X1_STATE

from game.models import Bundle

class SupervisorTaskTests(TestCase):

    def setUp(self):
        super(SupervisorTaskTests, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

    def test_process_when_not_all_members_captured(self):
        task = SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        self.assertRaises(GameException, task.process)

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

        self.assertEqual(Action.objects.all().count(), 2)
        self.assertEqual(MetaAction.objects.all().count(), 0)

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PREPAIRING).count(), 2)
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSING).count(), 0)

        old_hero = HeroPrototype.get_by_account_id(self.account_1.id)
        old_hero.health = 1
        old_hero.save()

        self.assertEqual(Bundle.objects.all().count(), 2)

        task.process()

        self.assertEqual(Bundle.objects.all().count(), 3)

        self.assertEqual(Action.objects.all().order_by('created_at')[2].bundle_id, Bundle.objects.all().order_by('created_at')[2].id)
        self.assertNotEqual(Action.objects.all().order_by('created_at')[0].bundle_id, Action.objects.all().order_by('created_at')[2].bundle_id)
        self.assertNotEqual(Action.objects.all().order_by('created_at')[1].bundle_id, Action.objects.all().order_by('created_at')[2].bundle_id)

        new_hero = HeroPrototype.get_by_account_id(self.account_1.id)

        self.assertNotEqual(old_hero, new_hero)
        self.assertTrue(len(old_hero.actions_descriptions) < len(new_hero.actions_descriptions))
        self.assertEqual(new_hero.health, new_hero.max_health)

        self.assertEqual(Action.objects.all().count(), 4)
        self.assertEqual(MetaAction.objects.all().count(), 1)

        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PREPAIRING).count(), 0)
        self.assertEqual(Battle1x1.objects.filter(state=BATTLE_1X1_STATE.PROCESSING).count(), 2)
