
import smart_imports

smart_imports.all()


class BaseTestRequests(utils_testcase.TestCase, helpers.ClansTestsMixin, personal_messages_helpers.Mixin):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        forum_prototypes.CategoryPrototype.create(caption='category-1', slug=conf.settings.FORUM_CATEGORY_SLUG, order=0)

        self.account = self.accounts_factory.create_account()

        personal_messages_tt_services.personal_messages.cmd_debug_clear_service()

        tt_services.chronicle.cmd_debug_clear_service()
        tt_services.properties.cmd_debug_clear_service()
        tt_services.currencies.cmd_debug_clear_service()

    def check_no_righs__html(self, clan, url, permissions):
        account_2 = self.accounts_factory.create_account()
        self.request_login(account_2.email)

        # not clan_member
        self.check_html_ok(self.request_html(url), texts=['clans.no_rights'])

        # clan member with no rights
        for role in relations.MEMBER_ROLE.records:
            if any(permission in role.permissions for permission in permissions):
                continue

            member = self.accounts_factory.create_account()
            logic._add_member(clan=clan,
                              account=member,
                              role=role)
            self.request_login(member.email)
            self.check_html_ok(self.request_html(url), texts=['clans.no_rights'])

        # other clan member with rights
        account_3 = self.accounts_factory.create_account()
        self.create_clan(account_3, 1)
        self.request_login(account_3.email)

        self.check_html_ok(self.request_html(url), texts=['clans.no_rights'])

    def check_no_righs__ajax(self, clan, url, data, permission):
        account_2 = self.accounts_factory.create_account()
        self.request_login(account_2.email)

        # not clan_member
        self.check_ajax_error(self.post_ajax_json(url, data), 'clans.no_rights')

        # clan member with no rights
        for role in relations.MEMBER_ROLE.records:
            if permission in role.permissions:
                continue

            member = self.accounts_factory.create_account()
            logic._add_member(clan=clan,
                              account=member,
                              role=role)
            self.request_login(member.email)
            self.check_ajax_error(self.post_ajax_json(url, data), 'clans.no_rights')

        # other clan member with rights
        account_3 = self.accounts_factory.create_account()
        self.create_clan(account_3, 1)
        self.request_login(account_3.email)

        self.check_ajax_error(self.post_ajax_json(url, data), 'clans.no_rights')


class TestIndexRequests(BaseTestRequests):

    def setUp(self):
        super().setUp()

    def test_no_clans(self):
        self.check_html_ok(self.request_html(utils_urls.url('clans:')),
                           texts=[('pgf-no-clans-message', 1)])

    @mock.patch('the_tale.clans.conf.settings.CLANS_ON_PAGE', 4)
    def test_clans_2_pages(self):
        for i in range(6):
            self.create_clan(self.accounts_factory.create_account(), i)

        self.check_html_ok(self.request_html(utils_urls.url('clans:')),
                           texts=[('a-%d' % i, 1) for i in range(4)] + [('pgf-no-clans-message', 0)])

        self.check_html_ok(self.request_html(utils_urls.url('clans:', page=2)),
                           texts=[('a-%d' % i, 1) for i in range(4, 6)] + [('pgf-no-clans-message', 0)])

        self.check_redirect(utils_urls.url('clans:', page=3),
                            utils_urls.url('clans:', page=2, order_by=relations.ORDER_BY.ACTIVE_MEMBERS_NUMBER_DESC.value))


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.show_url = utils_urls.url('clans:show', self.clan.id)

    def test_ok(self):
        self.check_html_ok(self.request_html(self.show_url), texts=['pgf-no-folclor',
                                                                    self.clan.abbr,
                                                                    self.clan.name,
                                                                    self.clan.motto,
                                                                    self.clan.description_html,
                                                                    (self.clan.description, 0)])

    def test_ok__removed_clan(self):
        logic.remove_clan(self.clan)

        self.check_html_ok(self.request_html(self.show_url), texts=['pgf-no-folclor',
                                                                    self.clan.abbr,
                                                                    self.clan.name,
                                                                    self.clan.motto,
                                                                    self.clan.description_html,
                                                                    (self.clan.description, 0)])

    def test_redirect_from_old_urls(self):
        self.check_redirect('/accounts/clans/{}'.format(self.clan.id), self.show_url)

    def create_folclor(self):
        blogs_helpers.prepair_forum()

        blogs_helpers.create_post_for_meta_object(self.accounts_factory.create_account(),
                                                  'folclor-1-caption',
                                                  'folclor-1-text',
                                                  meta_relations.Clan.create_from_object(self.clan),
                                                  vote_by=self.account)

        blogs_helpers.create_post_for_meta_object(self.accounts_factory.create_account(),
                                                  'folclor-2-caption',
                                                  'folclor-2-text',
                                                  meta_relations.Clan.create_from_object(self.clan),
                                                  vote_by=self.account)

        blogs_helpers.create_post_for_meta_object(self.accounts_factory.create_account(),
                                                  'folclor-3-caption',
                                                  'folclor-3-text',
                                                  meta_relations.Clan.create_from_object(self.clan))

    def test_folclor(self):
        self.create_folclor()

        self.check_html_ok(self.request_html(self.show_url),
                           texts=[('pgf-no-folclor', 0),
                                  'folclor-1-caption',
                                  'folclor-2-caption',
                                  'folclor-3-caption'])

    def test_folclor__removed_clan(self):
        self.create_folclor()

        logic.remove_clan(self.clan)

        self.check_html_ok(self.request_html(self.show_url),
                           texts=[('pgf-no-folclor', 0),
                                  'folclor-1-caption',
                                  'folclor-2-caption',
                                  'folclor-3-caption'])

    def test_points_access(self):
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[('pgf-clans-points-amount', 0),
                                  ('pgf-clans-points-dummy', 1)])

        self.request_login(self.account.email)
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[('pgf-clans-points-amount', 1),
                                  ('pgf-clans-points-dummy', 0)])

        clan_2 = self.create_clan(self.accounts_factory.create_account(), 1)
        self.check_html_ok(self.request_html(utils_urls.url('clans:show', clan_2.id)),
                           texts=[('pgf-clans-points-amount', 0),
                                  ('pgf-clans-points-dummy', 1)])

    def test_free_quests_access(self):
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[('pgf-clans-free-quests-amount', 0),
                                  ('pgf-clans-free-quests-dummy', 1)])

        self.request_login(self.account.email)
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[('pgf-clans-free-quests-amount', 1),
                                  ('pgf-clans-free-quests-dummy', 0)])

        clan_2 = self.create_clan(self.accounts_factory.create_account(), 1)
        self.check_html_ok(self.request_html(utils_urls.url('clans:show', clan_2.id)),
                           texts=[('pgf-clans-free-quests-amount', 0),
                                  ('pgf-clans-free-quests-dummy', 1)])

    def test_experience_access(self):
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[('pgf-experience-amount', 0),
                                  ('pgf-experience-dummy', 1)])

        self.request_login(self.account.email)
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[('pgf-experience-amount', 1),
                                  ('pgf-experience-dummy', 0)])

        clan_2 = self.create_clan(self.accounts_factory.create_account(), 1)
        self.check_html_ok(self.request_html(utils_urls.url('clans:show', clan_2.id)),
                           texts=[('pgf-experience-amount', 0),
                                  ('pgf-experience-dummy', 1)])



