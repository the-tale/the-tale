# coding: utf-8
import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from common.utils.testcase import TestCase

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from game.actions.prototypes import ActionQuestPrototype, ActionIdlenessPrototype

from game.logic import create_test_map
from game.bundles import BundlePrototype
from game.prototypes import TimePrototype
from game.quests.quests_generator.tests.helpers import QuestWith2ChoicePoints, patch_quests_list

class RequestsTests(TestCase):

    def setUp(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        register_user('test_user_2', 'test_user_2@test.com', '111111')

        account = AccountPrototype.get_by_email('test_user@test.com')
        angel = account.angel
        self.bundle_1 = BundlePrototype.get_by_angel(angel)

        self.client = client.Client()

    def login(self, email):
        response = self.client.post(reverse('accounts:login'), {'email': email, 'password': '111111'})
        self.assertEqual(response.status_code, 200)

    def create_quest_for_user(self, bundle):

        current_time = TimePrototype.get_current_time()

        while bundle.tests_get_last_action().TYPE != ActionQuestPrototype.TYPE:
            bundle.process_turn()
            bundle.save_data()
            current_time.increment_turn()

        return bundle.tests_get_last_action().quest.id


    def test_choose_no_quest(self):
        self.login('test_user@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[666]) + '?choice_point=some_point&choice=some_choice')
        self.check_ajax_error(response, 'quests.no_quest')

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_no_account(self):
        quest_id = self.create_quest_for_user(self.bundle_1)
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=some_point&choice=some_choice')
        self.check_ajax_error(response, 'common.login_required')

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_wrong_account(self):
        quest_id = self.create_quest_for_user(self.bundle_1)
        self.login('test_user_2@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=some_point&choice=some_choice')
        self.check_ajax_error(response, 'quests.wrong_account')

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_wrong_choice(self):
        quest_id = self.create_quest_for_user(self.bundle_1)
        self.login('test_user@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=some_point&choice=some_choice')
        self.check_ajax_error(response, 'quests.choose.unknown_choice')

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_not_first_choice_point(self):
        quest_id = self.create_quest_for_user(self.bundle_1)
        self.login('test_user@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_2&choice=choice_1_1')
        self.check_ajax_error(response, 'quests.choose.wrong_point')

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_success(self):
        quest_id = self.create_quest_for_user(self.bundle_1)
        self.login('test_user@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_1&choice=choice_1_1')
        self.check_ajax_ok(response)

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_already_choosen(self):
        quest_id = self.create_quest_for_user(self.bundle_1)
        self.login('test_user@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_1&choice=choice_1_1')
        self.check_ajax_ok(response)
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_1&choice=choice_1_1')
        self.check_ajax_error(response, 'quests.choose.already_choosed')

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    # TODO: patch not QuestPrototype, but Line
    @mock.patch('game.quests.prototypes.QuestPrototype.is_choice_available', lambda self, choice: False)
    def test_choose_not_allowed(self):
        quest_id = self.create_quest_for_user(self.bundle_1)
        self.login('test_user@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_1&choice=choice_1_1')
        self.check_ajax_error(response, 'quests.choose.line_not_availbale')

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_second_choice_before_first_completed(self):
        quest_id = self.create_quest_for_user(self.bundle_1)
        self.login('test_user@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_1&choice=choice_1_2')
        self.check_ajax_ok(response)
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_2&choice=choice_2_1')
        self.check_ajax_error(response, 'quests.choose.unknown_choice')

    @patch_quests_list('game.quests.logic.QuestsSource', [QuestWith2ChoicePoints])
    def test_choose_second_choice_after_first_completed(self):
        quest_id = self.create_quest_for_user(self.bundle_1)
        self.login('test_user@test.com')
        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_1&choice=choice_1_2')
        self.check_ajax_ok(response)

        response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_2&choice=choice_2_1')

        current_time = TimePrototype.get_current_time()

        while s11n.from_json(response.content)['status'] == 'error':
            self.assertNotEqual(self.bundle_1.tests_get_last_action().TYPE, ActionIdlenessPrototype.TYPE)
            self.bundle_1.process_turn()
            self.bundle_1.save_data()
            current_time.increment_turn()
            response = self.client.post(reverse('game:quests:choose', args=[quest_id]) + '?choice_point=choose_2&choice=choice_2_1')

        self.check_ajax_ok(response)
