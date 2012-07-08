# coding: utf-8

from dext.utils import s11n

from django.test import TestCase, client
from django.core.urlresolvers import reverse

from accounts.logic import register_user

from game.actions.fake import FakeActor

from game.heroes.fake import FakeMessanger
from game.heroes.models import Hero, ChooseAbilityTask, CHOOSE_ABILITY_STATE
from game.bundles import BundlePrototype
from game.heroes.prototypes import HeroPrototype, ChooseAbilityTaskPrototype
from game.heroes.habilities import prototypes as common_abilities
from game.heroes.habilities import ABILITIES
from game.heroes.habilities.prototypes import ABILITIES_LOGIC_TYPE
from game.prototypes import TimePrototype

from game.logic import create_test_map


class HabilitiesTest(TestCase):

    def setUp(self):
        self.messanger = FakeMessanger()
        self.attacker = FakeActor(name='attacker')
        self.defender = FakeActor(name='defender')

    def tearDown(self):
        pass

    def test_on_miss_method_exists(self):
        for ability_class in ABILITIES.values():
            if ability_class.LOGIC_TYPE == ABILITIES_LOGIC_TYPE.WITH_CONTACT:
                self.assertTrue('on_miss' in ability_class.__dict__)

    def test_hit(self):
        common_abilities.HIT.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messanger.messages, ['hero_ability_hit'])

    def test_magic_mushroom(self):
        common_abilities.MAGIC_MUSHROOM.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertTrue(self.attacker.context.ability_magic_mushroom)
        self.assertFalse(self.defender.context.ability_magic_mushroom)
        self.assertEqual(self.messanger.messages, ['hero_ability_magicmushroom'])

    def test_sidestep(self):
        common_abilities.SIDESTEP.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertFalse(self.attacker.context.ability_sidestep)
        self.assertTrue(self.defender.context.ability_sidestep)
        self.assertEqual(self.messanger.messages, ['hero_ability_sidestep'])

    def test_run_up_push(self):
        common_abilities.RUN_UP_PUSH.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertFalse(self.attacker.context.stun_length)
        self.assertTrue(self.defender.context.stun_length)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messanger.messages, ['hero_ability_runuppush'])

    def test_regeneration(self):
        self.attacker.health = 1
        common_abilities.REGENERATION.use(self.messanger, TimePrototype.get_current_time(), self.attacker, self.defender)
        self.assertTrue(self.attacker.health > 1)
        self.assertEqual(self.messanger.messages, ['hero_ability_regeneration'])

    def test_critical_chance(self):
        pass


class HabilitiesViewsTest(TestCase):

    def setUp(self):
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.bundle = BundlePrototype.get_by_id(bundle_id)
        self.hero = self.bundle.tests_get_hero()

        self.client = client.Client()

    def get_new_ability_id(self, hero=None):
        if hero is None:
            hero = self.hero
        return hero.get_abilities_for_choose()[0].get_id()

    @property
    def task(self):
        if not hasattr(self, '_task'):
            self._task = ChooseAbilityTaskPrototype(ChooseAbilityTask.objects.all()[0])
        return self._task

    def tearDown(self):
        pass

    def test_choose_ability_dialog(self):
        response = self.client.get(reverse('game:heroes:choose-ability-dialog', args=[self.hero.id]))
        self.assertEqual(response.status_code, 200) #here is error page

        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:heroes:choose-ability-dialog', args=[self.hero.id]))
        self.assertEqual(response.status_code, 200) #here is real page

    def test_choose_ability_request_anonimouse(self):
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')


    def test_choose_ability_request_wrong_hero(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})

        # hero not exist
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id+1]) + '?ability_id=' + self.get_new_ability_id())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

        # wrong hero
        register_user('test_user2', 'test_user2@test.com', '111111')
        wrong_hero = HeroPrototype(Hero.objects.all()[1])
        response = self.client.post(reverse('game:heroes:choose-ability', args=[wrong_hero.id]) + '?ability_id=' + self.get_new_ability_id(wrong_hero))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_ability_request_wrong_ability(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id+1]) + '?ability_id=xxxyyy')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_ability_request_ok(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'processing',
                                                            'status_url': '/game/heroes/1/choose-ability-status?task_id=1'})
        self.assertEqual(ChooseAbilityTask.objects.all().count(), 1)

    def test_choose_ability_status_anonimouse(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        response = self.client.get(reverse('accounts:logout'))
        response = self.client.get(reverse('game:heroes:choose-ability-status', args=[self.hero.id]) + '?task_id=%s' % self.task.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_ability_status_from_other_account(self):
        register_user('test_user2', 'test_user2@test.com', '111111')

        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        response = self.client.get(reverse('accounts:logout'))

        response = self.client.post(reverse('accounts:login'), {'email': 'test_user2@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:heroes:choose-ability-status', args=[self.hero.id]) + '?task_id=%s' % self.task.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')


    def test_choose_ability_status_processing(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        response = self.client.get(reverse('game:heroes:choose-ability-status', args=[self.hero.id]) + '?task_id=%s' % self.task.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'processing',
                                                            'status_url': '/game/heroes/1/choose-ability-status?task_id=1'})


    def test_choose_ability_status_processed(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())

        self.task.process(self.bundle)
        self.task.save()

        response = self.client.get(reverse('game:heroes:choose-ability-status', args=[self.hero.id]) + '?task_id=%s' % self.task.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'ok'})


    def test_choose_ability_status_error(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())

        self.task.state = CHOOSE_ABILITY_STATE.ERROR
        self.task.save()

        response = self.client.get(reverse('game:heroes:choose-ability-status', args=[self.hero.id]) + '?task_id=%s' % self.task.id, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')
