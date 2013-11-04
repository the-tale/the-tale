# coding: utf-8
from django.test import client

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map

from the_tale.game.abilities.logic import use_ability_url
from the_tale.game.abilities.relations import ABILITY_TYPE


class AbilityRequests(TestCase):

    def setUp(self):
        super(AbilityRequests, self).setUp()
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.client = client.Client()

    def test_activate_ability_unlogined(self):
        self.check_ajax_error(self.client.post(use_ability_url(ABILITY_TYPE.HELP)), 'common.login_required')

    def test_activate_ability(self):
        self.request_login('test_user@test.com')
        response = self.client.post(use_ability_url(ABILITY_TYPE.HELP))
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)
