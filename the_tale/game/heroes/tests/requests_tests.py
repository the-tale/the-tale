# coding: utf-8
import mock

from django.test import client
from django.core.urlresolvers import reverse

from textgen.words import Noun

from common.utils.testcase import TestCase

from accounts.logic import register_user

from game.game_info import RACE, GENDER, GENDER_ID_2_STR
from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.heroes.prototypes import HeroPrototype, ChangeHeroTaskPrototype
from game.heroes.models import ChangeHeroTask, CHANGE_HERO_STATE

class HeroRequestsTestBase(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.client = client.Client()
        self.request_login('test_user@test.com')


class HeroIndexRequestsTests(HeroRequestsTestBase):

    def test_index(self):
        response = self.client.get(reverse('game:heroes:'))
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)


class HeroPageRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(HeroPageRequestsTests, self).setUp()

    def test_wrong_hero_id(self):
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=['dsdsd'])), texts=[('heroes.wrong_hero_id', 1)], status_code=404)

    def test_own_hero_page(self):
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=[self.hero.id])),
                           texts=(('pgf-health-percents', 1),
                                  ('pgf-experience-percents', 1),
                                  ('pgf-energy-percents', 1),
                                  ('pgf-power value', 1),
                                  ('pgf-money', 1),
                                  ('"pgf-health"', 1),
                                  ('pgf-max-health', 1),
                                  ('pgf-choose-ability-button', 1),
                                  ('pgf-choose-preference-button', 2),
                                  ('pgf-free-destiny-points', 1))) # in script and in 1 lvl preference


    def test_other_hero_page(self):
        texts = (('pgf-health-percents', 0),
                                  ('pgf-experience-percents', 0),
                                  ('pgf-energy-percents', 0),
                                  ('pgf-power value', 1),
                                  ('pgf-money', 0),
                                  ('"pgf-health"', 0),
                                  ('pgf-max-health', 1),
                                  ('pgf-choose-ability-button', 0),
                                  ('pgf-choose-preference-button', 0),
                                  ('pgf-free-destiny-points', 0))

        self.request_logout()
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=[self.hero.id])), texts=texts)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=[self.hero.id])), texts=texts)


class ChangeHeroRequestsTests(HeroRequestsTestBase):

    def test_hero_page(self):
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=[self.hero.id])), texts=[(self.hero.name, 7),
                                                                                                     ('pgf-change-name-warning', 1)])

    def test_hero_page_change_name_warning_hidden(self):
        self.hero.normalized_name = Noun(u'слово', forms=[u'слово']*12)
        self.hero.save()
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=[self.hero.id])), texts=[('pgf-change-name-warning', 0)])

    def get_post_data(self, name='new_name', gender=GENDER.MASCULINE, race=RACE.DWARF):
        return {'name_forms_0': u'%s_0' % name,
                'name_forms_1': u'%s_1' % name,
                'name_forms_2': u'%s_2' % name,
                'name_forms_3': u'%s_3' % name,
                'name_forms_4': u'%s_4' % name,
                'name_forms_5': u'%s_5' % name,
                'gender': gender,
                'race': race}

    def get_name(self, name='new_name', gender=GENDER.MASCULINE):
        return Noun(normalized='%s_0' % name,
                    forms=[u'%s_0' % name,
                           u'%s_1' % name,
                           u'%s_2' % name,
                           u'%s_3' % name,
                           u'%s_4' % name,
                           u'%s_5' % name] * 2,
                    properties=(GENDER_ID_2_STR[gender], ))

    def test_chane_hero_ownership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error(self.client.post(reverse('game:heroes:change-hero', args=[self.hero.id]), self.get_post_data()),
                              'heroes.not_owner')

    def test_change_hero_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:heroes:change-hero', args=[self.hero.id]), {}),
                              'heroes.change_name.form_errors')


    def test_change_hero(self):
        self.assertEqual(ChangeHeroTask.objects.all().count(), 0)
        response = self.client.post(reverse('game:heroes:change-hero', args=[self.hero.id]), self.get_post_data())
        self.assertEqual(ChangeHeroTask.objects.all().count(), 1)

        task = ChangeHeroTaskPrototype(ChangeHeroTask.objects.all()[0])
        self.check_ajax_processing(response, status_url=reverse('game:heroes:change-hero-status', args=[self.hero.id]) + ('?task_id=%d' % task.id))

        self.assertEqual(task.name, self.get_name())
        self.assertEqual(task.gender, GENDER.MASCULINE)
        self.assertEqual(task.race, RACE.DWARF)

    def test_change_hero_status_no_task(self):
        self.client.post(reverse('game:heroes:change-hero', args=[self.hero.id]), self.get_post_data())
        self.check_ajax_error(self.client.get(reverse('game:heroes:change-hero-status', args=[self.hero.id]) + '?task_id=666'),
                              'heroes.change_hero_status.no_task')


    def test_change_hero_status_waiting(self):
        self.client.post(reverse('game:heroes:change-hero', args=[self.hero.id]), self.get_post_data())
        task = ChangeHeroTaskPrototype(ChangeHeroTask.objects.all()[0])
        self.check_ajax_processing(self.client.get(reverse('game:heroes:change-hero-status', args=[self.hero.id]) + ('?task_id=%d' % task.id)),
                                   reverse('game:heroes:change-hero-status', args=[self.hero.id]) + ('?task_id=%d' % task.id))

    def test_change_hero_status_processed(self):
        self.client.post(reverse('game:heroes:change-hero', args=[self.hero.id]), self.get_post_data())
        task = ChangeHeroTaskPrototype(ChangeHeroTask.objects.all()[0])
        task.model.state = CHANGE_HERO_STATE.PROCESSED
        task.save()
        self.check_ajax_ok(self.client.get(reverse('game:heroes:change-hero-status', args=[self.hero.id]) + ('?task_id=%d' % task.id)))

    def test_change_hero_status_unknown_error(self):
        self.client.post(reverse('game:heroes:change-hero', args=[self.hero.id]), self.get_post_data())
        task = ChangeHeroTaskPrototype(ChangeHeroTask.objects.all()[0])
        task.model.state = 666
        task.save()
        self.check_ajax_error(self.client.get(reverse('game:heroes:change-hero-status', args=[self.hero.id]) + ('?task_id=%d' % task.id)),
                              'heroes.change_hero_status.error')
