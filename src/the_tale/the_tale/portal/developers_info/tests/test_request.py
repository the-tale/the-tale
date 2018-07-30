
import smart_imports

smart_imports.all()


class TestRequestsBase(utils_testcase.TestCase):

    def setUp(self):
        super(TestRequestsBase, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        staff_account = django_auth.authenticate(nick=self.account_2.nick, password='111111')
        staff_account.is_staff = True
        staff_account.save()


class TestIndexRequests(TestRequestsBase):

    def test_login_required(self):
        request_url = django_reverse('portal:developers-info:')
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_staff_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(django_reverse('portal:developers-info:')), texts=['common.staff_required'])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('portal:developers-info:')))


class TestMobsAndArtifactsRequests(TestRequestsBase):

    def test_login_required(self):
        request_url = django_reverse('portal:developers-info:mobs-and-artifacts')
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_staff_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(django_reverse('portal:developers-info:mobs-and-artifacts')), texts=['common.staff_required'])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('portal:developers-info:mobs-and-artifacts')))

    def test_mobs_without_artifacts(self):
        self.request_login(self.account_2.email)

        mob_without_loot = mobs_logic.create_random_mob_record('no_loot')
        mob_without_artifact = mobs_logic.create_random_mob_record('no_artifact')
        mob_without_loot_on_first_level = mobs_logic.create_random_mob_record('no_loot_on_1_level')
        mob_without_artifact_on_firs_level = mobs_logic.create_random_mob_record('no_artifact_on_1_level')

        artifacts_logic.create_random_artifact_record('not_first_loot', mob=mob_without_loot_on_first_level, level=mob_without_loot_on_first_level.level + 1)
        artifacts_logic.create_random_artifact_record('not_first_artifact', mob=mob_without_artifact_on_firs_level, level=mob_without_artifact_on_firs_level.level + 1)

        self.check_html_ok(self.request_html(django_reverse('portal:developers-info:mobs-and-artifacts')), texts=[mob_without_loot.name,
                                                                                                                  mob_without_artifact.name,
                                                                                                                  mob_without_loot_on_first_level.name,
                                                                                                                  mob_without_artifact_on_firs_level.name])

    def test_artifacts_without_mobs(self):
        self.request_login(self.account_2.email)

        no_mob_loot = artifacts_logic.create_random_artifact_record('no_mob_loot', level=1)
        no_mob_artifact = artifacts_logic.create_random_artifact_record('no_mob_artifact', level=1)

        self.check_html_ok(self.request_html(django_reverse('portal:developers-info:mobs-and-artifacts')), texts=[no_mob_loot.name, no_mob_artifact.name])
