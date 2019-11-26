
import smart_imports

smart_imports.all()


class BaseRequestsTests(utils_testcase.TestCase,
                        clans_helpers.ClansTestsMixin,
                        helpers.EmissariesTestsMixin):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        self.prepair_forum_for_clans()

        clans_tt_services.currencies.cmd_debug_clear_service()

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

        clans_tt_services.chronicle.cmd_debug_clear_service()

        self.emissary = self.create_emissary(clan=self.clan_1,
                                             initiator=self.account_1,
                                             place_id=self.places[0].id)

        concrete_event = events.Rest(raw_ability_power=100500)

        self.event = logic.create_event(initiator=self.account_1,
                                        emissary=self.emissary,
                                        concrete_event=concrete_event,
                                        days=7)

        self.url = dext_urls.url('game:emissaries:show', self.emissary.id)

    def test_success__unauthorized(self):
        self.request_logout()

        self.check_html_ok(self.request_html(self.url), texts=[('pgf-event-operation', 0)])

    def test_success__authorized_clan_member__no_permission(self):
        clans_logic.change_role(self.clan_1,
                                initiator=self.account_1,
                                member=self.account_1,
                                new_role=clans_relations.MEMBER_ROLE.RECRUIT)

        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.url), texts=[('pgf-event-operation', 0)])

    def test_success__authorized_clan_member__has_permission(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.url), texts=['pgf-event-operation'])

    def test_success__other_clan_member(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(owner=account_2, uid=2)

        self.request_login(account_2.email)

        self.check_html_ok(self.request_html(self.url), texts=[('pgf-event-operation', 0)])

    def test_success__authorized_not_clan_member(self):
        account_2 = self.accounts_factory.create_account()
        self.request_login(account_2.email)
        self.check_html_ok(self.request_html(self.url), texts=[('pgf-event-operation', 0)])


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

        self.check_html_ok(self.request_ajax_html(self.url), texts=['clans.no_rights'])

    def test_has_no_rights__wrong_role(self):
        clans_logic.change_role(self.clan_1,
                                initiator=self.account_1,
                                member=self.account_1,
                                new_role=clans_relations.MEMBER_ROLE.RECRUIT)

        self.check_html_ok(self.request_ajax_html(self.url), texts=['clans.no_rights'])

    def test_maximum_emissaries_reached(self):
        clan_attributes = clans_logic.load_attributes(self.clan_1.id)

        for i in range(clan_attributes.emissary_maximum):
            self.create_emissary(clan=self.clan_1,
                                 initiator=self.account_1,
                                 place_id=self.places[0].id)

        self.check_html_ok(self.request_ajax_html(self.url), texts=['emissaries.maximum_emissaries'])

    def test_success(self):
        self.check_html_ok(self.request_ajax_html(self.url), texts=[('clans.no_rights', 0),
                                                                    'form'])


class CreateTests(BaseRequestsTests):

    def setUp(self):
        super().setUp()
        self.url = dext_urls.url('game:emissaries:create')

        clans_tt_services.currencies.cmd_debug_clear_service()

        game_tt_services.debug_clear_service()

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

    def test_maximum_emissaries_reached(self):

        clan_attributes = clans_logic.load_attributes(self.clan_1.id)

        for i in range(clan_attributes.emissary_maximum):
            self.create_emissary(clan=self.clan_1,
                                 initiator=self.account_1,
                                 place_id=self.places[0].id)

        with self.check_no_changes_in_emissaries(self.clan_1):
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'emissaries.maximum_emissaries')

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


