# coding: utf-8
from django.test import client
from django.core.urlresolvers import reverse

from dext.utils import s11n
from dext.utils.urls import url

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.abilities.deck.help import Help

class AbilityRequests(TestCase):

    def setUp(self):
        super(AbilityRequests, self).setUp()
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.client = client.Client()

    def test_activate_ability_unlogined(self):
        response = self.client.post(reverse('game:abilities:activate', args=[Help.get_type()]), {'hero_id': HeroPrototype.get_by_account_id(self.account.id).id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_activate_ability(self):
        self.request_login('test_user@test.com')
        response = self.client.post(url('game:abilities:activate', Help.get_type(), hero=HeroPrototype.get_by_account_id(self.account.id).id))
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)
