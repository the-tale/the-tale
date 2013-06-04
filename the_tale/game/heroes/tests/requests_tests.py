# coding: utf-8

import jinja2

from django.test import client
from django.core.urlresolvers import reverse

from textgen.words import Noun

from common.utils.testcase import TestCase
from common.postponed_tasks import PostponedTask, PostponedTaskPrototype
from common.utils.permissions import sync_group

from accounts.logic import register_user, login_url
from accounts.prototypes import AccountPrototype

from game.balance import constants as c
from game.game_info import GENDER, GENDER_ID_2_STR
from game.balance.enums import RACE
from game.logic_storage import LogicStorage
from game.logic import create_test_map
from game.heroes.prototypes import HeroPrototype

class HeroRequestsTestBase(TestCase):

    def setUp(self):
        super(HeroRequestsTestBase, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

        self.client = client.Client()
        self.request_login('test_user@test.com')


class HeroIndexRequestsTests(HeroRequestsTestBase):

    def test_index(self):
        response = self.request_html(reverse('game:heroes:'))
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)


class MyHeroRequestsTests(HeroRequestsTestBase):

    def test_unloginned(self):
        self.request_logout()
        url = reverse('game:heroes:my-hero')
        self.check_redirect(url, login_url(url))

    def test_redirect(self):
        self.check_redirect(reverse('game:heroes:my-hero'), reverse('game:heroes:show', args=[self.hero.id]))


class HeroPageRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(HeroPageRequestsTests, self).setUp()

    def test_wrong_hero_id(self):
        self.check_html_ok(self.request_html(reverse('game:heroes:show', args=['dsdsd'])), texts=[('heroes.hero.wrong_format', 1)])

    def test_own_hero_page(self):
        self.check_html_ok(self.request_html(reverse('game:heroes:show', args=[self.hero.id])),
                           texts=(('pgf-health-percents', 1),
                                  ('pgf-experience-percents', 1),
                                  ('pgf-energy-percents', 1),
                                  ('pgf-power value', 1),
                                  ('pgf-money', 1),
                                  ('"pgf-health"', 1),
                                  ('pgf-max-health', 1),
                                  ('pgf-choose-ability-button', 1),
                                  ('pgf-choose-preference-button', 2),
                                  ('pgf-free-destiny-points', 1),
                                  ('pgf-settings-container',2),
                                  ('pgf-settings-tab-button', 2),
                                  ('pgf-moderation-container', 0)))

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
                 ('pgf-free-destiny-points', 0),
                 ('pgf-settings-container',0),
                 ('pgf-settings-tab-button', 1),
                 ('pgf-moderation-container', 0))

        self.request_logout()
        self.check_html_ok(self.request_html(reverse('game:heroes:show', args=[self.hero.id])), texts=texts)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('game:heroes:show', args=[self.hero.id])), texts=texts)

    def test_moderation_tab(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)
        self.request_login('test_user_2@test.com')

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.account_set.add(account_2._model)

        self.check_html_ok(self.request_html(reverse('game:heroes:show', args=[self.hero.id])), texts=['pgf-moderation-container'])




class ChangePreferencesRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(ChangePreferencesRequestsTests, self).setUp()

    def test_chooce_preferences_dialog(self):
        from game.heroes.models import PREFERENCE_TYPE

        self.hero._model.level = c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED
        self.hero.save()

        for preference_type in PREFERENCE_TYPE._ALL:
            texts = []
            self.check_html_ok(self.request_html(reverse('game:heroes:choose-preferences-dialog', args=[self.hero.id]) + ('?type=%d' % preference_type)), texts=texts)


class ChangeHeroRequestsTests(HeroRequestsTestBase):

    def test_hero_page(self):
        self.check_html_ok(self.request_html(reverse('game:heroes:show', args=[self.hero.id])), texts=[(jinja2.escape(self.hero.name), 7),
                                                                                                     ('pgf-change-name-warning', 1)])

    def test_hero_page_change_name_warning_hidden(self):
        self.hero.normalized_name = Noun(u'слово', forms=[u'слово']*12)
        self.hero.save()
        self.check_html_ok(self.request_html(reverse('game:heroes:show', args=[self.hero.id])), texts=[('pgf-change-name-warning', 0)])

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
        self.assertEqual(PostponedTask.objects.all().count(), 0)
        response = self.client.post(reverse('game:heroes:change-hero', args=[self.hero.id]), self.get_post_data())
        self.assertEqual(PostponedTask.objects.all().count(), 1)

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertEqual(task.internal_logic.name, self.get_name())
        self.assertEqual(task.internal_logic.gender, GENDER.MASCULINE)
        self.assertEqual(task.internal_logic.race, RACE.DWARF)


class ResetNameRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(ResetNameRequestsTests, self).setUp()

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.account_set.add(self.account_2._model)

        self.request_login('test_user_2@test.com')

    def test_chane_hero_moderation(self):
        self.request_logout()
        self.request_login('test_user@test.com')

        self.check_ajax_error(self.client.post(reverse('game:heroes:reset-name', args=[self.hero.id])), 'heroes.moderator_rights_required')

    def test_change_hero(self):
        self.hero._model.name = '111'
        self.hero.save()

        self.assertEqual(PostponedTask.objects.all().count(), 0)
        response = self.client.post(reverse('game:heroes:reset-name', args=[self.hero.id]))
        self.assertEqual(PostponedTask.objects.all().count(), 1)

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertNotEqual(task.internal_logic.name, self.hero.name)
        self.assertEqual(task.internal_logic.gender, self.hero.gender)
        self.assertEqual(task.internal_logic.race, self.hero.race)
