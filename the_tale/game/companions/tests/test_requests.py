# coding: utf-8

from dext.common.utils.urls import url

from the_tale.common.utils import testcase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts import logic as accounts_logic

from the_tale.linguistics.tests import helpers as linguistics_helpers

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.game.companions import logic
from the_tale.game.companions import models
from the_tale.game.companions import storage
from the_tale.game.companions import relations



class RequestsTestsBase(testcase.TestCase):

    def setUp(self):
        super(RequestsTestsBase, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        # self.request_login('test_user_1@test.com')

        group_edit = sync_group('edit companions', ['companions.create_companionrecord'])
        group_moderate = sync_group('moderate companions', ['companions.moderate_companionrecord'])

        group_edit.user_set.add(self.account_2._model)
        group_edit.user_set.add(self.account_3._model)
        group_moderate.user_set.add(self.account_3._model)



class IndexRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(IndexRequestsTests, self).setUp()
        self.requested_url = url('game:companions:')
        self.requested_url_disabled = url('game:companions:', state=relations.STATE.DISABLED.value)

        self.companion_1 = logic.create_companion_record(utg_name=names.generator.get_test_name(u'c-1'),
                                                         description='companion-description',
                                                         type=relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         rarity=relations.RARITY.random(),
                                                         state=relations.STATE.ENABLED)

        self.companion_2 = logic.create_companion_record(utg_name=names.generator.get_test_name(u'c-2'),
                                                         description='companion-description',
                                                         type=relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         rarity=relations.RARITY.random(),
                                                         state=relations.STATE.DISABLED)


    def test_no_items(self):
        models.CompanionRecord.objects.all().delete()
        storage.companions.refresh()
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 1),
                                                                         (self.companion_1.name, 0),
                                                                         (self.companion_2.name, 0)])

    def test_anonimouse_view(self):
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 0),
                                                                         (self.companion_1.name, 1),
                                                                         (self.companion_2.name, 0)])

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 0),
                                                                         (self.companion_1.name, 1),
                                                                         (self.companion_2.name, 0)])

    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 1),
                                                                         (self.companion_1.name, 1),
                                                                         (self.companion_2.name, 0)])

    def test_moderator_view(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 1),
                                                                         (self.companion_1.name, 1),
                                                                         (self.companion_2.name, 0)])

    def test_normal_view__disabled_records(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url_disabled), texts=[('pgf-no-companions-message', 1),
                                                                         ('pgf-create-companion-button', 0),
                                                                         (self.companion_1.name, 0),
                                                                         (self.companion_2.name, 0)])

    def test_editor_view__disabled_records(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url_disabled), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 1),
                                                                         (self.companion_1.name, 0),
                                                                         (self.companion_2.name, 1)])


    def test_moderator_view__disabled_records(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.requested_url_disabled), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 1),
                                                                         (self.companion_1.name, 0),
                                                                         (self.companion_2.name, 1)])



class NewRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(NewRequestsTests, self).setUp()

        self.requested_url = url('game:companions:new')

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        group_edit = sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)


    def test_anonimouse_view(self):
        self.check_redirect(self.requested_url, accounts_logic.login_page_url(self.requested_url))

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=['companions.no_edit_rights'])

    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('companions.no_edit_rights', 0)])


class CreateRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(CreateRequestsTests, self).setUp()

        self.requested_url = url('game:companions:create')

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        group_edit = sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

    def post_data(self):
        data = {'description': 'some-description',
                'type': relations.TYPE.random(),
                'max_health': 666,
                'dedication': relations.DEDICATION.random(),
                'rarity': relations.RARITY.random()}
        data.update(linguistics_helpers.get_word_post_data(names.generator.get_test_name(name='name'), prefix='name'))
        return data

    def test_anonimouse_view(self):
        self.check_ajax_error(self.post_ajax_json(self.requested_url, self.post_data()), 'common.login_required')


    def test_normal_user(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.requested_url, self.post_data()), 'companions.no_edit_rights')

    def test_editor_user(self):
        self.request_login(self.account_2.email)

        post_data = self.post_data()

        with self.check_delta(models.CompanionRecord.objects.count, 1):
            with self.check_changed(lambda: storage.companions._version):
                with self.check_delta(lambda: len(storage.companions), 1):
                    response = self.post_ajax_json(self.requested_url, post_data)

        new_companion = logic.get_last_companion()

        self.check_ajax_ok(response, data={'next_url': url('guide:companions:show', new_companion.id)})

        self.assertEqual(new_companion.description, 'some-description')
        self.assertTrue(new_companion.state.is_DISABLED)
        self.assertEqual(new_companion.type, post_data['type'])
        self.assertEqual(new_companion.max_health, post_data['max_health'])
        self.assertEqual(new_companion.dedication, post_data['dedication'])
        self.assertEqual(new_companion.rarity, post_data['rarity'])
        self.assertEqual(new_companion.name, u'name-нс,ед,им')


    def test_form_errors(self):
        self.request_login(self.account_2.email)

        with self.check_not_changed(models.CompanionRecord.objects.count):
            with self.check_not_changed(lambda: storage.companions._version):
                with self.check_not_changed(storage.companions.__len__):
                    self.check_ajax_error(self.post_ajax_json(self.requested_url, {}), 'companions.create.form_errors')


class ShowRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(ShowRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=names.generator.get_test_name(u'c-1'),
                                                         description='companion-description-1',
                                                         type=relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         rarity=relations.RARITY.random(),
                                                         state=relations.STATE.ENABLED)

        self.companion_2 = logic.create_companion_record(utg_name=names.generator.get_test_name(u'c-2'),
                                                         description='companion-description-2',
                                                         type=relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         rarity=relations.RARITY.random(),
                                                         state=relations.STATE.DISABLED)

        self.requested_url_1 = url('game:companions:show', self.companion_1.id)
        self.requested_url_2 = url('game:companions:show', self.companion_2.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        group_edit = sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

        group_moderate = sync_group('moderate companions', ['companions.moderate_companionrecord'])
        group_moderate.user_set.add(self.account_3._model)


    def test_anonimouse_view(self):
        self.check_html_ok(self.request_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('companions.show.no_rights', 0),
                                                                           ('pgf-edit-companion-button', 0),
                                                                           ('pgf-enable-companion-button', 0)])

    def test_anonimouse_view__companion_disabled(self):
        self.check_html_ok(self.request_html(self.requested_url_2), texts=[(self.companion_2.description, 0),
                                                                           ('companions.show.no_rights', 1),
                                                                           ('pgf-edit-companion-button', 0),
                                                                           ('pgf-enable-companion-button', 0)])


    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('companions.show.no_rights', 0),
                                                                           ('pgf-edit-companion-button', 0),
                                                                           ('pgf-enable-companion-button', 0)])

    def test_normal_view__companion_disabled(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url_2), texts=[(self.companion_2.description, 0),
                                                                           ('companions.show.no_rights', 1),
                                                                           ('pgf-edit-companion-button', 0),
                                                                           ('pgf-enable-companion-button', 0)])


    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('companions.show.no_rights', 0),
                                                                           ('pgf-edit-companion-button', 1),
                                                                           ('pgf-enable-companion-button', 0)])


    def test_editor_view__companion_disabled(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url_2), texts=[(self.companion_2.description, 1),
                                                                           ('companions.show.no_rights', 0),
                                                                           ('pgf-edit-companion-button', 1),
                                                                           ('pgf-enable-companion-button', 0)])

    def test_moderator_view(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('companions.show.no_rights', 0),
                                                                           ('pgf-edit-companion-button', 1),
                                                                           ('pgf-enable-companion-button', 0)])


    def test_moderator_view__companion_disabled(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.requested_url_2), texts=[(self.companion_2.description, 1),
                                                                           ('companions.show.no_rights', 0),
                                                                           ('pgf-edit-companion-button', 1),
                                                                           ('pgf-enable-companion-button', 1)])


class InfoRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(InfoRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=names.generator.get_test_name(u'c-1'),
                                                         description='companion-description-1',
                                                         type=relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         rarity=relations.RARITY.random(),
                                                         state=relations.STATE.ENABLED)

        self.companion_2 = logic.create_companion_record(utg_name=names.generator.get_test_name(u'c-2'),
                                                         description='companion-description-2',
                                                         type=relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         rarity=relations.RARITY.random(),
                                                         state=relations.STATE.DISABLED)

        self.requested_url_1 = url('game:companions:info', self.companion_1.id)
        self.requested_url_2 = url('game:companions:info', self.companion_2.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        group_edit = sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

        group_moderate = sync_group('moderate companions', ['companions.moderate_companionrecord'])
        group_moderate.user_set.add(self.account_3._model)


    def test_anonimouse_view(self):
        self.check_html_ok(self.request_ajax_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('companions.info.no_rights', 0)])

    def test_anonimouse_view__companion_disabled(self):
        self.check_html_ok(self.request_ajax_html(self.requested_url_2), texts=[(self.companion_2.description, 0),
                                                                           ('companions.info.no_rights', 1)])


    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('companions.info.no_rights', 0)])

    def test_normal_view__companion_disabled(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_2), texts=[(self.companion_2.description, 0),
                                                                           ('companions.info.no_rights', 1)])


    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('companions.info.no_rights', 0)])


    def test_editor_view__companion_disabled(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_2), texts=[(self.companion_2.description, 1),
                                                                           ('companions.info.no_rights', 0)])

    def test_moderator_view(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('companions.info.no_rights', 0)])


    def test_moderator_view__companion_disabled(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_2), texts=[(self.companion_2.description, 1),
                                                                           ('companions.info.no_rights', 0)])




class EditRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(EditRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=names.generator.get_test_name(u'c-1'),
                                                       description='companion-description-1',
                                                         type=relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         rarity=relations.RARITY.random(),
                                                       state=relations.STATE.DISABLED)


        self.requested_url = url('game:companions:edit', self.companion_1.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        group_edit = sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)


    def test_anonimouse_view(self):
        self.check_redirect(self.requested_url, accounts_logic.login_page_url(self.requested_url))

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=['companions.no_edit_rights'])

    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('companions.no_edit_rights', 0),
                                                                         self.companion_1.name,
                                                                         self.companion_1.description])




class UpdateRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(UpdateRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=names.generator.get_test_name(u'c-1'),
                                                         description='companion-description-1',
                                                         type=relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         rarity=relations.RARITY.random(),
                                                         state=relations.STATE.DISABLED)

        self.requested_url = url('game:companions:update', self.companion_1.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        group_edit = sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

    def post_data(self):
        data = {'description': 'new-description',
                'type': relations.TYPE.random(),
                'max_health': 666,
                'dedication': relations.DEDICATION.random(),
                'rarity': relations.RARITY.random()}
        data.update(linguistics_helpers.get_word_post_data(names.generator.get_test_name(name='new_name'), prefix='name'))
        return data

    def test_anonimouse_view(self):
        self.check_ajax_error(self.post_ajax_json(self.requested_url, self.post_data()), 'common.login_required')

    def test_normal_user(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.requested_url, self.post_data()), 'companions.no_edit_rights')

    def test_editor_user(self):
        self.request_login(self.account_2.email)

        post_data = self.post_data()

        with self.check_not_changed(models.CompanionRecord.objects.count):
            with self.check_changed(lambda: storage.companions._version):
                with self.check_not_changed(storage.companions.__len__):
                    self.check_ajax_ok(self.post_ajax_json(self.requested_url, post_data),
                                       data={'next_url': url('guide:companions:show', self.companion_1.id)})

        # storage.companions.refresh()

        companion = storage.companions[self.companion_1.id]

        self.assertEqual(companion.description, 'new-description')
        self.assertTrue(companion.state.is_DISABLED)
        self.assertEqual(companion.type, post_data['type'])
        self.assertEqual(companion.max_health, post_data['max_health'])
        self.assertEqual(companion.dedication, post_data['dedication'])
        self.assertEqual(companion.rarity, post_data['rarity'])
        self.assertEqual(companion.name, u'new_name-нс,ед,им')


    def test_form_errors(self):
        self.request_login(self.account_2.email)

        with self.check_not_changed(models.CompanionRecord.objects.count):
            with self.check_not_changed(lambda: storage.companions._version):
                with self.check_not_changed(storage.companions.__len__):
                    self.check_ajax_error(self.post_ajax_json(self.requested_url, {}), 'companions.update.form_errors')

        companion = storage.companions[self.companion_1.id]

        self.assertEqual(companion.description, self.companion_1.description)
        self.assertEqual(companion.name, self.companion_1.name)


class EnableRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(EnableRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=names.generator.get_test_name(u'c-1'),
                                                         description='companion-description-1',
                                                         type=relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         rarity=relations.RARITY.random(),
                                                         state=relations.STATE.DISABLED)

        self.requested_url = url('game:companions:enable', self.companion_1.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        group_edit = sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

        group_edit = sync_group('moderate companions', ['companions.moderate_companionrecord'])
        group_edit.user_set.add(self.account_3._model)

    def test_anonimouse_view(self):
        self.check_ajax_error(self.post_ajax_json(self.requested_url), 'common.login_required')

    def test_normal_user(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.requested_url), 'companions.no_moderate_rights')

    def test_editor_user(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.requested_url), 'companions.no_moderate_rights')

    def test_moderator_user(self):
        self.request_login(self.account_3.email)

        with self.check_not_changed(models.CompanionRecord.objects.count):
            with self.check_changed(lambda: storage.companions._version):
                with self.check_not_changed(storage.companions.__len__):
                    self.check_ajax_ok(self.post_ajax_json(self.requested_url))

        companion = storage.companions[self.companion_1.id]

        self.assertTrue(companion.state.is_ENABLED)
