# coding: utf-8
from django.test import client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from common.utils.testcase import TestCase
from common.postponed_tasks.models import PostponedTask
from common.postponed_tasks.prototypes import PostponedTaskPrototype

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from game.logic import create_test_map

from game.heroes.prototypes import HeroPrototype

from game.abilities.deck.help import Help

class AbilityRequests(TestCase):

    def setUp(self):
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
        response = self.client.post(reverse('game:abilities:activate', args=[Help.get_type()]), {'hero_id': HeroPrototype.get_by_account_id(self.account.id).id})
        task = PostponedTaskPrototype(PostponedTask.objects.all()[0])
        self.check_ajax_processing(response, task.status_url)


    def test_activate_abiliy_status(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:abilities:activate', args=[Help.get_type()]), {'hero_id': HeroPrototype.get_by_account_id(self.account.id).id})
        status_url = s11n.from_json(response.content)['status_url']

        response = self.client.get(status_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'processing', 'status_url':  status_url})
