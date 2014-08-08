# coding: utf-8
import datetime

import jinja2
import mock

from django.test import client

from dext.common.utils.urls import url

from textgen.words import Noun

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import PostponedTask, PostponedTaskPrototype
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.logic import register_user, login_page_url
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.relations import GENDER, RACE
from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.cards.relations import CARD_TYPE

from the_tale.game.heroes import relations


class HeroRequestsTestBase(TestCase):

    def setUp(self):
        super(HeroRequestsTestBase, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        self.client = client.Client()
        self.request_login('test_user@test.com')


class HeroIndexRequestsTests(HeroRequestsTestBase):

    def test_index(self):
        response = self.request_html(url('game:heroes:'))
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)


class MyHeroRequestsTests(HeroRequestsTestBase):

    def test_unloginned(self):
        self.request_logout()
        request_url = url('game:heroes:my-hero')
        self.check_redirect(request_url, login_page_url(request_url))

    def test_redirect(self):
        self.check_redirect(url('game:heroes:my-hero'), url('game:heroes:show', self.hero.id))


class HeroPageRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(HeroPageRequestsTests, self).setUp()

    def test_wrong_hero_id(self):
        self.check_html_ok(self.request_html(url('game:heroes:show', 'dsdsd')), texts=[('heroes.hero.wrong_format', 1)])

    def test_own_hero_page(self):
        self.check_html_ok(self.request_html(url('game:heroes:show', self.hero.id)),
                           texts=(('pgf-health-percents', 1),
                                  ('pgf-reset-abilities-timeout-button', 1),
                                  ('pgf-reset-abilities-button', 0),
                                  ('pgf-experience-percents', 1),
                                  ('pgf-energy-percents', 1),
                                  ('pgf-physic-power value', 1),
                                  ('pgf-magic-power value', 1),
                                  ('pgf-money', 1),
                                  ('"pgf-health"', 1),
                                  ('pgf-max-health', 1),
                                  ('pgf-choose-ability-button', 2),
                                  ('pgf-choose-preference-button', 2),
                                  ('pgf-free-destiny-points', 3),
                                  ('pgf-no-destiny-points', 2),
                                  ('pgf-settings-container',2),
                                  ('pgf-settings-tab-button', 2),
                                  ('pgf-moderation-container', 0)))

    def test_can_reset_abilities(self):
        self.hero.abilities.set_reseted_at(datetime.datetime.fromtimestamp(0))
        self.hero.abilities.updated = True
        self.hero.save()
        self.check_html_ok(self.request_html(url('game:heroes:show', self.hero.id)),
                           texts=(('pgf-reset-abilities-timeout-button', 0),
                                  ('pgf-reset-abilities-button', 1)))

    def test_other_hero_page(self):
        texts = (('pgf-health-percents', 1),
                 ('pgf-reset-abilities-timeout-button', 0),
                 ('pgf-reset-abilities-button', 0),
                 ('pgf-experience-percents', 0),
                 ('pgf-energy-percents', 0),
                 ('pgf-physic-power value', 1),
                 ('pgf-magic-power value', 1),
                 ('pgf-money', 1),
                 ('"pgf-health"', 1),
                 ('pgf-max-health', 1),
                 ('pgf-choose-ability-button', 0),
                 ('pgf-choose-preference-button', 0),
                 ('pgf-no-destiny-points', 0),
                 ('pgf-free-destiny-points', 0),
                 ('pgf-settings-container',0),
                 ('pgf-settings-tab-button', 1),
                 ('pgf-moderation-container', 0))

        self.request_logout()
        self.check_html_ok(self.request_html(url('game:heroes:show', self.hero.id)), texts=texts)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(url('game:heroes:show', self.hero.id)), texts=texts)

    def test_moderation_tab(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_id(account_id)
        self.request_login('test_user_2@test.com')

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(account_2._model)

        self.check_html_ok(self.request_html(url('game:heroes:show', self.hero.id)), texts=['pgf-moderation-container'])




class ChangePreferencesRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(ChangePreferencesRequestsTests, self).setUp()

    def test_chooce_preferences_dialog(self):
        self.hero._model.level = relations.PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required
        self.hero.save()

        for preference_type in relations.PREFERENCE_TYPE.records:
            texts = []
            self.check_html_ok(self.request_html(url('game:heroes:choose-preferences-dialog', self.hero.id) + ('?type=%d' % preference_type.value)), texts=texts)


class ChangeHeroRequestsTests(HeroRequestsTestBase):

    def test_hero_page(self):
        self.check_html_ok(self.request_html(url('game:heroes:show', self.hero.id)), texts=[jinja2.escape(self.hero.name),
                                                                                                       ('pgf-settings-approved-warning', 1)])

    def test_hero_page_change_name_warning_hidden(self):
        self.hero.settings_approved = True
        self.hero.save()
        self.check_html_ok(self.request_html(url('game:heroes:show', self.hero.id)), texts=[('pgf-settings-approved-warning', 0)])

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
                    properties=(gender.text_id, ))

    def test_chane_hero_ownership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error(self.client.post(url('game:heroes:change-hero', self.hero.id), self.get_post_data()),
                              'heroes.not_owner')

    def test_change_hero_form_errors(self):
        self.check_ajax_error(self.client.post(url('game:heroes:change-hero', self.hero.id), {}),
                              'heroes.change_name.form_errors')


    def test_change_hero(self):
        self.assertEqual(PostponedTask.objects.all().count(), 0)
        response = self.client.post(url('game:heroes:change-hero', self.hero.id), self.get_post_data())
        self.assertEqual(PostponedTask.objects.all().count(), 1)

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertEqual(task.internal_logic.name, self.get_name())
        self.assertEqual(task.internal_logic.gender, GENDER.MASCULINE)
        self.assertEqual(task.internal_logic.race, RACE.DWARF)


class ResetAbilitiesRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(ResetAbilitiesRequestsTests, self).setUp()

        self.hero.abilities.set_reseted_at(datetime.datetime.fromtimestamp(0))
        self.hero.abilities.updated = True
        self.hero.save()

    def test_wrong_ownership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error(self.post_ajax_json(url('game:heroes:reset-abilities', self.hero.id)),
                              'heroes.not_owner')

    def test_reset_timeout(self):
        self.hero.abilities.set_reseted_at(datetime.datetime.now())
        self.hero.abilities.updated = True
        self.hero.save()
        self.check_ajax_error(self.post_ajax_json(url('game:heroes:reset-abilities', self.hero.id)),
                              'heroes.reset_abilities.reset_timeout')


    def test_success(self):
        self.assertEqual(PostponedTask.objects.all().count(), 0)
        response = self.post_ajax_json(url('game:heroes:reset-abilities', self.hero.id))
        self.assertEqual(PostponedTask.objects.all().count(), 1)

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)


class GetCardRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(GetCardRequestsTests, self).setUp()

    def test_wrong_ownership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error(self.post_ajax_json(url('game:heroes:get-card', self.hero.id)),
                              'heroes.not_owner')


    def test_created(self):
        with self.check_delta(PostponedTask.objects.all().count, 1):
            response = self.post_ajax_json(url('game:heroes:get-card', self.hero.id))

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)


class CombineCardsRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(CombineCardsRequestsTests, self).setUp()

    def test_wrong_ownership(self):
        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.request_logout()
        self.request_login('test_user_2@test.com')
        with self.check_not_changed(PostponedTask.objects.all().count):
            self.check_ajax_error(self.post_ajax_json(url('game:heroes:combine-cards', self.hero.id, cards='%d' % CARD_TYPE.ADD_GOLD_COMMON.value)),
                                'heroes.not_owner')


    def test_created(self):

        self.hero.cards.add_card(CARD_TYPE.ADD_GOLD_COMMON, 2)
        self.hero.save()

        with self.check_delta(PostponedTask.objects.all().count, 1):
            response = self.post_ajax_json(url('game:heroes:combine-cards', self.hero.id, cards='%d,%d' % (CARD_TYPE.ADD_GOLD_COMMON.value, CARD_TYPE.ADD_GOLD_COMMON.value) ))

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

    def test_wrong_cards(self):

        for combine_status in relations.CARDS_COMBINING_STATUS.records:
            if combine_status.is_ALLOWED:
                continue

            with self.check_not_changed(PostponedTask.objects.all().count):
                self.check_ajax_error(self.post_ajax_json(url('game:heroes:combine-cards', self.hero.id, cards='%d' % CARD_TYPE.ADD_GOLD_COMMON.value)),
                                    'heroes.combine_cards.wrong_cards')


class ResetNameRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(ResetNameRequestsTests, self).setUp()

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_2._model)

        self.request_login('test_user_2@test.com')

    def test_chane_hero_moderation(self):
        self.request_logout()
        self.request_login('test_user@test.com')

        self.check_ajax_error(self.client.post(url('game:heroes:reset-name', self.hero.id)), 'heroes.moderator_rights_required')

    def test_change_hero(self):
        self.hero._model.name = '111'
        self.hero.save()

        self.assertEqual(PostponedTask.objects.all().count(), 0)
        response = self.client.post(url('game:heroes:reset-name', self.hero.id))
        self.assertEqual(PostponedTask.objects.all().count(), 1)

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertNotEqual(task.internal_logic.name, self.hero.name)
        self.assertEqual(task.internal_logic.gender, self.hero.gender)
        self.assertEqual(task.internal_logic.race, self.hero.race)


class ForceSaveRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(ForceSaveRequestsTests, self).setUp()

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        group = sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_2._model)

        self.request_login('test_user_2@test.com')

    def test_no_moderation_rights(self):
        self.request_logout()
        self.request_login('test_user@test.com')

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_force_save') as cmd_force_save:
            self.check_ajax_error(self.client.post(url('game:heroes:force-save', self.hero.id)), 'heroes.moderator_rights_required')

        self.assertEqual(cmd_force_save.call_args_list, [])

    def test_force_save(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_force_save') as cmd_force_save:
            self.check_ajax_ok(self.client.post(url('game:heroes:force-save', self.hero.id)))

        self.assertEqual(cmd_force_save.call_args_list, [mock.call(account_id=self.hero.account_id)])