class StartEventDialogTests(BaseRequestsTests):

    def setUp(self):
        super().setUp()

        self.emissary = self.create_emissary(clan=self.clan_1,
                                             initiator=self.account_1,
                                             place_id=self.places[0].id)

        self.url = dext_urls.url('game:emissaries:start-event-dialog', self.emissary.id, event_type=relations.EVENT_TYPE.REST.value)

        self.request_login(self.account_1.email)

    def test_no_event_type(self):
        url = dext_urls.url('game:emissaries:start-event-dialog', self.emissary.id)

        self.check_html_ok(self.request_ajax_html(url), texts=['event_type.not_specified'])

    def test_not_authenticated(self):
        self.request_logout()
        self.check_html_ok(self.request_ajax_html(self.url), texts=['common.login_required'])

    def test_has_no_rights__not_member(self):
        account = self.accounts_factory.create_account()

        self.request_login(account.email)

        self.check_html_ok(self.request_ajax_html(self.url), texts=['emissaries.no_rights'])

    def test_has_no_rights__wrong_role(self):
        clans_logic.change_role(self.clan_1,
                                initiator=self.account_1,
                                member=self.account_1,
                                new_role=clans_relations.MEMBER_ROLE.RECRUIT)

        self.check_html_ok(self.request_ajax_html(self.url), texts=['emissaries.no_rights'])

    def test_has_no_rights__wrong_clan(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(owner=account_2, uid=2)

        self.request_login(account_2.email)

        self.check_html_ok(self.request_ajax_html(self.url), texts=['emissaries.no_rights'])

    def test_success(self):
        self.check_html_ok(self.request_ajax_html(self.url), texts=[('emissaries.no_rights', 0),
                                                                     'form'])


class StartEventTests(BaseRequestsTests):

    def setUp(self):
        super().setUp()

        self.emissary = self.create_emissary(clan=self.clan_1,
                                             initiator=self.account_1,
                                             place_id=self.places[0].id)

        self.url = dext_urls.url('game:emissaries:start-event', self.emissary.id, event_type=relations.EVENT_TYPE.REST.value)

        self.request_login(self.account_1.email)

        clans_tt_services.currencies.cmd_debug_clear_service()

        game_tt_services.debug_clear_service()

        clans_tt_services.currencies.cmd_change_balance(account_id=self.clan_1.id,
                                                        type='test',
                                                        autocommit=True,
                                                        amount=tt_clans_constants.MAXIMUM_POINTS)

        self.power = 10005000

        politic_power_logic.add_power_impacts([game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                            actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                            actor_id=self.account_1.id,
                                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                            target_id=self.emissary.id,
                                                                            amount=self.power)])

    @contextlib.contextmanager
    def check_no_actions_applied(self):

        def get_points():
            return clans_tt_services.currencies.cmd_balance(self.clan_1.id,
                                                            currency=clans_relations.CURRENCY.ACTION_POINTS)

        with self.check_not_changed(models.Event.objects.count):
            with self.check_not_changed(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])):
                with self.check_not_changed(get_points):
                    yield

    def get_post_data(self):
        return {'period': 7}

    def test_no_authenticated(self):
        self.request_logout()

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'common.login_required')

    def test_no_rights__wrong_role(self):
        clans_logic.change_role(self.clan_1,
                                initiator=self.account_1,
                                member=self.account_1,
                                new_role=clans_relations.MEMBER_ROLE.RECRUIT)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'emissaries.no_rights')

    def test_no_rights__member_of_other_clan(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(owner=account_2, uid=2)

        self.request_login(account_2.email)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'emissaries.no_rights')

    def test_no_rights__not_member(self):
        account_2 = self.accounts_factory.create_account()

        self.request_login(account_2.email)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'emissaries.no_rights')

    def test_no_action_points(self):
        clans_tt_services.currencies.cmd_change_balance(account_id=self.clan_1.id,
                                                        type='test',
                                                        autocommit=True,
                                                        amount=-tt_clans_constants.MAXIMUM_POINTS)

        clan_points = clans_tt_services.currencies.cmd_balance(self.clan_1.id,
                                                               currency=clans_relations.CURRENCY.ACTION_POINTS)

        self.assertEqual(clan_points, 0)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'clans.no_enought_clan_points')

    def test_no_power(self):

        politic_power_logic.add_power_impacts([game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                            actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                            actor_id=self.account_1.id,
                                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                            target_id=self.emissary.id,
                                                                            amount=-self.power * 10)])
        self.assertTrue(politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id] < 0)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'emissaies.no_enough_power')

    def test_success(self):

        def get_points():
            return clans_tt_services.currencies.cmd_balance(self.clan_1.id,
                                                            currency=clans_relations.CURRENCY.ACTION_POINTS)

        with self.check_delta(models.Event.objects.count, 1):
            with self.check_decreased(lambda: politic_power_logic.get_emissaries_power([self.emissary.id])[self.emissary.id]):
                with self.check_decreased(get_points):
                    self.check_ajax_ok(self.post_ajax_json(self.url, self.get_post_data()))

    def test_dublicate_event(self):
        self.check_ajax_ok(self.post_ajax_json(self.url, self.get_post_data()))

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'emissaies.dublicate_event')

    def test_maximum_simultaneously_events(self):
        logic.create_event(initiator=self.account_1,
                           emissary=self.emissary,
                           concrete_event=events.Rest(raw_ability_power=100500),
                           days=7)

        logic.create_event(initiator=self.account_1,
                           emissary=self.emissary,
                           concrete_event=events.Dismiss(raw_ability_power=100500),
                           days=7)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'emissaies.maximum_simultaneously_events')

    def test_on_create_failed(self):

        @contextlib.contextmanager
        def on_create(event, emissary):
            raise exceptions.OnEventCreateError(message='test error')
            yield

        with mock.patch('the_tale.game.emissaries.events.EventBase.on_create', on_create):
            with self.check_no_actions_applied():
                self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'emissaries.on_create_error')

    def test_event_not_available(self):

        @classmethod
        def is_available(event_class, emissary, active_events):
            return False

        with mock.patch('the_tale.game.emissaries.events.EventBase.is_available', is_available):
            with self.check_no_actions_applied():
                self.check_ajax_error(self.post_ajax_json(self.url, self.get_post_data()), 'emissaries.event_not_available')

    def test_success__after_create_called(self):

        places_tt_services.effects.cmd_debug_clear_service()

        url = dext_urls.url('game:emissaries:start-event', self.emissary.id, event_type=relations.EVENT_TYPE.ARTISANS_SUPPORT.value)

        self.emissary.place_rating_position = 0

        with self.check_delta(lambda: len(places_storage.effects.all()), 1):
            self.check_ajax_ok(self.post_ajax_json(url, self.get_post_data()))

    def check_event_rights(self, event_type):
        clans_logic.change_role(self.clan_1,
                                initiator=self.account_1,
                                member=self.account_1,
                                new_role=clans_relations.MEMBER_ROLE.OFFICER)

        rights = clans_logic.operations_rights(initiator=self.account_1,
                                               clan=self.clan_1,
                                               is_moderator=False)

        self.assertTrue(rights.can_emissaries_planing())
        self.assertFalse(rights.can_emissaries_relocation())

        places_tt_services.effects.cmd_debug_clear_service()

        url = dext_urls.url('game:emissaries:start-event', self.emissary.id, event_type=event_type.value)

        self.emissary.place_rating_position = 0

        with self.check_not_changed(lambda: len(places_storage.effects.all())):
            self.check_ajax_error(self.post_ajax_json(url, self.get_post_data()), 'emissaries.no_rights')

    def test_restricted_move_event(self):
        self.check_event_rights(relations.EVENT_TYPE.RELOCATION)

    def test_restricted_dismiss_event(self):
        self.check_event_rights(relations.EVENT_TYPE.DISMISS)


