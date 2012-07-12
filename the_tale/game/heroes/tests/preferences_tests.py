# coding: utf-8

from dext.utils import s11n

from django.test import TestCase, client
from django.core.urlresolvers import reverse

from game.balance import calculated as calc

from accounts.logic import register_user

from game.logic import create_test_bundle, create_test_map
from game.bundles import BundlePrototype

from game.mobs.storage import MobsDatabase

from game.heroes.preferences import ChoosePreferencesTaskPrototype
from game.heroes.models import ChoosePreferencesTask, CHOOSE_PREFERENCES_STATE, PREFERENCE_TYPE


class HeroPreferencesMobTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('HeroTest')
        self.hero = self.bundle.tests_get_hero()

        self.hero.model.level = calc.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED
        self.hero.model.save()

        self.mob_id = MobsDatabase.storage().get_available_mobs_list(level=self.hero.level)[0].id
        self.mob_2_id = MobsDatabase.storage().get_available_mobs_list(level=self.hero.level)[1].id

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, 'wrong_mob_id')
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.WAITING)
        self.assertEqual(self.hero.preferences.mob_id, None)

    def test_reset_all(self):
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 1)
        ChoosePreferencesTaskPrototype.reset_all()
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).count(), 0)
        self.assertEqual(ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.RESET).count(), 1)

    def test_wrong_level(self):
        self.hero.model.level = 1
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, 'wrong_mob_id')
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_mob(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, 'wrong_mob_id')
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_preference(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, 666, self.mob_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)

    def test_wrong_mob_level(self):
        wrong_mob_id = None
        for mob_id, mob_record in MobsDatabase.storage().data.items():
            if mob_record.level > self.hero.level:
                wrong_mob_id = mob_id
                break

        self.assertTrue(wrong_mob_id)

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, wrong_mob_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.ERROR)
        self.assertEqual(self.hero.preferences.mob_id, None)


    def test_set_mob(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, self.mob_id)
        self.assertEqual(self.hero.preferences.mob_id, None)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.mob_id, self.mob_id)

    def test_change_mob(self):
        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, self.mob_id)
        task.process(self.bundle)

        task = ChoosePreferencesTaskPrototype.create(self.hero, PREFERENCE_TYPE.MOB, self.mob_2_id)
        self.assertEqual(self.hero.preferences.mob_id, self.mob_id)
        task.process(self.bundle)
        self.assertEqual(task.state, CHOOSE_PREFERENCES_STATE.PROCESSED)
        self.assertEqual(self.hero.preferences.mob_id, self.mob_2_id)

        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 2)


class HeroPreferencesRequestsTest(TestCase):

    def setUp(self):
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.bundle = BundlePrototype.get_by_id(bundle_id)
        self.hero = self.bundle.tests_get_hero()

        self.hero.model.level = calc.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED # maximum blocking level
        self.hero.model.save()

        register_user('test_user_2', 'test_user_2@test.com', '222222')

        self.client = client.Client()

        self.mob_id = MobsDatabase.storage().data.keys()[0]
        self.mob_2_id = MobsDatabase.storage().data.keys()[1]

    def tearDown(self):
        pass

    def test_preferences_dialog_mob(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.get(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % PREFERENCE_TYPE.MOB))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        for mob_id, mob_record in MobsDatabase.storage().data.items():
            if mob_record.level <= self.hero.level:
                self.assertTrue(mob_id in content)
            else:
                self.assertFalse(mob_id in content)

    def test_choose_preferences_unlogined(self):
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_preferences_success(self):
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 0)
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})
        self.assertEqual(response.status_code, 200)

        task = ChoosePreferencesTask.objects.all()[0]

        self.assertEqual(s11n.from_json(response.content), {'status': 'processing',
                                                            'status_url': reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % task.id)})
        self.assertEqual(ChoosePreferencesTask.objects.all().count(), 1)

    def test_choose_preferences_status_unlogined(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})
        response = self.client.post(reverse('accounts:logout'))

        task = ChoosePreferencesTask.objects.all()[0]
        response = self.client.post(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_preferences_status_foreign_task(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})
        response = self.client.post(reverse('accounts:logout'))

        response = self.client.post(reverse('accounts:login'), {'email': 'test_user_2@test.com', 'password': '222222'})

        task = ChoosePreferencesTask.objects.all()[0]
        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_preferences_status_error(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})

        task = ChoosePreferencesTask.objects.all()[0]
        task.state = CHOOSE_PREFERENCES_STATE.ERROR
        task.save()

        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_preferences_status_success(self):
        response = self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})
        response = self.client.post(reverse('game:heroes:choose-preferences', args=[self.hero.id]), {'preference_type': PREFERENCE_TYPE.MOB, 'preference_id': self.mob_id})

        task = ChoosePreferencesTask.objects.all()[0]
        task.state = CHOOSE_PREFERENCES_STATE.PROCESSED
        task.save()

        response = self.client.get(reverse('game:heroes:choose-preferences-status', args=[self.hero.id]) + ('?task_id=%d' % (task.id,)) )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content), {'status': 'ok'})
