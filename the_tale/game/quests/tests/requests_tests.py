# coding: utf-8
import mock

from django.test import client

from dext.utils.urls import url


from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import PostponedTask, PostponedTaskPrototype

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.quests.tests.helpers import QuestTestsMixin, QuestWith2ChoicePoints


class ChooseRequestsTests(testcase.TestCase, QuestTestsMixin):

    def setUp(self):
        super(ChooseRequestsTests, self).setUp()
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')

        account = AccountPrototype.get_by_email('test_user@test.com')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account.id))
        self.hero =self.storage.accounts_to_heroes[account.id]

        self.client = client.Client()

        self.choice_uid = '[ns-0]choice_1'
        self.option_uid = '#option<[ns-0]choice_1, [ns-0]choice_2>'

    @mock.patch('questgen.quests.quests_base.QuestsBase._available_quests', lambda *argv, **kwargs: [QuestWith2ChoicePoints])
    def test_choose_no_account(self):
        self.turn_to_quest(self.storage, self.hero.id)
        response = self.client.post(url('game:quests:choose', choice_uid=self.choice_uid, option_uid=self.option_uid))
        self.check_ajax_error(response, 'common.login_required')


    @mock.patch('questgen.quests.quests_base.QuestsBase._available_quests', lambda *argv, **kwargs: [QuestWith2ChoicePoints])
    def test_choose_processing(self):
        self.turn_to_quest(self.storage, self.hero.id)

        self.request_login('test_user@test.com')
        response = self.client.post(url('game:quests:choose', choice_uid=self.choice_uid, option_uid=self.option_uid))

        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)
        self.assertEqual(PostponedTask.objects.all().count(), 1)