class TestChronicleRequests(BaseTestRequests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.chronicle_url = utils_urls.url('clans:chronicle', self.clan.id)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.chronicle_url, accounts_logic.login_page_url(self.chronicle_url))

    def test_no_events(self):
        tt_services.chronicle.cmd_debug_clear_service()

        self.request_login(self.account.email)

        self.check_html_ok(self.request_html(self.chronicle_url), texts=['pgf-no-records-message'])

    def test_no_rights(self):
        self.check_no_righs__html(clan=self.clan,
                                  url=self.chronicle_url,
                                  permissions=[relations.PERMISSION.ACCESS_CHRONICLE])

    def test_has_events(self):
        self.request_login(self.account.email)

        records_on_page = conf.settings.CHRONICLE_RECORDS_ON_CLAN_PAGE

        tt_services.chronicle.cmd_debug_clear_service()

        messages = []

        for i in range(records_on_page + 1):
            message = 'clan.message.{:02d}'.format(i)
            tt_services.chronicle.cmd_add_event(self.clan,
                                                event=relations.EVENT.TECHNICAL,
                                                message=message,
                                                tags=())
            messages.append(message)

        self.check_html_ok(self.request_html(self.chronicle_url),
                           texts=[('pgf-no-records-message', 0)] +
                                 [(message, 1 if i == records_on_page else 0)
                                  for i, message in enumerate(messages)])

        self.check_html_ok(self.request_html(self.chronicle_url+'?page=2'),
                           texts=[('pgf-no-records-message', 0)] +
                                 [(message, 1 if i == records_on_page else 0)
                                  for i, message in enumerate(messages)])

        self.check_html_ok(self.request_html(self.chronicle_url+'?page=1'),
                           texts=[('pgf-no-records-message', 0)] +
                                 [(message, 0 if i == records_on_page else 1)
                                  for i, message in enumerate(messages)])


class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.edit_url = utils_urls.url('clans:edit', self.clan.id)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.edit_url, accounts_logic.login_page_url(self.edit_url))

    def test_ownership(self):
        account = self.accounts_factory.create_account()
        clan = self.create_clan(account, 1)

        self.check_html_ok(self.request_html(utils_urls.url('clans:edit', clan.id)), texts=['clans.no_rights'])

    def test_rights(self):
        account = self.accounts_factory.create_account()
        logic._add_member(clan=self.clan, account=account, role=relations.MEMBER_ROLE.RECRUIT)

        self.request_login(account.email)

        self.check_html_ok(self.request_html(utils_urls.url('clans:edit', self.clan.id)), texts=['clans.no_rights'])

    def test_no_rights(self):
        self.check_no_righs__html(clan=self.clan,
                                  url=self.edit_url,
                                  permissions=[relations.PERMISSION.EDIT])

    def test_ok(self):
        self.check_html_ok(self.request_html(self.edit_url), texts=[self.clan.abbr,
                                                                    self.clan.name,
                                                                    self.clan.motto,
                                                                    self.clan.description,
                                                                    (self.clan.description_html, 0)])

    def test_banned(self):
        self.request_login(self.account.email)
        self.account.ban_forum(1)
        self.check_html_ok(self.request_html(self.edit_url), texts=['common.ban_any'])


