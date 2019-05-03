
import smart_imports

smart_imports.all()


class SupervisorTaskTests(utils_testcase.TestCase):

    def setUp(self):
        super(SupervisorTaskTests, self).setUp()

        self.p1, self.p2, self.p3 = logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

    def test_process_when_not_all_members_captured(self):
        task = prototypes.SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)
        self.assertRaises(exceptions.GameError, task.process, bundle_id=666)

    def test_process_arena_pvp_1x1(self):
        task = prototypes.SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        task.capture_member(self.account_1.id)
        task.capture_member(self.account_2.id)

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

    @mock.patch('the_tale.game.actions.container.ActionsContainer.has_proxy_actions', lambda container: True)
    def test_process_arena_pvp_1x1__already_had_proxy_action(self):
        task = prototypes.SupervisorTaskPrototype.create_arena_pvp_1x1(self.account_1, self.account_2)

        task.capture_member(self.account_1.id)
        task.capture_member(self.account_2.id)

        old_hero = heroes_logic.load_hero(account_id=self.account_1.id)
        old_hero.health = 1
        heroes_logic.save_hero(old_hero)

        task.process(bundle_id=666)

        new_hero = heroes_logic.load_hero(account_id=self.account_1.id)
        new_hero_2 = heroes_logic.load_hero(account_id=self.account_2.id)

        self.assertNotEqual(new_hero.actions.current_action.bundle_id, new_hero_2.actions.current_action.bundle_id)

        self.assertEqual(old_hero.actions.number, new_hero.actions.number)
        self.assertNotEqual(new_hero.health, new_hero.max_health)

        self.assertEqual(new_hero.actions.number, 1)
        self.assertEqual(new_hero_2.actions.number, 1)

        self.assertEqual(new_hero.actions.current_action.meta_action, None)
        self.assertEqual(new_hero_2.actions.current_action.meta_action, None)
