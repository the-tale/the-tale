# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate as django_authenticate

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.logic import login_page_url

from the_tale.game.logic import create_test_map

class TestRequestsBase(TestCase):

    def setUp(self):
        super(TestRequestsBase, self).setUp()
        create_test_map()
        self.client = client.Client()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        staff_account = django_authenticate(nick=self.account_2.nick, password='111111')
        staff_account.is_staff = True
        staff_account.save()


class TestIndexRequests(TestRequestsBase):

    def test_login_required(self):
        request_url = reverse('portal:developers-info:')
        self.check_redirect(request_url, login_page_url(request_url))

    def test_staff_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(reverse('portal:developers-info:')), texts=['common.staff_required'])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(reverse('portal:developers-info:')))

class TestMobsAndArtifactsRequests(TestRequestsBase):

    def test_login_required(self):
        request_url = reverse('portal:developers-info:mobs-and-artifacts')
        self.check_redirect(request_url, login_page_url(request_url))

    def test_staff_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(reverse('portal:developers-info:mobs-and-artifacts')), texts=['common.staff_required'])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(reverse('portal:developers-info:mobs-and-artifacts')))

    def test_mobs_without_artifacts(self):
        self.request_login(self.account_2.email)

        from the_tale.game.mobs.prototypes import MobRecordPrototype
        from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype

        mob_without_loot = MobRecordPrototype.create_random('mob_without_loot')
        mob_without_artifact = MobRecordPrototype.create_random('mob_without_artifact')
        mob_without_loot_on_first_level = MobRecordPrototype.create_random('mob_without_loot_on_first_level')
        mob_without_artifact_on_firs_level = MobRecordPrototype.create_random('mob_without_artifact_on_firs_level')

        ArtifactRecordPrototype.create_random('not_first_loot', mob=mob_without_loot_on_first_level, level=mob_without_loot_on_first_level.level+1)
        ArtifactRecordPrototype.create_random('not_first_artifact', mob=mob_without_artifact_on_firs_level, level=mob_without_artifact_on_firs_level.level+1)

        self.check_html_ok(self.request_html(reverse('portal:developers-info:mobs-and-artifacts')), texts=[mob_without_loot.name,
                                                                                                         mob_without_artifact.name,
                                                                                                         mob_without_loot_on_first_level.name,
                                                                                                         mob_without_artifact_on_firs_level.name])


    def test_artifacts_without_mobs(self):
        self.request_login(self.account_2.email)

        from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype

        no_mob_loot = ArtifactRecordPrototype.create_random('no_mob_loot', level=1)
        no_mob_artifact = ArtifactRecordPrototype.create_random('no_mob_artifact', level=1)

        self.check_html_ok(self.request_html(reverse('portal:developers-info:mobs-and-artifacts')), texts=[no_mob_loot.name, no_mob_artifact.name])