class StopEventTests(BaseRequestsTests):

    def setUp(self):
        super().setUp()

        self.emissary = self.create_emissary(clan=self.clan_1,
                                             initiator=self.account_1,
                                             place_id=self.places[0].id)

        concrete_event = events.Rest(raw_ability_power=100500)

        self.event = logic.create_event(initiator=self.account_1,
                                        emissary=self.emissary,
                                        concrete_event=concrete_event,
                                        days=7)

        self.url = dext_urls.url('game:emissaries:stop-event', self.emissary.id, event=self.event.id)

        self.request_login(self.account_1.email)

        clans_tt_services.currencies.cmd_debug_clear_service()

        game_tt_services.debug_clear_service()

    @contextlib.contextmanager
    def check_no_actions_applied(self):

        with self.check_not_changed(models.Event.objects.filter(state=relations.EVENT_STATE.RUNNING).count):
            yield

    def test_no_authenticated(self):
        self.request_logout()

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url), 'common.login_required')

    def test_no_rights__wrong_role(self):
        clans_logic.change_role(self.clan_1,
                                initiator=self.account_1,
                                member=self.account_1,
                                new_role=clans_relations.MEMBER_ROLE.RECRUIT)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url), 'emissaries.no_rights')

    def test_no_rights__member_of_other_clan(self):
        account_2 = self.accounts_factory.create_account()
        self.create_clan(owner=account_2, uid=2)

        self.request_login(account_2.email)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url), 'emissaries.no_rights')

    def test_no_rights__not_member(self):
        account_2 = self.accounts_factory.create_account()

        self.request_login(account_2.email)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(self.url), 'emissaries.no_rights')

    def test_success(self):
        with self.check_delta(models.Event.objects.filter(state=relations.EVENT_STATE.RUNNING).count, -1):
            with self.check_delta(models.Event.objects.filter(state=relations.EVENT_STATE.STOPPED).count, 1):
                self.check_ajax_ok(self.post_ajax_json(self.url))

        event = logic.load_event(self.event.id)

        self.assertTrue(event.state.is_STOPPED)

    def test_success__already_stopped(self):
        with self.check_delta(models.Event.objects.filter(state=relations.EVENT_STATE.RUNNING).count, -1):
            with self.check_delta(models.Event.objects.filter(state=relations.EVENT_STATE.STOPPED).count, 1):
                self.check_ajax_ok(self.post_ajax_json(self.url))

        with self.check_no_actions_applied():
            self.check_ajax_ok(self.post_ajax_json(self.url))

        event = logic.load_event(self.event.id)

        self.assertTrue(event.state.is_STOPPED)

    def test_wrong_emissary(self):

        wrong_emissary = self.create_emissary(clan=self.clan_1,
                                              initiator=self.account_1,
                                              place_id=self.places[0].id)

        url = dext_urls.url('game:emissaries:stop-event', wrong_emissary.id, event=self.event.id)

        with self.check_no_actions_applied():
            self.check_ajax_error(self.post_ajax_json(url), 'emissaries.wrong_emissary')