class TestUpdateRequests(BaseTestRequests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.update_url = utils_urls.url('clans:update', self.clan.id)
        self.request_login(self.account.email)

    def update_data(self, name=None, abbr=None):

        if name is None:
            name = 'clan-1'

        data = {'name': name,
                'abbr': 'CLN-1' if abbr is None else abbr,
                'motto': 'Clan!',
                'description': 'ARGH!'}

        data.update(linguistics_helpers.get_word_post_data(game_names.generator().get_test_name(name=name),
                                                           prefix='linguistics_name'))

        return data

    def check_clan_old_data(self):
        self.clan = logic.load_clan(clan_id=self.clan.id)

        self.assertEqual('a-0', self.clan.abbr)
        self.assertEqual('name-0', self.clan.name)
        self.assertEqual('motto-0', self.clan.motto)
        self.assertEqual('[b]description-0[/b]', self.clan.description)

    def check_clan_new_data(self):
        self.clan = logic.load_clan(clan_id=self.clan.id)

        self.assertEqual('CLN-1', self.clan.abbr)
        self.assertEqual('clan-1', self.clan.name)
        self.assertEqual('Clan!', self.clan.motto)
        self.assertEqual('ARGH!', self.clan.description)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.update_data()), 'common.login_required')
        self.check_clan_old_data()

    def test_no_rights(self):
        self.check_no_righs__ajax(self.clan,
                                  url=utils_urls.url('clans:update', self.clan.id),
                                  data=self.update_data(),
                                  permission=relations.PERMISSION.EDIT)

    def test_form_errors(self):
        self.check_ajax_error(self.post_ajax_json(self.update_url, {}), 'form_errors')
        self.check_clan_old_data()

    def test_name_exists(self):
        account = self.accounts_factory.create_account()

        clan = self.create_clan(account, 1)
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.update_data(name=clan.name)), 'clans.update.name_exists')

        self.check_clan_old_data()

    def test_abbr_exists(self):
        account = self.accounts_factory.create_account()

        clan = self.create_clan(account, 1)
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.update_data(abbr=clan.abbr)), 'clans.update.abbr_exists')

        self.check_clan_old_data()

    def test_ok(self):
        self.check_ajax_ok(self.post_ajax_json(self.update_url, self.update_data()))
        self.check_clan_new_data()

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.UPDATED.meta_object().tag,
                          self.account.meta_object().tag})

    def test_banned(self):
        self.request_login(self.account.email)
        self.account.ban_forum(1)
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.update_data()), 'common.ban_any')

    def test_name_and_abbr_not_changed(self):
        self.check_ajax_ok(self.post_ajax_json(self.update_url, self.update_data(abbr=self.clan.abbr, name=self.clan.name)))


class TestRemoveRequests(BaseTestRequests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.remove_url = utils_urls.url('clans:remove', self.clan.id)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.remove_url), 'common.login_required')
        self.assertEqual(models.Clan.objects.count(), 1)

    def test_ownership(self):
        account = self.accounts_factory.create_account()
        clan = self.create_clan(account, 1)

        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:remove', clan.id)), 'clans.no_rights')
        self.assertEqual(models.Clan.objects.count(), 2)

    def test_no_rights(self):
        self.check_no_righs__ajax(self.clan,
                                  url=utils_urls.url('clans:remove', self.clan.id),
                                  data={},
                                  permission=relations.PERMISSION.DESTROY)

    def test_not_empty(self):
        logic._add_member(clan=self.clan, account=self.accounts_factory.create_account(), role=relations.MEMBER_ROLE.RECRUIT)

        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:remove', self.clan.id)), 'clans.remove.not_empty_clan')
        self.assertEqual(models.Clan.objects.count(), 1)

        self.clan = logic.load_clan(clan_id=self.clan.id)
        self.assertEqual(self.clan.members_number, 2)

    def test_ok(self):
        self.check_ajax_ok(self.post_ajax_json(self.remove_url, ))
        self.assertEqual(models.Clan.objects.filter(state=relations.STATE.ACTIVE).count(), 0)
        self.assertEqual(models.Clan.objects.filter(state=relations.STATE.REMOVED).count(), 1)

    def test_moderator(self):
        account = self.accounts_factory.create_account()

        group = utils_permissions.sync_group('clans moderator group', ['clans.moderate_clan'])
        group.user_set.add(account._model)

        self.request_login(account.email)

        self.check_ajax_ok(self.post_ajax_json(self.remove_url))
        self.assertEqual(models.Clan.objects.filter(state=relations.STATE.ACTIVE).count(), 0)
        self.assertEqual(models.Clan.objects.filter(state=relations.STATE.REMOVED).count(), 1)


class BaseMembershipRequestsTests(BaseTestRequests):

    def setUp(self):
        super().setUp()


class MembershipForClanRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.request_login(self.account.email)

        self.for_clan_url = utils_urls.url('clans:join-requests', self.clan.id)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.for_clan_url, accounts_logic.login_page_url(self.for_clan_url))

    def test_has_invite_rights(self):
        models.Membership.objects.all().update(role=relations.MEMBER_ROLE.RECRUIT)
        self.check_html_ok(self.request_html(self.for_clan_url), texts=['clans.no_rights'])

    def test_no_rights(self):
        self.check_no_righs__html(self.clan,
                                  url=self.for_clan_url,
                                  permissions=[relations.PERMISSION.TAKE_MEMBER])

    def test_no_requests(self):
        self.check_html_ok(self.request_html(self.for_clan_url), texts=[('clans.no_rights', 0),
                                                                        ('pgf-no-requests-message', 1)])

    def test_success(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()
        account_4 = self.accounts_factory.create_account()
        account_5 = self.accounts_factory.create_account()
        account_6 = self.accounts_factory.create_account()

        clan_2 = self.create_clan(account_4, 1)

        logic.create_invite(initiator=self.account,
                            member=account_2,
                            clan=self.clan,
                            text='invite-1')

        logic.create_request(initiator=account_3,
                             clan=self.clan,
                             text='invite-2')

        logic.create_request(initiator=account_5,
                             clan=clan_2,
                             text='invite-3')

        logic.create_invite(initiator=account_4,
                            member=account_6,
                            clan=clan_2,
                            text='invite-4')

        self.check_html_ok(self.request_html(self.for_clan_url), texts=[('clans.no_rights', 0),
                                                                        ('pgf-no-requests-message', 0),
                                                                        ('invite-1', 0),
                                                                        ('invite-2', 1),
                                                                        ('invite-3', 0),
                                                                        ('invite-4', 0)])


class MembershipForAccountRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.for_account_url = utils_urls.url('clans:invites')
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.for_account_url, accounts_logic.login_page_url(self.for_account_url))

    def test_no_requests(self):
        self.check_html_ok(self.request_html(self.for_account_url), texts=[('pgf-no-requests-message', 1)])

    # change tests order to fix sqlite segmentation fault
    def test_1_success(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()
        account_4 = self.accounts_factory.create_account()
        account_5 = self.accounts_factory.create_account()
        account_6 = self.accounts_factory.create_account()

        clan_1 = self.create_clan(account_2, 0)
        clan_2 = self.create_clan(account_4, 1)
        clan_3 = self.create_clan(account_6, 2)

        logic.create_invite(initiator=account_2,
                            member=self.account,
                            clan=clan_1,
                            text='invite-1')

        logic.create_request(initiator=self.account,
                             clan=clan_3,
                             text='invite-2')

        logic.create_request(initiator=account_3,
                             clan=clan_2,
                             text='invite-3')

        logic.create_invite(initiator=account_4,
                            member=account_5,
                            clan=clan_2,
                            text='invite-4')

        self.check_html_ok(self.request_html(self.for_account_url), texts=[('pgf-no-requests-message', 0),
                                                                           ('invite-1', 1),
                                                                           ('invite-2', 0),
                                                                           ('invite-3', 0),
                                                                           ('invite-4', 0)])


class MembershipInviteDialogRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        self.invite_url = utils_urls.url('clans:invite-dialog', self.clan.id, account=self.account_2.id)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.invite_url, accounts_logic.login_page_url(self.invite_url))

    def test_no_rights(self):
        self.check_no_righs__html(self.clan,
                                  url=self.invite_url,
                                  permissions=[relations.PERMISSION.TAKE_MEMBER])

    def test_in_clan(self):
        self.create_clan(self.account_2, 1)
        self.check_html_ok(self.request_ajax_html(self.invite_url), texts=['clans.other_already_in_clan'])

    def test_wrong_account(self):
        self.check_html_ok(self.request_ajax_html(utils_urls.url('clans:invite-dialog', self.clan.id, account=666)),
                           texts=['account.wrong_value'])
        self.check_html_ok(self.request_ajax_html(utils_urls.url('clans:invite-dialog', self.clan.id, account='bla-bla')),
                           texts=['account.wrong_format'])

    def test_invite_exist__from_clan(self):
        logic.create_invite(initiator=self.account,
                            member=self.account_2,
                            clan=self.clan,
                            text='invite')
        self.check_html_ok(self.request_ajax_html(self.invite_url), texts=['clans.account_has_invite'])

    def test_invite_exist__from_account(self):
        logic.create_request(initiator=self.account_2,
                             clan=self.clan,
                             text='invite')
        self.check_html_ok(self.request_ajax_html(self.invite_url), texts=['clans.account_has_invite'])

    def test_accept_invites_from_clans(self):
        accounts_tt_services.players_properties.cmd_set_property(self.account_2.id, 'accept_invites_from_clans', False)
        self.check_html_ok(self.request_ajax_html(self.invite_url), texts=['clans.player_does_not_accept_invites_from_clans'])

    def test_success(self):
        account_3 = self.accounts_factory.create_account()
        clan_3 = self.create_clan(account_3, 1)
        account_4 = self.accounts_factory.create_account()
        clan_4 = self.create_clan(account_4, 2)

        logic.create_invite(initiator=account_3,
                            member=self.account_2,
                            clan=clan_3,
                            text='invite')

        logic.create_request(initiator=self.account_2,
                             clan=clan_4,
                             text='invite')

        self.check_html_ok(self.request_ajax_html(self.invite_url), texts=['pgf-invite-dialog'])


class MembershipRequestDialogRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        self.request_url = utils_urls.url('clans:request-dialog', self.clan.id)
        self.request_login(self.account_2.email)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.request_url, accounts_logic.login_page_url(self.request_url))

    def test_in_clan(self):
        self.create_clan(self.account_2, 1)
        self.check_html_ok(self.request_ajax_html(self.request_url), texts=['clans.already_in_clan'])

    def test_wrong_clan(self):
        self.check_html_ok(self.request_ajax_html(utils_urls.url('clans:request-dialog', 666)),
                           texts=['clan.wrong_value'])
        self.check_html_ok(self.request_ajax_html(utils_urls.url('clans:request-dialog', 'bla-bla')),
                           texts=['clan.wrong_format'])

    def test_request_exist__from_clan(self):
        logic.create_invite(initiator=self.account,
                            member=self.account_2,
                            clan=self.clan,
                            text='request')
        self.check_html_ok(self.request_ajax_html(self.request_url), texts=['clans.clan_has_request'])

    def test_request_exist__from_account(self):
        logic.create_request(initiator=self.account_2,
                             clan=self.clan,
                             text='request')
        self.check_html_ok(self.request_ajax_html(self.request_url), texts=['clans.clan_has_request'])

    def test_accept_requests_from_players(self):
        tt_services.properties.cmd_set_property(self.clan.id, 'accept_requests_from_players', False)
        self.check_html_ok(self.request_ajax_html(self.request_url), texts=['clans.clan_does_not_accept_requests_from_players'])

    def test_success(self):
        account_3 = self.accounts_factory.create_account()
        clan_3 = self.create_clan(account_3, 1)
        account_4 = self.accounts_factory.create_account()
        clan_4 = self.create_clan(account_4, 2)

        logic.create_invite(initiator=account_3,
                            member=self.account,
                            clan=clan_3,
                            text='invite')

        logic.create_request(initiator=self.account,
                             clan=clan_4,
                             text='invite')

        self.check_html_ok(self.request_ajax_html(self.request_url), texts=['pgf-request-dialog'])


class MembershipInviteRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()

        accounts_tt_services.players_properties.cmd_debug_clear_service()

        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        self.invite_url = utils_urls.url('clans:invite', self.clan.id, account=self.account_2.id)
        self.request_login(self.account.email)

    def post_data(self):
        return {'text': 'invite-text'}

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.invite_url, self.post_data()), 'common.login_required')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_clan_required(self):
        logic.remove_clan(self.clan)
        self.check_ajax_error(self.post_ajax_json(self.invite_url, self.post_data()), 'clans.no_rights')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_no_rights(self):
        self.check_no_righs__ajax(self.clan,
                                  url=self.invite_url,
                                  data=self.post_data(),
                                  permission=relations.PERMISSION.TAKE_MEMBER)

    def test_in_clan(self):
        self.create_clan(self.account_2, 1)
        self.check_ajax_error(self.post_ajax_json(self.invite_url, self.post_data()), 'clans.other_already_in_clan')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_wrong_account(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:invite', self.clan.id, account=666), self.post_data()),
                              'account.wrong_value')
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:invite', self.clan.id, account='bla-bla'), self.post_data()),
                              'account.wrong_format')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_invite_exist__from_clan(self):
        logic.create_invite(initiator=self.account,
                            member=self.account_2,
                            clan=self.clan,
                            text='invite')
        self.check_ajax_error(self.post_ajax_json(self.invite_url, self.post_data()), 'clans.account_has_invite')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)

    def test_invite_exist__from_account(self):
        logic.create_request(initiator=self.account_2,
                             clan=self.clan,
                             text='invite')
        self.check_ajax_error(self.post_ajax_json(self.invite_url, self.post_data()), 'clans.account_has_invite')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)

    def test_not_accept_invites_from_clans(self):
        accounts_tt_services.players_properties.cmd_set_property(self.account_2.id, 'accept_invites_from_clans', False)
        self.check_ajax_error(self.post_ajax_json(self.invite_url, self.post_data()), 'clans.player_does_not_accept_invites_from_clans')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_form_errors(self):
        self.check_ajax_error(self.post_ajax_json(self.invite_url, {}), 'form_errors')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_success(self):
        account_3 = self.accounts_factory.create_account()
        clan_3 = self.create_clan(account_3, 1)
        account_4 = self.accounts_factory.create_account()
        clan_4 = self.create_clan(account_4, 2)

        logic.create_invite(initiator=account_3,
                            member=self.account_2,
                            clan=clan_3,
                            text='invite')
        logic.create_request(initiator=self.account_2,
                             clan=clan_4,
                             text='invite')

        with self.check_new_message(self.account_2.id, [self.account.id]):
            self.check_ajax_ok(self.post_ajax_json(self.invite_url, self.post_data()))
            self.assertEqual(models.MembershipRequest.objects.count(), 3)

            invite = models.MembershipRequest.objects.order_by('-created_at')[0]
            self.assertEqual(invite.text, 'invite-text')
            self.assertTrue(invite.type.is_FROM_CLAN)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.NEW_MEMBERSHIP_INVITE.meta_object().tag,
                          self.account.meta_object().tag,
                          self.account_2.meta_object().tag})


class MembershipRequestRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        self.request_url = utils_urls.url('clans:request', self.clan.id)
        self.request_login(self.account_2.email)

    def post_data(self):
        return {'text': 'request-text'}

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.request_url, self.post_data()), 'common.login_required')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_in_clan(self):
        self.create_clan(self.account_2, 1)
        self.check_ajax_error(self.post_ajax_json(self.request_url, self.post_data()), 'clans.already_in_clan')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_wrong_clan(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:request', 666), self.post_data()),
                              'clan.wrong_value')
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:request', 'bla-bla'), self.post_data()),
                              'clan.wrong_format')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_request_exist__from_clan(self):
        logic.create_invite(initiator=self.account,
                            member=self.account_2,
                            clan=self.clan,
                            text='request')
        self.check_ajax_error(self.post_ajax_json(self.request_url, self.post_data()), 'clans.clan_has_request')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)

    def test_request_exist__from_account(self):
        logic.create_request(initiator=self.account_2,
                             clan=self.clan,
                             text='request')
        self.check_ajax_error(self.post_ajax_json(self.request_url, self.post_data()), 'clans.clan_has_request')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)

    def test_form_errors(self):
        self.check_ajax_error(self.post_ajax_json(self.request_url, {}), 'form_errors')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_not_accept_requests_from_players(self):
        tt_services.properties.cmd_set_property(self.clan.id, 'accept_requests_from_players', False)
        self.check_ajax_error(self.post_ajax_json(self.request_url, self.post_data()), 'clans.clan_does_not_accept_requests_from_players')
        self.assertEqual(models.MembershipRequest.objects.count(), 0)

    def test_success(self):
        account_3 = self.accounts_factory.create_account()
        clan_3 = self.create_clan(account_3, 1)
        account_4 = self.accounts_factory.create_account()
        clan_4 = self.create_clan(account_4, 2)

        logic.create_invite(initiator=account_3,
                            member=self.account,
                            clan=clan_3,
                            text='request')

        logic.create_request(initiator=self.account,
                             clan=clan_4,
                             text='request')

        with self.check_new_message(self.account.id, [self.account_2.id]):
            self.check_ajax_ok(self.post_ajax_json(self.request_url, self.post_data()))
            self.assertEqual(models.MembershipRequest.objects.count(), 3)
            request = models.MembershipRequest.objects.order_by('-created_at')[0]
            self.assertEqual(request.text, 'request-text')
            self.assertTrue(request.type.is_FROM_ACCOUNT)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.NEW_MEMBERSHIP_REQUEST.meta_object().tag,
                          self.account_2.meta_object().tag})


class MembershipAcceptRequestRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        self.request_id = logic.create_request(initiator=self.account_2,
                                               clan=self.clan,
                                               text='request')

        self.accept_url = utils_urls.url('clans:accept-request', self.clan.id, request=self.request_id)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.accept_url), 'common.login_required')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_no_rights(self):
        self.check_no_righs__ajax(self.clan,
                                  url=self.accept_url,
                                  data={},
                                  permission=relations.PERMISSION.TAKE_MEMBER)

        self.assertEqual(models.MembershipRequest.objects.count(), 1)

    def test_wrong_request_type(self):
        models.MembershipRequest.objects.all().update(type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)
        self.check_ajax_error(self.post_ajax_json(self.accept_url), 'clans.wrong_request_type')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_not_your_clan_request(self):
        account_3 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_3, 1)

        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:accept-request', clan_2.id, request=self.request_id)),
                              'clans.not_your_clan_request')

        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_wrong_request_id(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:accept-request', self.clan.id, request=666)),
                              'request.wrong_value')
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:accept-request', self.clan.id, request='bla-bla')),
                              'request.wrong_format')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_success(self):
        with self.check_new_message(self.account_2.id, [self.account.id]):
            self.check_ajax_ok(self.post_ajax_json(self.accept_url))
            self.assertEqual(models.MembershipRequest.objects.count(), 0)
            self.assertEqual(models.Membership.objects.count(), 2)
            self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account_2).is_RECRUIT)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBERSHIP_REQUEST_ACCEPTED.meta_object().tag,
                          self.account.meta_object().tag,
                          self.account_2.meta_object().tag})


class MembershipAcceptInviteRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        self.request_id = logic.create_invite(initiator=self.account,
                                              member=self.account_2,
                                              clan=self.clan,
                                              text='request')

        self.accept_url = utils_urls.url('clans:accept-invite', self.clan.id, request=self.request_id)
        self.request_login(self.account_2.email)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.accept_url), 'common.login_required')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_wrong_request_type(self):
        models.MembershipRequest.objects.all().update(type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)
        self.check_ajax_error(self.post_ajax_json(self.accept_url), 'clans.wrong_request_type')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_not_your_clan_request(self):
        account_3 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_3, 1)

        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:accept-invite', clan_2.id, request=self.request_id)),
                              'clans.not_your_clan_request')

        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_not_your_account(self):
        account_3 = self.accounts_factory.create_account()
        logic._add_member(clan=self.clan, account=account_3, role=relations.MEMBER_ROLE.COMANDOR)

        self.request_login(account_3.email)

        self.check_ajax_error(self.post_ajax_json(self.accept_url), 'clans.accept_request.not_your_account')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_wrong_request_id(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:accept-invite', self.clan.id, request=666)),
                              'request.wrong_value')
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:accept-invite', self.clan.id, request='bla-bla')),
                              'request.wrong_format')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_success(self):
        self.check_ajax_ok(self.post_ajax_json(self.accept_url))
        self.assertEqual(models.MembershipRequest.objects.count(), 0)
        self.assertEqual(models.Membership.objects.count(), 2)
        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account_2).is_RECRUIT)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBERSHIP_INVITE_ACCEPTED.meta_object().tag,
                          self.account_2.meta_object().tag})


class MembershipRejectRequestRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        self.request_id = logic.create_request(initiator=self.account_2,
                                               clan=self.clan,
                                               text='request')

        self.reject_url = utils_urls.url('clans:reject-request', self.clan.id, request=self.request_id)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.reject_url), 'common.login_required')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_no_rights(self):
        self.check_no_righs__ajax(self.clan,
                                  url=self.reject_url,
                                  data={},
                                  permission=relations.PERMISSION.TAKE_MEMBER)

        self.assertEqual(models.MembershipRequest.objects.count(), 1)

    def test_wrong_request_type(self):
        models.MembershipRequest.objects.all().update(type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN)
        self.check_ajax_error(self.post_ajax_json(self.reject_url), 'clans.wrong_request_type')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_not_your_clan_request(self):
        account_3 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_3, 1)

        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:reject-request', clan_2.id, request=self.request_id)),
                              'clans.not_your_clan_request')

        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_wrong_request_id(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:reject-request', self.clan.id, request=666)),
                              'request.wrong_value')
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:reject-request', self.clan.id, request='bla-bla')),
                              'request.wrong_format')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_success(self):
        with self.check_new_message(self.account_2.id, [self.account.id]):
            self.check_ajax_ok(self.post_ajax_json(self.reject_url))
            self.assertEqual(models.MembershipRequest.objects.count(), 0)
            self.assertEqual(models.Membership.objects.count(), 1)

        self.assertEqual(logic.get_member_role(clan=self.clan, member=self.account_2), None)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBERSHIP_REQUEST_REJECTED.meta_object().tag,
                          self.account.meta_object().tag,
                          self.account_2.meta_object().tag})


class MembershipRejectInviteRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        self.request_id = logic.create_invite(initiator=self.account,
                                              member=self.account_2,
                                              clan=self.clan,
                                              text='request')

        self.reject_url = utils_urls.url('clans:reject-invite', self.clan.id, request=self.request_id)
        self.request_login(self.account_2.email)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.reject_url), 'common.login_required')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_wrong_request_type(self):
        models.MembershipRequest.objects.all().update(type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT)
        self.check_ajax_error(self.post_ajax_json(self.reject_url), 'clans.wrong_request_type')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_not_your_clan_request(self):
        account_3 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_3, 1)

        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:reject-invite', clan_2.id, request=self.request_id)),
                              'clans.not_your_clan_request')

        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_not_your_account(self):
        account_3 = self.accounts_factory.create_account()
        logic._add_member(clan=self.clan, account=account_3, role=relations.MEMBER_ROLE.COMANDOR)

        self.request_login(account_3.email)

        self.check_ajax_error(self.post_ajax_json(self.reject_url), 'clans.accept_request.not_your_account')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_wrong_request_id(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:reject-invite', self.clan.id, request=666)),
                              'request.wrong_value')
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:reject-invite', self.clan.id, request='bla-bla')),
                              'request.wrong_format')
        self.assertEqual(models.MembershipRequest.objects.count(), 1)
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_success(self):
        self.check_ajax_ok(self.post_ajax_json(self.reject_url))
        self.assertEqual(models.MembershipRequest.objects.count(), 0)
        self.assertEqual(models.Membership.objects.count(), 1)

        self.assertEqual(logic.get_member_role(clan=self.clan, member=self.account_2), None)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBERSHIP_INVITE_REJECTED.meta_object().tag,
                          self.account_2.meta_object().tag})


class MembershipRemoveFromClanRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        logic._add_member(clan=self.clan, account=self.account_2, role=relations.MEMBER_ROLE.RECRUIT)

        self.remove_url = utils_urls.url('clans:remove-member', self.clan.id, account=self.account_2.id)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.remove_url), 'common.login_required')
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_wrong_account_id(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:remove-member', self.clan.id, account=666)),
                              'account.wrong_value')
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:remove-member', self.clan.id, account='bla-bla')),
                              'account.wrong_format')
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_no_rights(self):
        self.check_no_righs__ajax(self.clan,
                                  url=self.remove_url,
                                  data={},
                                  permission=relations.PERMISSION.REMOVE_MEMBER)

        self.assertTrue(models.Membership.objects.filter(account_id=self.account_2.id).exists())

    def test_wrong_priority(self):
        # set same role for all clan members
        models.Membership.objects.all().update(role=relations.MEMBER_ROLE.COMANDOR)

        self.check_ajax_error(self.post_ajax_json(self.remove_url), 'clans.no_rights')
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_success(self):
        with self.check_new_message(self.account_2.id, [self.account.id]):
            self.check_ajax_ok(self.post_ajax_json(self.remove_url))

        self.assertEqual(models.Membership.objects.count(), 1)

        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account).is_MASTER)
        self.assertEqual(logic.get_member_role(clan=self.clan, member=self.account_2), None)

        self.clan = logic.load_clan(clan_id=self.clan.id)
        self.assertEqual(self.clan.members_number, 1)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBER_REMOVED.meta_object().tag,
                          self.account.meta_object().tag,
                          self.account_2.meta_object().tag})


class MembershipLeaveClanRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        logic._add_member(clan=self.clan, account=self.account_2, role=relations.MEMBER_ROLE.RECRUIT)

        self.leave_url = utils_urls.url('clans:leave-clan', self.clan.id)
        self.request_login(self.account_2.email)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.leave_url), 'common.login_required')
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_not_in_clan(self):
        logic._remove_member(clan=self.clan, account=self.account_2)
        self.check_ajax_ok(self.post_ajax_json(self.leave_url))
        self.assertEqual(models.Membership.objects.count(), 1)

    def test_leader(self):
        self.request_logout()
        self.request_login(self.account.email)
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:leave-clan', self.clan.id)), 'clans.leave_clan.leader')
        self.assertEqual(models.Membership.objects.count(), 2)

    def test_success(self):
        self.check_ajax_ok(self.post_ajax_json(self.leave_url))
        self.assertEqual(models.Membership.objects.count(), 1)

        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account).is_MASTER)
        self.assertFalse(logic.get_member_role(clan=self.clan, member=self.account_2), None)

        self.clan = logic.load_clan(clan_id=self.clan.id)
        self.assertEqual(self.clan.members_number, 1)

        total_events, events = tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          relations.EVENT.MEMBER_LEFT.meta_object().tag,
                          self.account_2.meta_object().tag})


class ChangeRoleRequestsTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()

        logic._add_member(clan=self.clan, account=self.account_2, role=relations.MEMBER_ROLE.RECRUIT)

        far_updated_time = datetime.datetime.now()-datetime.timedelta(days=conf.settings.RECRUITE_FREEZE_PERIOD)

        models.Membership.objects.filter(account_id=self.account_2.id).update(updated_at=far_updated_time)

        self.change_role_url = utils_urls.url('clans:change-role', self.clan.id, account=self.account_2.id)
        self.request_login(self.account.email)

        self.data = {'role': relations.MEMBER_ROLE.FIGHTER}

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.change_role_url, self.data), 'common.login_required')
        self.assertTrue(models.Membership.objects.filter(account_id=self.account_2.id, role=relations.MEMBER_ROLE.RECRUIT).exists())

    def test_wrong_account_id(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:change-role', self.clan.id, account=666), self.data),
                              'account.wrong_value')
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:change-role', self.clan.id, account='bla-bla'), self.data),
                              'account.wrong_format')
        self.assertTrue(models.Membership.objects.filter(account_id=self.account_2.id, role=relations.MEMBER_ROLE.RECRUIT).exists())

    def test_no_rights(self):
        self.check_no_righs__ajax(self.clan,
                                  url=self.change_role_url,
                                  data=self.data,
                                  permission=relations.PERMISSION.CHANGE_ROLE)

        self.assertTrue(models.Membership.objects.filter(account_id=self.account_2.id, role=relations.MEMBER_ROLE.RECRUIT).exists())

    def test_wrong_priority(self):
        # set same role for all clan members
        models.Membership.objects.all().update(role=relations.MEMBER_ROLE.COMANDOR)

        self.check_ajax_error(self.post_ajax_json(self.change_role_url, self.data), 'clans.no_rights')

        self.assertTrue(models.Membership.objects.filter(account_id=self.account_2.id, role=relations.MEMBER_ROLE.COMANDOR).exists())

    def test_greate_role(self):
        # set same role for all clan members
        models.Membership.objects.filter(account_id=self.account.id).update(role=relations.MEMBER_ROLE.COMANDOR)

        self.check_ajax_error(self.post_ajax_json(self.change_role_url, {'role': relations.MEMBER_ROLE.COMANDOR}), 'form_errors')
        self.check_ajax_error(self.post_ajax_json(self.change_role_url, {'role': relations.MEMBER_ROLE.MASTER}), 'form_errors')

        self.assertTrue(models.Membership.objects.filter(account_id=self.account_2.id, role=relations.MEMBER_ROLE.RECRUIT).exists())

    def test_greate_role__moderator(self):
        group = utils_permissions.sync_group('clans moderator group', ['clans.moderate_clan'])
        group.user_set.add(self.account._model)

        # set same role for all clan members
        models.Membership.objects.filter(account_id=self.account.id).update(role=relations.MEMBER_ROLE.RECRUIT)

        self.check_ajax_ok(self.post_ajax_json(self.change_role_url, self.data))

        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account).is_RECRUIT)
        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account_2).is_FIGHTER)

    def test_new_recruite(self):
        logic.change_role(clan=self.clan,
                          initiator=self.account,
                          member=self.account_2,
                          new_role=relations.MEMBER_ROLE.RECRUIT)

        self.assertTrue(logic.get_membership(self.account_2.id).is_freezed())

        with self.check_not_changed(lambda: logic.get_membership(self.account_2.id).role):
            self.check_ajax_error(self.post_ajax_json(self.change_role_url, self.data), 'clans.no_rights')

    def test_not_recruite_role(self):
        logic.change_role(clan=self.clan,
                          initiator=self.account,
                          member=self.account_2,
                          new_role=relations.MEMBER_ROLE.OFFICER)

        self.assertFalse(logic.get_membership(self.account_2.id).is_freezed())

        with self.check_changed(lambda: logic.get_membership(self.account_2.id).role):
            self.check_ajax_ok(self.post_ajax_json(self.change_role_url, self.data))

    def test_fighters_limit(self):
        attributes = logic.load_attributes(self.clan.id)

        for i in range(attributes.fighters_maximum):
            account = self.accounts_factory.create_account()
            logic._add_member(clan=self.clan,
                              account=account,
                              role=relations.MEMBER_ROLE.FIGHTER)

        with self.check_not_changed(lambda: logic.get_membership(self.account_2.id).role):
            self.check_ajax_error(self.post_ajax_json(self.change_role_url, self.data), 'clans.fighters_maximum')

    def test_success(self):
        with self.check_increased(lambda: logic.get_membership(self.account_2.id).updated_at):
            self.check_ajax_ok(self.post_ajax_json(self.change_role_url, self.data))

        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account).is_MASTER)
        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account_2).is_FIGHTER)


