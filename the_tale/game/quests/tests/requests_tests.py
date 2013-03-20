# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils import testcase
from common.postponed_tasks import PostponedTask, PostponedTaskPrototype

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from game.logic_storage import LogicStorage

from game.logic import create_test_map
from game.quests.quests_generator.tests.helpers import QuestWith2ChoicePoints, patch_quests_list

from game.quests.tests.helpers import QuestTestsMixin


class RequestsTests(testcase.TestCase, QuestTestsMixin):

    def setUp(self):
        super(RequestsTests, self).setUp()
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        register_user('test_user_2', 'test_user_2@test.com', '111111')

        account = AccountPrototype.get_by_email('test_user@test.com')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account.id))
        self.hero =self.storage.accounts_to_heroes[account.id]

        self.client = client.Client()

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_no_account(self):
        quest_id = self.turn_to_quest(self.storage, self.hero.id).id
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=some_point&choice=some_choice')
        self.check_ajax_error(response, 'common.login_required')


    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_processing(self):
        quest_id = self.turn_to_quest(self.storage, self.hero.id).id

        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_1&choice=choice_1_1')

        task = PostponedTaskPrototype(PostponedTask.objects.all()[0])
        self.check_ajax_processing(response, task.status_url)
        self.assertEqual(PostponedTask.objects.all().count(), 1)
