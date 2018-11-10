
import smart_imports

smart_imports.all()


class TestRequestsBase(utils_testcase.TestCase, helpers.PvPTestsMixin):

    def setUp(self):
        super(TestRequestsBase, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.hero_1 = heroes_logic.load_hero(account_id=self.account_1.id)
        self.hero_2 = heroes_logic.load_hero(account_id=self.account_2.id)

        self.request_login(self.account_1.email)


class TestRequests(TestRequestsBase):

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(django_reverse('game:pvp:'), accounts_logic.login_page_url(django_reverse('game:pvp:')))

    def test_game_page_when_pvp_in_queue(self):
        self.pvp_create_battle(self.account_1, None)
        self.pvp_create_battle(self.account_2, None)
        self.check_redirect(django_reverse('game:pvp:'), django_reverse('game:'))

    def test_game_page_when_pvp_prepairing(self):
        self.pvp_create_battle(self.account_1, self.account_2)
        self.pvp_create_battle(self.account_2, self.account_1)
        self.check_redirect(django_reverse('game:pvp:'), django_reverse('game:'))

    def test_game_page_when_pvp_processing(self):
        self.pvp_create_battle(self.account_1, self.account_2, relations.BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, relations.BATTLE_1X1_STATE.PROCESSING)
        self.check_html_ok(self.client.get(django_reverse('game:pvp:')), texts=[])

    def test_game_page__not_in_ratings(self):
        self.pvp_create_battle(self.account_1, self.account_2, relations.BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, relations.BATTLE_1X1_STATE.PROCESSING)
        self.check_html_ok(self.client.get(django_reverse('game:pvp:')), texts=[('pgf-battle-not-in-rating', 1)])

    def test_game_page__in_ratings(self):
        self.pvp_create_battle(self.account_1, self.account_2, relations.BATTLE_1X1_STATE.PROCESSING, calculate_rating=True)
        self.pvp_create_battle(self.account_2, self.account_1, relations.BATTLE_1X1_STATE.PROCESSING, calculate_rating=True)
        self.check_html_ok(self.client.get(django_reverse('game:pvp:')), texts=[('pgf-battle-not-in-rating', 0)])


class SayRequestsTests(TestRequestsBase):

    def test_no_battle(self):
        self.check_ajax_error(self.client.post(django_reverse('game:pvp:say'), {'text': 'some text'}), 'pvp.say.no_battle')

    def test_battle_not_in_processing_state(self):
        self.pvp_create_battle(self.account_1, None)
        self.check_ajax_error(self.client.post(django_reverse('game:pvp:say'), {'text': 'some text'}), 'pvp.say.no_battle')

    def test_form_errors(self):
        self.pvp_create_battle(self.account_1, self.account_2, relations.BATTLE_1X1_STATE.PROCESSING)
        self.check_ajax_error(self.client.post(django_reverse('game:pvp:say'), {'text': ''}), 'pvp.say.form_errors')

    def test_success(self):
        self.pvp_create_battle(self.account_1, self.account_2, relations.BATTLE_1X1_STATE.PROCESSING)
        response = self.client.post(django_reverse('game:pvp:say'), {'text': 'some text'})
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)


class UsePvPAbilityRequestsTests(TestRequestsBase):

    def setUp(self):
        super(UsePvPAbilityRequestsTests, self).setUp()
        self.ability = random.choice(list(abilities.ABILITIES.values()))
        self.change_style_url = dext_urls.url('game:pvp:use-ability', ability=self.ability.TYPE)

    def test_no_battle(self):
        self.check_ajax_error(self.client.post(self.change_style_url), 'pvp.use_ability.no_battle')

    def test_battle_not_in_processing_state(self):
        self.pvp_create_battle(self.account_1, None)
        self.check_ajax_error(self.client.post(self.change_style_url), 'pvp.use_ability.no_battle')

    def test_wrong_style_id(self):
        self.pvp_create_battle(self.account_1, self.account_2, relations.BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_1, None)
        self.check_ajax_error(self.client.post(dext_urls.url('game:pvp:use-ability', ability=666)), 'pvp.ability.wrong_format')

    def test_success(self):
        self.pvp_create_battle(self.account_1, self.account_2, relations.BATTLE_1X1_STATE.PROCESSING)
        response = self.client.post(self.change_style_url)
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)