class ChangeOwnershipTests(BaseMembershipRequestsTests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)
        self.account_2 = self.accounts_factory.create_account()
        logic._add_member(clan=self.clan, account=self.account_2, role=relations.MEMBER_ROLE.RECRUIT)

        self.change_ownership_url = utils_urls.url('clans:change-ownership', self.clan.id, account=self.account_2.id)
        self.request_login(self.account.email)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(self.change_ownership_url), 'common.login_required')
        self.assertTrue(models.Membership.objects.filter(account_id=self.account_2.id, role=relations.MEMBER_ROLE.RECRUIT).exists())

    def test_wrong_account_id(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:change-ownership', self.clan.id, account=666)),
                              'account.wrong_value')
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('clans:change-ownership', self.clan.id, account='bla-bla')),
                              'account.wrong_format')
        self.assertTrue(models.Membership.objects.filter(account_id=self.account_2.id, role=relations.MEMBER_ROLE.RECRUIT).exists())

    def test_no_rights(self):
        self.check_no_righs__ajax(self.clan,
                                  url=self.change_ownership_url,
                                  data={},
                                  permission=relations.PERMISSION.CHANGE_OWNER)

        self.assertTrue(models.Membership.objects.filter(account_id=self.account_2.id, role=relations.MEMBER_ROLE.RECRUIT).exists())

    def test_success(self):
        self.check_ajax_ok(self.post_ajax_json(self.change_ownership_url))

        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account).is_COMANDOR)
        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account_2).is_MASTER)

    def test_fighters_limit(self):
        for i in range(clans_logic.load_attributes(self.clan.id).fighters_maximum - 1):
            clans_logic._add_member(clan=self.clan,
                                    account=self.accounts_factory.create_account(),
                                    role=clans_relations.MEMBER_ROLE.COMANDOR)

        self.assertTrue(clans_logic.is_clan_in_fighters_limit(self.clan.id, delta=0))

        self.check_ajax_error(self.post_ajax_json(self.change_ownership_url), 'clans.fighters_maximum')

        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account).is_MASTER)
        self.assertTrue(logic.get_member_role(clan=self.clan, member=self.account_2).is_RECRUIT)


class TestEditMemberRequests(BaseTestRequests):

    def setUp(self):
        super().setUp()
        self.clan = self.create_clan(self.account, 0)

        self.account_2 = self.accounts_factory.create_account()
        logic._add_member(clan=self.clan, account=self.account_2, role=relations.MEMBER_ROLE.RECRUIT)

        self.edit_member_url = utils_urls.url('clans:edit-member', self.clan.id, account=self.account_2.id)

    def test_login_required(self):
        self.request_logout()
        self.check_redirect(self.edit_member_url, accounts_logic.login_page_url(self.edit_member_url))

    def test_no_rights(self):
        self.check_no_righs__html(clan=self.clan,
                                  url=self.edit_member_url,
                                  permissions=[relations.PERMISSION.CHANGE_ROLE,
                                               relations.PERMISSION.CHANGE_OWNER,
                                               relations.PERMISSION.REMOVE_MEMBER])

    def test_has_rights(self):
        self.request_login(self.account.email)

        self.check_html_ok(self.request_html(self.edit_member_url),
                           texts=[])

    def check_actions_controls(self,
                               allow_change_role=False,
                               allow_change_owner=False,
                               allow_remove_member=False):
        with mock.patch('the_tale.clans.objects.OperationsRights.can_change_role', mock.Mock(return_value=allow_change_role)), \
             mock.patch('the_tale.clans.objects.OperationsRights.can_change_owner', mock.Mock(return_value=allow_change_owner)), \
             mock.patch('the_tale.clans.objects.OperationsRights.can_remove_member', mock.Mock(return_value=allow_remove_member)):
            self.check_html_ok(self.request_html(self.edit_member_url),
                               texts=[('pgf-change-role-form', 2 if allow_change_role else 0),
                                      ('pgf-change-owner-action', 1 if allow_change_owner else 0),
                                      ('pgf-remove-member-action', 1 if allow_remove_member else 0),

                                      ('pgf-change-role-not-allower', 0 if allow_change_role else 1),
                                      ('pgf-change-owner-not-allowed', 0 if allow_change_owner else 1),
                                      ('pgf-remove-member-not-allowed', 0 if allow_remove_member else 1)])

    def test_show_controls(self):
        self.request_login(self.account.email)

        self.check_actions_controls(allow_change_role=True)
        self.check_actions_controls(allow_remove_member=True)
        self.check_actions_controls(allow_change_owner=True)
