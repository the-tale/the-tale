
import smart_imports

smart_imports.all()


class TestRequestsBase(utils_testcase.TestCase, helpers.PvPTestsMixin):

    def setUp(self):
        super(TestRequestsBase, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.request_login(self.account_1.email)

        pvp_tt_services.matchmaker.cmd_debug_clear_service()


class TestPvPPageRequests(TestRequestsBase):

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(django_reverse('game:pvp:'), accounts_logic.login_page_url(django_reverse('game:pvp:')))

    def test_game_page_when_pvp_in_queue(self):
        self.check_ajax_ok(self.post_ajax_json(logic.pvp_call_to_arena_url()))
        self.check_redirect(django_reverse('game:pvp:'), django_reverse('game:'))

    def test_game_page_when_pvp_battle_is_running(self):
        self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)
        self.check_html_ok(self.request_html(django_reverse('game:pvp:')), texts=[])

    @mock.patch('the_tale.game.pvp.logic.calculate_rating_required', lambda *argv, **kwargs: False)
    def test_game_page__not_in_ratings(self):
        self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)
        self.check_html_ok(self.request_html(django_reverse('game:pvp:')), texts=[('pgf-battle-not-in-rating', 1)])

    @mock.patch('the_tale.game.pvp.logic.calculate_rating_required', lambda *argv, **kwargs: True)
    def test_game_page__in_ratings(self):
        self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)
        self.check_html_ok(self.request_html(django_reverse('game:pvp:')), texts=[('pgf-battle-not-in-rating', 0)])


class SayRequestsTests(TestRequestsBase):

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(django_reverse('game:pvp:say')), 'common.login_required')

    def test_no_battle(self):
        response = self.client.post(django_reverse('game:pvp:say'), {'text': 'some text'})
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)

    def test_form_errors(self):
        self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)
        self.check_ajax_error(self.client.post(django_reverse('game:pvp:say'), {'text': ''}), 'form_errors')

    def test_success(self):
        self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)
        response = self.client.post(django_reverse('game:pvp:say'), {'text': 'some text'})
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)


class UsePvPAbilityRequestsTests(TestRequestsBase):

    def setUp(self):
        super().setUp()
        self.ability = random.choice(list(abilities.ABILITIES.values()))
        self.change_style_url = utils_urls.url('game:pvp:use-ability', ability=self.ability.TYPE)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.change_style_url), 'common.login_required')

    def test_no_battle(self):
        response = self.client.post(self.change_style_url)
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)

    def test_wrong_style_id(self):
        self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)
        self.check_ajax_error(self.client.post(utils_urls.url('game:pvp:use-ability', ability=666)), 'ability.wrong_format')

    def test_success(self):
        self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)

        response = self.client.post(self.change_style_url)
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)


class CallToArenaTests(TestRequestsBase):

    def setUp(self):
        super().setUp()
        self.request_url = logic.pvp_call_to_arena_url()

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.request_url), 'common.login_required')

    def test_battle_request_created(self):
        self.check_ajax_ok(self.post_ajax_json(self.request_url))

        battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=(relations.MATCHMAKER_TYPE.ARENA,))

        self.assertEqual(battle_requests[0].initiator_id, self.account_1.id)
        self.assertTrue(battle_requests[0].matchmaker_type.is_ARENA)


class LeaveArenaTests(TestRequestsBase):

    def setUp(self):
        super().setUp()
        self.request_url = logic.pvp_leave_arena_url()

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.request_url), 'common.login_required')

    def test_battle_request_created(self):
        self.check_ajax_ok(self.post_ajax_json(logic.pvp_call_to_arena_url()))

        battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=(relations.MATCHMAKER_TYPE.ARENA,))

        self.assertEqual(battle_requests[0].initiator_id, self.account_1.id)

        self.check_ajax_ok(self.post_ajax_json(self.request_url))

        battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=(relations.MATCHMAKER_TYPE.ARENA,))

        self.assertEqual(battle_requests, [])


