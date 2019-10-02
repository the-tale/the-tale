
import smart_imports

smart_imports.all()


class BaseRequestsTests(utils_testcase.TestCase,
                        clans_helpers.ClansTestsMixin,
                        helpers.EmissariesTestsMixin):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        self.prepair_forum_for_clans()

        self.account_1 = self.accounts_factory.create_account()
        self.clan_1 = self.create_clan(owner=self.account_1, uid=1)

    @contextlib.contextmanager
    def check_no_changes_in_emissaries(self, clan):
        with self.check_not_changed(lambda: logic.load_emissaries_for_clan(clan.id)):
            with self.check_not_changed(lambda: clans_tt_services.currencies.cmd_balance(clan.id)):
                yield


class ShowTests(BaseRequestsTests):

    def setUp(self):
        super().setUp()
        self.emissary = self.create_emissary(clan=self.clan_1,
                                             initiator=self.account_1,
                                             place_id=self.places[0].id)

        self.url = dext_urls.url('game:emissaries:show', self.emissary.id)

    def test_success__unauthorized(self):
        self.request_logout()

        self.check_html_ok(self.request_html(self.url), texts=[])

    def test_success__authorized_clan_member(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.url), texts=[])

    def test_success__authorized_not_clan_member(self):
        account_2 = self.accounts_factory.create_account()
        self.request_login(account_2.email)
        self.check_html_ok(self.request_html(self.url), texts=[])


class CreateDialogTests(BaseRequestsTests):

    def setUp(self):
        super().setUp()
        self.url = dext_urls.url('game:emissaries:create-dialog')

        self.request_login(self.account_1.email)

    def test_not_authenticated(self):
        self.request_logout()
        self.check_html_ok(self.request_ajax_html(self.url), texts=['common.login_required'])

    def test_has_no_rights__not_member(self):
        account = self.accounts_factory.create_account()

        self.request_login(account.email)

        self.check_html_ok(self.request_html(self.url), texts=['clans.no_rights'])

    def test_has_no_rights__wrong_role(self):
        clans_logic.change_role(self.clan_1,
                                initiator=self.account_1,
                                member=self.account_1,
                                new_role=clans_relations.MEMBER_ROLE.RECRUIT)

        self.check_html_ok(self.request_html(self.url), texts=['clans.no_rights'])

    def test_success(self):
        self.check_html_ok(self.request_html(self.url), texts=[('clans.no_rights', 0),
                                                               'form'])


class CreateTests(BaseRequestsTests):

    def setUp(self):
        super().setUp()
        self.url = dext_urls.url('game:emissaries:create')

        clans_tt_services.currencies.cmd_debug_clear_service()

        clans_tt_services.currencies.cmd_change_balance(account_id=self.clan_1.id,
                                                        type='test',
                                                        autocommit=True,
                                                        amount=tt_clans_constants.PRICE_CREATE_EMISSARY + 1)

        self.request_login(self.account_1.email)

    def get_post_data(self):
        return {'gender': game_relations.GENDER.MALE,
                'race': game_relations.RACE.DWARF,
                'place': self.places[0].id}

    def test_not_authenticated(self):
        self.request_logout()

        with self.check_no_changes_in_emissaries(self.clan_1):
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'common.login_required')

    def test_has_no_rights__not_member(self):
        account = self.accounts_factory.create_account()

        self.request_login(account.email)

        with self.check_no_changes_in_emissaries(self.clan_1):
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'clans.no_rights')

    def test_has_no_rights__wrong_role(self):
        clans_logic.change_role(self.clan_1,
                                initiator=self.account_1,
                                member=self.account_1,
                                new_role=clans_relations.MEMBER_ROLE.RECRUIT)

        with self.check_no_changes_in_emissaries(self.clan_1):
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'clans.no_rights')

    def test_wrong_form(self):
        with self.check_no_changes_in_emissaries(self.clan_1):
            self.check_ajax_error(self.post_ajax_json(self.url, {}), 'form_errors')

    def test_no_points(self):
        balance = clans_tt_services.currencies.cmd_balance(account_id=self.clan_1.id,
                                                           currency=clans_relations.CURRENCY.ACTION_POINTS)
        clans_tt_services.currencies.cmd_change_balance(account_id=self.clan_1.id,
                                                        type='test',
                                                        autocommit=True,
                                                        amount=-balance)

        with self.check_no_changes_in_emissaries(self.clan_1):
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'clans.no_enought_clan_points')

    def test_success(self):
        with self.check_changed(lambda: logic.load_emissaries_for_clan(self.clan_1.id)):
            with self.check_delta(lambda: clans_tt_services.currencies.cmd_balance(self.clan_1.id,
                                                                                   currency=clans_relations.CURRENCY.ACTION_POINTS),
                                  -tt_clans_constants.PRICE_CREATE_EMISSARY):
                self.check_ajax_ok(self.post_ajax_json(self.url, self.get_post_data()))

        emissaries = logic.load_emissaries_for_clan(self.clan_1.id)

        self.assertEqual(len(emissaries), 1)

        self.assertTrue(emissaries[0].state.is_IN_GAME)
        self.assertTrue(emissaries[0].gender.is_MALE)
        self.assertTrue(emissaries[0].race.is_DWARF)
        self.assertEqual(emissaries[0].place_id, self.places[0].id)