class TestCallsPage(TestRequestsBase):

    def setUp(self):
        super(TestCallsPage, self).setUp()

    def test_anonimouse(self):
        self.request_logout()
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pgf-level-restrictions-message', 0),
                                                                                     ('pgf-unlogined-message', 1),
                                                                                     ('pgf-no-current-battles-message', 1),
                                                                                     ('pgf-fast-account-message', 0)])

    def test_fast_user(self):
        self.account_1.is_fast = True
        self.account_1.save()
        self.hero_1.is_fast = True
        heroes_logic.save_hero(self.hero_1)
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('common.fast_account', 0),
                                                                                     ('pgf-level-restrictions-message', 0),
                                                                                     ('pgf-unlogined-message', 0),
                                                                                     ('pgf-no-current-battles-message', 1),
                                                                                     ('pgf-fast-account-message', 1)])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_participate_in_pvp', False)
    def test_no_rights(self):
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pvp.no_rights', 0),
                                                                                     ('pgf-level-restrictions-message', 0),
                                                                                     ('pgf-unlogined-message', 0),
                                                                                     ('pgf-no-current-battles-message', 1),
                                                                                     ('pgf-fast-account-message', 1)])

    def test_normal_account(self):
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pgf-level-restrictions-message', 1),
                                                                                     ('pgf-unlogined-message', 0),
                                                                                     ('pgf-no-current-battles-message', 1),
                                                                                     ('pgf-fast-account-message', 0)])

    def test_no_battles(self):
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pgf-no-calls-message', 1),
                                                                                     ('pgf-no-current-battles-message', 1), ])

    def test_own_battle(self):
        self.pvp_create_battle(self.account_1, None, relations.BATTLE_1X1_STATE.WAITING)
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pgf-no-calls-message', 0),
                                                                                     ('pgf-no-current-battles-message', 1),
                                                                                     ('pgf-own-battle-message', 1)])

    def test_low_level_battle(self):
        self.hero_1.level = 100
        heroes_logic.save_hero(self.hero_1)
        self.pvp_create_battle(self.account_2, None, relations.BATTLE_1X1_STATE.WAITING)
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pgf-no-calls-message', 0),
                                                                                     ('pgf-no-current-battles-message', 1),
                                                                                     ('pgf-can-not-accept-call', 1)])

    def test_height_level_battle(self):
        self.hero_2.level = 100
        heroes_logic.save_hero(self.hero_2)
        self.pvp_create_battle(self.account_2, None, relations.BATTLE_1X1_STATE.WAITING)
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pgf-no-calls-message', 0),
                                                                                     ('pgf-no-current-battles-message', 1),
                                                                                     ('pgf-can-not-accept-call', 1)])

    def test_battle(self):
        self.pvp_create_battle(self.account_2, None, relations.BATTLE_1X1_STATE.WAITING)
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pgf-no-calls-message', 0),
                                                                                     ('pgf-no-current-battles-message', 1),
                                                                                     ('pgf-accept-battle', 1)])

    def test_current_battle(self):
        self.pvp_create_battle(self.account_2, self.account_1, relations.BATTLE_1X1_STATE.PROCESSING)
        self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pgf-no-calls-message', 1),
                                                                                     ('pgf-no-current-battles-message', 0),
                                                                                     ('pgf-accept-battle', 0),
                                                                                     jinja2.escape(self.hero_1.name),
                                                                                     jinja2.escape(self.hero_2.name)])

    def test_only_waiting_and_processing_battles(self):
        for state in relations.BATTLE_1X1_STATE.records:
            if state.is_WAITING or state.is_PROCESSING:
                continue
            self.pvp_create_battle(self.account_2, None, state)
            self.check_html_ok(self.client.get(django_reverse('game:pvp:calls')), texts=[('pgf-no-calls-message', 1), ('pgf-no-current-battles-message', 1)])
            models.Battle1x1.objects.all().delete()