class AcceptArenaBattleTests(TestRequestsBase):

    def setUp(self):
        super().setUp()
        self.battle_request_id = tt_services.matchmaker.cmd_create_battle_request(matchmaker_type=relations.MATCHMAKER_TYPE.ARENA,
                                                                                  initiator_id=self.account_2.id)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(logic.pvp_accept_arena_battle_url(battle_request_id=self.battle_request_id)),
                              'common.login_required')

    def test_no_battle_reuqest(self):
        self.check_ajax_error(self.post_ajax_json(logic.pvp_accept_arena_battle_url(battle_request_id=self.battle_request_id+1)),
                              'pvp.accept_arena_battle.no_battle_request_found')

        battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=relations.MATCHMAKER_TYPE.records)
        self.assertEqual(active_battles, {relations.MATCHMAKER_TYPE.BOT: 0,
                                          relations.MATCHMAKER_TYPE.ARENA: 0})

    def test_initiator_already_in_battle(self):
        account_3 = self.accounts_factory.create_account()

        result, battle_id = tt_services.matchmaker.cmd_create_battle(matchmaker_type=relations.MATCHMAKER_TYPE.BOT,
                                                                     participants_ids=(self.account_1.id, account_3.id))

        self.check_ajax_error(self.post_ajax_json(logic.pvp_accept_arena_battle_url(battle_request_id=self.battle_request_id)),
                              'pvp.accept_arena_battle.already_in_battle')

        battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=relations.MATCHMAKER_TYPE.records)
        self.assertEqual(active_battles, {relations.MATCHMAKER_TYPE.BOT: 1,
                                          relations.MATCHMAKER_TYPE.ARENA: 0})

    def test_success(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_add_task') as cmd_add_task:
            response = self.post_ajax_json(logic.pvp_accept_arena_battle_url(battle_request_id=self.battle_request_id))

        supervisor_task = game_prototypes.SupervisorTaskPrototype._db_get_object(0)
        self.assertEqual(cmd_add_task.call_args_list, [mock.call(supervisor_task.id)])

        self.check_ajax_processing(response, supervisor_task.status_url)

        battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=relations.MATCHMAKER_TYPE.records)
        self.assertEqual(battle_requests, [])
        self.assertEqual(active_battles, {relations.MATCHMAKER_TYPE.BOT: 0,
                                          relations.MATCHMAKER_TYPE.ARENA: 1})

        self.assertTrue(supervisor_task.type.is_ARENA_PVP_1X1)
        self.assertEqual(supervisor_task.members, {self.account_1.id, self.account_2.id})


class CreateArenaBotBattleTests(TestRequestsBase):

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(logic.pvp_create_arena_bot_battle_url()),
                              'common.login_required')

    def test_success(self):
        bot = self.accounts_factory.create_account(is_bot=True)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_add_task') as cmd_add_task:
            response = self.post_ajax_json(logic.pvp_create_arena_bot_battle_url())

        supervisor_task = game_prototypes.SupervisorTaskPrototype._db_get_object(0)
        self.assertEqual(cmd_add_task.call_args_list, [mock.call(supervisor_task.id)])

        self.check_ajax_processing(response, supervisor_task.status_url)

        self.assertTrue(supervisor_task.type.is_ARENA_PVP_1X1)
        self.assertEqual(supervisor_task.members, {self.account_1.id, bot.id})

        battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=relations.MATCHMAKER_TYPE.records)
        self.assertEqual(battle_requests, [])
        self.assertEqual(active_battles, {relations.MATCHMAKER_TYPE.BOT: 1,
                                          relations.MATCHMAKER_TYPE.ARENA: 0})

    def test_bot_limits(self):
        n = 10

        bots = [self.accounts_factory.create_account(is_bot=True)
                for i in range(n)]

        accounts = [self.accounts_factory.create_account()
                    for i in range(n)]

        for account in accounts:
            self.request_login(account.email)
            self.post_ajax_json(logic.pvp_create_arena_bot_battle_url())

        battle_requests, active_battles = tt_services.matchmaker.cmd_get_info(matchmaker_types=relations.MATCHMAKER_TYPE.records)
        self.assertEqual(battle_requests, [])
        self.assertEqual(active_battles, {relations.MATCHMAKER_TYPE.BOT: n,
                                          relations.MATCHMAKER_TYPE.ARENA: 0})

        bots_ids = {bot.id for bot in bots}
        accounts_ids = {account.id for account in accounts}

        for supervisor_task_model in game_prototypes.SupervisorTaskPrototype._db_all():
            supervisor_task = game_prototypes.SupervisorTaskPrototype(supervisor_task_model)
            participant_1_id, participant_2_id = list(supervisor_task.members)

            if participant_1_id in accounts_ids and participant_2_id in bots_ids:
                accounts_ids.remove(participant_1_id)
                bots_ids.remove(participant_2_id)
                continue

            if participant_2_id in accounts_ids and participant_1_id in bots_ids:
                accounts_ids.remove(participant_2_id)
                bots_ids.remove(participant_1_id)
                continue

            raise Exception('wrong participants distibution')

        self.assertFalse(bots_ids)
        self.assertFalse(accounts_ids)

        limited_account = self.accounts_factory.create_account()

        self.request_login(limited_account.email)

        self.check_ajax_error(self.post_ajax_json(logic.pvp_create_arena_bot_battle_url()), 'pvp.create_arena_bot_battle.no_free_bots')


class InfoTests(TestRequestsBase):

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.request_ajax_json(logic.pvp_info_url()),
                              'common.login_required')

    def test_no_requests(self):
        data = self.check_ajax_ok(self.request_ajax_json(logic.pvp_info_url()))
        self.assertEqual(data, {'info': logic.arena_info()})

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

        data = self.check_ajax_ok(self.request_ajax_json(logic.pvp_info_url()))
        self.assertEqual(data, {'info': s11n.from_json(s11n.to_json(logic.arena_info()))})
