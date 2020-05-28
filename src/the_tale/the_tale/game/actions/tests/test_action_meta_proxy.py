
import smart_imports

smart_imports.all()


class MetaProxyActionForArenaPvP1x1Tests(pvp_helpers.PvPTestsMixin, utils_testcase.TestCase):

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        super(MetaProxyActionForArenaPvP1x1Tests, self).setUp()

        game_logic.create_test_map()

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

        self.battle_info = self.create_pvp_battle()

        self.action_idl_1 = self.battle_info.hero_1.actions.actions_list[0]
        self.action_idl_2 = self.battle_info.hero_2.actions.actions_list[0]

        self.bundle_id = 666

    def test_create(self):
        self.assertFalse(self.action_idl_1.leader)
        self.assertFalse(self.action_idl_2.leader)
        self.assertTrue(self.battle_info.hero_1.actions.current_action.leader)
        self.assertTrue(self.battle_info.hero_2.actions.current_action.leader)
        self.assertEqual(self.battle_info.hero_1.actions.number, 2)
        self.assertEqual(self.battle_info.hero_2.actions.number, 2)

        self.assertNotEqual(self.battle_info.hero_1.actions.current_action.bundle_id, self.action_idl_1.bundle_id)
        self.assertNotEqual(self.battle_info.hero_2.actions.current_action.bundle_id, self.action_idl_2.bundle_id)
        self.assertEqual(self.battle_info.hero_1.actions.current_action.bundle_id, self.battle_info.hero_2.actions.current_action.bundle_id)

        self.assertEqual(self.battle_info.hero_1.actions.current_action.meta_action,
                         self.battle_info.hero_2.actions.current_action.meta_action)

        self.assertEqual(len(self.battle_info.storage.meta_actions), 1)

    def test_one_action_step_one_meta_step(self):
        with mock.patch('the_tale.game.actions.meta_actions.ArenaPvP1x1._process') as meta_action_process_counter:
            self.battle_info.hero_1.actions.current_action.process()

        self.assertEqual(meta_action_process_counter.call_count, 1)

    def test_two_actions_step_one_meta_step(self):
        with mock.patch('the_tale.game.actions.meta_actions.ArenaPvP1x1._process') as meta_action_process_counter:
            self.battle_info.hero_1.actions.current_action.process()
            self.battle_info.hero_2.actions.current_action.process()

        self.assertEqual(meta_action_process_counter.call_count, 1)

    def test_two_actions_step_one_meta_step_from_storage(self):
        with mock.patch('the_tale.game.actions.meta_actions.ArenaPvP1x1._process') as meta_action_process_counter:
            self.battle_info.storage.process_turn()

        self.assertEqual(meta_action_process_counter.call_count, 1)

    def test_success_processing(self):
        self.battle_info.hero_1.actions.current_action.process()

        self.assertEqual(self.battle_info.hero_1.actions.current_action.percents, self.battle_info.meta_action.percents)
        self.assertNotEqual(self.battle_info.hero_2.actions.current_action.percents, self.battle_info.meta_action.percents)

        self.assertEqual(self.battle_info.hero_1.actions.current_action.state,
                         meta_actions.ArenaPvP1x1.STATE.BATTLE_RUNNING)
        self.assertLess(self.battle_info.hero_1.actions.current_action.percents, 1)

    def test_invalid_meta_action(self):
        heroes_ids = (self.battle_info.hero_1.id, self.battle_info.hero_2.id)

        battles = pvp_tt_services.matchmaker.cmd_get_battles_by_participants(heroes_ids)
        self.assertEqual(len(battles), 1)

        storage = self.battle_info.meta_action.storage

        released_account_id = random.choice(heroes_ids)

        storage.release_account_data(released_account_id)

        if released_account_id == self.battle_info.hero_1.id:
            proxy_action = self.battle_info.hero_2.actions.current_action
        else:
            proxy_action = self.battle_info.hero_1.actions.current_action

        storage.process_turn(continue_steps_if_needed=True)

        self.assertEqual(proxy_action.state,
                         meta_actions.ArenaPvP1x1.STATE.PROCESSED)
        self.assertEqual(proxy_action.percents, 1)
        self.assertFalse(proxy_action.leader)

        self.assertNotEqual(self.battle_info.hero_1.actions.current_action, proxy_action)
        self.assertNotEqual(self.battle_info.hero_2.actions.current_action, proxy_action)

        battles = pvp_tt_services.matchmaker.cmd_get_battles_by_participants(heroes_ids)
        self.assertEqual(len(battles), 0)

    def test_full_battle(self):
        meta_action = self.battle_info.meta_action

        while meta_action.state != meta_actions.ArenaPvP1x1.STATE.PROCESSED:
            self.battle_info.storage.process_turn(continue_steps_if_needed=False)
            game_turn.increment()

        self.assertTrue(self.battle_info.hero_1.is_alive and self.battle_info.hero_2.is_alive)

        self.assertTrue(self.action_idl_1.leader)
        self.assertTrue(self.action_idl_2.leader)

    def test_get_meta_action__without_storage(self):
        self.battle_info.hero_1.actions.current_action.storage = None
        self.assertNotEqual(self.battle_info.hero_1.actions.current_action.meta_action, None)

    def test_get_meta_action__no_meta_action(self):
        self.battle_info.storage.meta_actions = {}
        self.assertEqual(self.battle_info.hero_1.actions.current_action.meta_action, None)

    def test_get_meta_action(self):
        self.assertEqual(self.battle_info.hero_1.actions.current_action.meta_action.uid, self.battle_info.meta_action.uid)
        self.assertEqual(self.battle_info.hero_2.actions.current_action.meta_action.uid, self.battle_info.meta_action.uid)

    def test_get_ui_type__without_storage(self):
        self.battle_info.hero_1.actions.current_action.storage = None
        self.assertEqual(self.battle_info.hero_1.actions.current_action.ui_type, relations.ACTION_TYPE.ARENA_PVP_1X1)
        self.assertEqual(self.battle_info.hero_1.actions.current_action.description_text_name, 'meta_action_arena_pvp_1x1_description')

    def test_get_ui_type__with_metaaction(self):
        self.assertEqual(self.battle_info.hero_1.actions.current_action.ui_type, relations.ACTION_TYPE.ARENA_PVP_1X1)
        self.assertEqual(self.battle_info.hero_1.actions.current_action.description_text_name, 'meta_action_arena_pvp_1x1_description')
