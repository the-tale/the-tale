
import smart_imports

smart_imports.all()


class InitiateBattleTests(helpers.PvPTestsMixin, utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.request_login(self.account_1.email)

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

    def test(self):
        result, battle_id = tt_services.matchmaker.cmd_create_battle(matchmaker_type=relations.MATCHMAKER_TYPE.BOT,
                                                                     participants_ids=(self.account_1.id, self.account_2.id))

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_add_task') as cmd_add_task:
            supervisor_task = logic.initiate_battle(initiator_id=self.account_1.id,
                                                    acceptor_id=self.account_2.id,
                                                    battle_id=battle_id)

        self.assertEqual(cmd_add_task.call_args_list, [mock.call(supervisor_task.id)])

        supervisor_task.capture_member(self.account_1.id)
        supervisor_task.capture_member(self.account_2.id)

        supervisor_task.process(bundle_id=100500)

        self.assertTrue(isinstance(heroes_logic.load_hero(self.account_1.id).actions.current_action.meta_action,
                                   actions_meta_actions.ArenaPvP1x1))


class ArenaInfoTests(clans_helpers.ClansTestsMixin,
                     helpers.PvPTestsMixin,
                     utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=clans_conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.clan_1 = self.create_clan(owner=self.account_1, uid=1)
        self.clan_2 = self.create_clan(owner=self.account_2, uid=2)

        self.hero_1 = heroes_logic.load_hero(self.account_1.id)
        self.hero_2 = heroes_logic.load_hero(self.account_2.id)

    def test_no_requests(self):
        info = logic.arena_info()
        self.assertEqual(info,
                         {'accounts': {},
                          'active_arena_battles': 0,
                          'active_bot_battles': 0,
                          'arena_battle_requests': [],
                          'clans': {}})

    def test_has_requests_and_battles(self):
        battle_request_id = tt_services.matchmaker.cmd_create_battle_request(matchmaker_type=relations.MATCHMAKER_TYPE.ARENA,
                                                                             initiator_id=self.account_1.id)

        for i in range(3):
            account_x = self.accounts_factory.create_account()
            account_y = self.accounts_factory.create_account()

            result, battle_id = tt_services.matchmaker.cmd_create_battle(matchmaker_type=relations.MATCHMAKER_TYPE.BOT,
                                                                         participants_ids=(account_x.id, account_y.id))

        for i in range(2):
            account_x = self.accounts_factory.create_account()
            account_y = self.accounts_factory.create_account()

            result, battle_id = tt_services.matchmaker.cmd_create_battle(matchmaker_type=relations.MATCHMAKER_TYPE.ARENA,
                                                                         participants_ids=(account_x.id, account_y.id))

        info = logic.arena_info()

        accounts_info = game_logic.accounts_info((self.account_1.id,))

        self.assertEqual(info,
                         {'accounts': accounts_info,
                          'active_arena_battles': 2,
                          'active_bot_battles': 3,
                          'arena_battle_requests': [{'created_at': info['arena_battle_requests'][0]['created_at'],
                                                     'id': battle_request_id,
                                                     'initiator_id': self.account_1.id,
                                                     'matchmaker_type': relations.MATCHMAKER_TYPE.ARENA.value,
                                                     'updated_at': info['arena_battle_requests'][0]['updated_at']}],
                          'clans': game_logic.clans_info(accounts_info)})


class GetEnemyIdTests(helpers.PvPTestsMixin,
                      utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

    def test_no_battle(self):
        account = self.accounts_factory.create_account()

        self.assertEqual(logic.get_enemy_id(account.id), None)

    def test_has_battle(self):
        battle_info = self.create_pvp_battle()

        self.assertEqual(logic.get_enemy_id(battle_info.account_1.id), battle_info.account_2.id)
        self.assertEqual(logic.get_enemy_id(battle_info.account_2.id), battle_info.account_1.id)


class GetArenaHeroesTests(helpers.PvPTestsMixin,
                          utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

    def test_not_in_battle(self):
        account = self.accounts_factory.create_account()

        hero = heroes_logic.load_hero(account.id)

        original_hero, enemy = logic.get_arena_heroes(hero)

        self.assertEqual(original_hero, hero)
        self.assertEqual(enemy, None)

    def test_in_battle(self):
        battle_info = self.create_pvp_battle()

        self.assertEqual(logic.get_arena_heroes(battle_info.hero_1), (battle_info.hero_1, battle_info.hero_2))
        self.assertEqual(logic.get_arena_heroes(battle_info.hero_2), (battle_info.hero_2, battle_info.hero_1))


class GetArenaHeroesPvPTests(helpers.PvPTestsMixin,
                             utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

    def test_not_in_battle(self):
        account = self.accounts_factory.create_account()

        hero = heroes_logic.load_hero(account.id)

        original_hero_pvp, enemy_pvp = logic.get_arena_heroes_pvp(hero)

        self.assertEqual(original_hero_pvp, None)
        self.assertEqual(enemy_pvp, None)

    def test_in_battle(self):
        battle_info = self.create_pvp_battle()

        self.assertEqual(logic.get_arena_heroes_pvp(battle_info.hero_1),
                         (battle_info.hero_1.actions.current_action.meta_action.hero_1_pvp,
                          battle_info.hero_1.actions.current_action.meta_action.hero_2_pvp))
        self.assertEqual(logic.get_arena_heroes_pvp(battle_info.hero_2),
                         (battle_info.hero_2.actions.current_action.meta_action.hero_2_pvp,
                          battle_info.hero_2.actions.current_action.meta_action.hero_1_pvp))


class CalculateRatingRequiredTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

    def test_bots(self):
        player = self.accounts_factory.create_account()
        bot = self.accounts_factory.create_account(is_bot=True)

        player_hero = heroes_logic.load_hero(player.id)
        bot_hero = heroes_logic.load_hero(bot.id)

        self.assertFalse(logic.calculate_rating_required(player_hero, bot_hero))
        self.assertFalse(logic.calculate_rating_required(bot_hero, player_hero))

    def test_level_difference(self):
        player_1 = self.accounts_factory.create_account()
        player_2 = self.accounts_factory.create_account()

        hero_1 = heroes_logic.load_hero(player_1.id)
        hero_2 = heroes_logic.load_hero(player_2.id)

        hero_2.level = hero_1.level + conf.settings.MAX_RATING_LEVEL_DELTA + 1
        self.assertFalse(logic.calculate_rating_required(hero_1, hero_2))
        self.assertFalse(logic.calculate_rating_required(hero_2, hero_1))

        hero_2.level = hero_1.level + conf.settings.MAX_RATING_LEVEL_DELTA
        self.assertTrue(logic.calculate_rating_required(hero_1, hero_2))
        self.assertTrue(logic.calculate_rating_required(hero_2, hero_1))

        hero_2.level = hero_1.level + conf.settings.MAX_RATING_LEVEL_DELTA - 1
        self.assertTrue(logic.calculate_rating_required(hero_1, hero_2))
        self.assertTrue(logic.calculate_rating_required(hero_2, hero_1))
