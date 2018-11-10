
import smart_imports

smart_imports.all()


class LogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

    def test_remove_game_data(self):

        self.assertEqual(heroes_models.Hero.objects.count(), 1)

        logic.remove_game_data(self.account)

        self.assertEqual(heroes_models.Hero.objects.count(), 0)


class FormGameInfoTests(utils_testcase.TestCase, pvp_helpers.PvPTestsMixin):

    def setUp(self):
        super(FormGameInfoTests, self).setUp()

        logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account(is_fast=True)
        self.account_2 = self.accounts_factory.create_account(is_fast=True)

    def test_no_account(self):
        data = logic.form_game_info()
        self.assertEqual(data['mode'], 'pve')
        self.assertEqual(data['account'], None)
        self.assertEqual(data['enemy'], None)

    def test_account(self):
        data = logic.form_game_info(self.account_1, is_own=True)
        self.assertEqual(data['mode'], 'pve')
        self.assertFalse(data['account']['in_pvp_queue'])
        self.assertEqual(data['account']['id'], self.account_1.id)
        self.assertEqual(data['enemy'], None)

    def test_account__other(self):
        data = logic.form_game_info(self.account_2, is_own=True)
        self.assertEqual(data['mode'], 'pve')
        self.assertFalse(data['account']['in_pvp_queue'])
        self.assertEqual(data['account']['id'], self.account_2.id)
        self.assertEqual(data['enemy'], None)

    def test_pvp_in_queue(self):
        self.pvp_create_battle(self.account_1, None)
        self.pvp_create_battle(self.account_2, None)

        data = logic.form_game_info(self.account_1)
        self.assertEqual(data['mode'], 'pve')
        self.assertTrue(data['account']['in_pvp_queue'])
        self.assertEqual(data['enemy'], None)

    def test_pvp_prepairing(self):
        self.pvp_create_battle(self.account_1, self.account_2, state=pvp_relations.BATTLE_1X1_STATE.PREPAIRING)
        self.pvp_create_battle(self.account_2, self.account_1, state=pvp_relations.BATTLE_1X1_STATE.PREPAIRING)

        data = logic.form_game_info(self.account_1)
        self.assertEqual(data['mode'], 'pve')
        self.assertFalse(data['account']['in_pvp_queue'])
        self.assertEqual(data['enemy'], None)

    def test_pvp_processing(self):
        self.pvp_create_battle(self.account_1, self.account_2, state=pvp_relations.BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, state=pvp_relations.BATTLE_1X1_STATE.PROCESSING)

        data = logic.form_game_info(self.account_1)
        self.assertEqual(data['mode'], 'pvp')
        self.assertFalse(data['account']['in_pvp_queue'])
        self.assertFalse(data['enemy']['in_pvp_queue'])

        self.assertEqual(data['account']['id'], self.account_1.id)
        self.assertEqual(data['enemy']['id'], self.account_2.id)

    def test_own_hero_get_cached_data(self):
        hero = heroes_logic.load_hero(account_id=self.account_1.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.cached_ui_info_for_hero',
                        mock.Mock(return_value={'actual_on_turn': hero.saved_at_turn,
                                                'pvp': 'actual',
                                                'ui_caching_started_at': 0})) as cached_ui_info_for_hero:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                data = logic.form_game_info(self.account_1, is_own=True)

        self.assertEqual(data['account']['hero']['pvp'], 'actual')
        self.assertEqual(data['enemy'], None)

        self.assertEqual(cached_ui_info_for_hero.call_count, 1)
        self.assertEqual(cached_ui_info_for_hero.call_args, mock.call(account_id=self.account_1.id, recache_if_required=True, patch_turns=None, for_last_turn=False))
        self.assertEqual(ui_info.call_count, 0)

    def create_not_own_ui_info(self, hero):
        return {'actual_on_turn': hero.saved_at_turn,
                'action': {'data': {'pvp__actual': 'actual',
                                    'pvp__last_turn': 'last_turn'}},
                'ui_caching_started_at': 0,
                'changed_fields': []}

    def test_not_own_hero_get_cached_data__not_cached(self):
        hero = heroes_logic.load_hero(account_id=self.account_1.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.cached_ui_info_for_hero',
                        mock.Mock(return_value=self.create_not_own_ui_info(hero))) as cached_ui_info_for_hero:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info',
                            mock.Mock(return_value=self.create_not_own_ui_info(hero))) as ui_info:
                logic.form_game_info(self.account_1, is_own=False)

        self.assertEqual(cached_ui_info_for_hero.call_count, 1)
        self.assertEqual(cached_ui_info_for_hero.call_args, mock.call(account_id=self.account_1.id, recache_if_required=False, patch_turns=None, for_last_turn=True))
        self.assertEqual(ui_info.call_count, 0)

    def test_not_own_hero_get_cached_data(self):
        hero = heroes_logic.load_hero(account_id=self.account_1.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.ui_info',
                        mock.Mock(return_value=self.create_not_own_ui_info(hero))) as ui_info:
            data = logic.form_game_info(self.account_1, is_own=False)

        self.assertEqual(data['account']['hero']['action']['data']['pvp'], 'last_turn')
        self.assertEqual(data['enemy'], None)

        self.assertFalse('pvp__actual' in data['account']['hero']['action']['data']['pvp'])
        self.assertFalse('pvp__last_turn' in data['account']['hero']['action']['data']['pvp'])

        self.assertEqual(data['account']['energy'], None)

        self.assertEqual(ui_info.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    def test_is_old(self):
        self.assertFalse(logic.form_game_info(self.account_1, is_own=True)['account']['is_old'])

        game_turn.set(666)
        self.assertTrue(logic.form_game_info(self.account_1, is_own=True)['account']['is_old'])

        heroes_logic.save_hero(heroes_logic.load_hero(account_id=self.account_1.id))
        self.assertFalse(logic.form_game_info(self.account_1, is_own=True)['account']['is_old'])

    def test_is_old__not_own_hero(self):
        self.assertFalse(logic.form_game_info(self.account_1, is_own=False)['account']['is_old'])

        game_turn.set(666)

        self.assertTrue(logic.form_game_info(self.account_1, is_own=False)['account']['is_old'])

        heroes_logic.save_hero(heroes_logic.load_hero(account_id=self.account_1.id))
        self.assertFalse(logic.form_game_info(self.account_1, is_own=False)['account']['is_old'])

    def test_is_old__pvp(self):
        self.pvp_create_battle(self.account_1, self.account_2, pvp_relations.BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, pvp_relations.BATTLE_1X1_STATE.PROCESSING)

        hero_1 = heroes_logic.load_hero(account_id=self.account_1.id)
        hero_2 = heroes_logic.load_hero(account_id=self.account_2.id)

        self.assertFalse(logic.form_game_info(self.account_1)['account']['is_old'])
        self.assertFalse(logic.form_game_info(self.account_1)['enemy']['is_old'])

        game_turn.set(666)
        self.assertTrue(logic.form_game_info(self.account_1)['account']['is_old'])
        self.assertTrue(logic.form_game_info(self.account_1)['enemy']['is_old'])

        heroes_logic.save_hero(hero_1)
        heroes_logic.save_hero(hero_2)

        self.assertFalse(logic.form_game_info(self.account_1)['account']['is_old'])
        self.assertFalse(logic.form_game_info(self.account_1)['enemy']['is_old'])

    def test_game_info_data_hidding(self):
        '''
        player hero always must show actual data
        enemy hero always must show data on statrt of the turn
        '''
        self.pvp_create_battle(self.account_1, self.account_2, pvp_relations.BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, pvp_relations.BATTLE_1X1_STATE.PROCESSING)

        self.storage = logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        meta_action_battle = actions_meta_actions.ArenaPvP1x1.create(self.storage, hero_1, hero_2)
        meta_action_battle.set_storage(self.storage)

        actions_prototypes.ActionMetaProxyPrototype.create(hero=hero_1, _bundle_id=hero_1.actions.current_action.bundle_id, meta_action=meta_action_battle)
        actions_prototypes.ActionMetaProxyPrototype.create(hero=hero_2, _bundle_id=hero_1.actions.current_action.bundle_id, meta_action=meta_action_battle)

        meta_action_battle.hero_1_pvp.set_energy(1)
        meta_action_battle.hero_2_pvp.set_energy(2)

        heroes_logic.save_hero(hero_1)
        heroes_logic.save_hero(hero_2)

        data = logic.form_game_info(self.account_1, is_own=True)

        self.assertEqual(data['account']['hero']['action']['data']['pvp']['energy'], 1)
        self.assertEqual(data['enemy']['hero']['action']['data']['pvp']['energy'], 0)

        meta_action_battle.hero_2_pvp.store_turn_data()
        heroes_logic.save_hero(hero_2)

        data = logic.form_game_info(self.account_1, is_own=True)

        self.assertEqual(data['enemy']['hero']['action']['data']['pvp']['energy'], 2)

    def test_game_info_caching(self):
        self.pvp_create_battle(self.account_1, self.account_2, pvp_relations.BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, pvp_relations.BATTLE_1X1_STATE.PROCESSING)

        hero_1 = heroes_logic.load_hero(account_id=self.account_1.id)
        hero_2 = heroes_logic.load_hero(account_id=self.account_2.id)

        def get_ui_info(hero, **kwargs):
            if hero.id == hero_1.id:
                return {'actual_on_turn': hero_1.saved_at_turn,
                        'action': {'data': {'pvp__actual': 'actual',
                                            'pvp__last_turn': 'last_turn'}},
                        'changed_fields': [],
                        'ui_caching_started_at': 0}
            else:
                return self.create_not_own_ui_info(hero_2)

        with mock.patch('the_tale.game.heroes.objects.Hero.ui_info', get_ui_info):
            data = logic.form_game_info(self.account_1, is_own=True)

        self.assertEqual(data['account']['hero']['action']['data']['pvp'], 'actual')
        self.assertEqual(data['enemy']['hero']['action']['data']['pvp'], 'last_turn')

        self.assertFalse('pvp__actual' in data['account']['hero']['action']['data']['pvp'])
        self.assertFalse('pvp__last_turn' in data['account']['hero']['action']['data']['pvp'])
        self.assertFalse('pvp__actual' in data['enemy']['hero']['action']['data']['pvp'])
        self.assertFalse('pvp__last_turn' in data['enemy']['hero']['action']['data']['pvp'])

        self.assertEqual(data['enemy']['energy'], None)
