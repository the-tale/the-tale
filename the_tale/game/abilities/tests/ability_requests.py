# coding: utf-8
from django.test import TestCase, client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from game.logic import create_test_map

from game.abilities.models import AbilityTask
from game.abilities.prototypes import AbilityTaskPrototype

class AbilityRequests(TestCase):

    def setUp(self):
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.client = client.Client()

    def test_activate_ability_unlogined(self):
        response = self.client.post(reverse('game:abilities:activate', args=[self.account.angel.abilities.keys()[0]]), {'angel_id': self.account.angel.id,
                                                                                                                        'hero_id': self.account.angel.get_hero().id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_activate_ability(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:abilities:activate', args=[self.account.angel.abilities.keys()[0]]), {'angel_id': self.account.angel.id,
                                                                                                                        'hero_id': self.account.angel.get_hero().id})
        self.assertEqual(response.status_code, 200)
        task = AbilityTaskPrototype(AbilityTask.objects.all()[0])
        self.assertEqual(s11n.from_json(response.content), {'status': 'processing',
                                                            'status_url':  reverse('game:abilities:activate_status', args=[task.type]) + '?task_id=%s' % task.id} )


    def test_activate_abiliy_status(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:abilities:activate', args=[self.account.angel.abilities.keys()[0]]), {'angel_id': self.account.angel.id,
                                                                                                                        'hero_id': self.account.angel.get_hero().id})
        status_url = s11n.from_json(response.content)['status_url']

        response = self.client.get(status_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'processing', 'status_url':  status_url})


    def test_activate_abiliy_status_unlogined(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:abilities:activate', args=[self.account.angel.abilities.keys()[0]]), {'angel_id': self.account.angel.id,
                                                                                                                        'hero_id': self.account.angel.get_hero().id})
        status_url = s11n.from_json(response.content)['status_url']

        response = self.client.post(reverse('accounts:logout'))

        response = self.client.get(status_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')
