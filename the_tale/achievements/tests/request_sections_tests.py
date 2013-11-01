# coding: utf-8

from dext.utils.urls import url

from common.utils import testcase
from common.utils.permissions import sync_group

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url


from game.logic import create_test_map


from achievements.prototypes import SectionPrototype, KitPrototype


class BaseRequestTests(testcase.TestCase):

    def setUp(self):
        super(BaseRequestTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        self.account_3 = AccountPrototype.get_by_id(account_id)

        group_edit = sync_group('edit section', ['achievements.edit_section'])
        group_moderate = sync_group('moderate section', ['achievements.moderate_section'])

        group_edit.account_set.add(self.account_2._model)
        group_moderate.account_set.add(self.account_3._model)


        self.section_1 = SectionPrototype.create(caption=u'section_1', description=u'description_1')
        self.section_2 = SectionPrototype.create(caption=u'section_2', description=u'description_2', approved=True)

        self.kit_1 = KitPrototype.create(section=self.section_1, caption=u'kit_1', description=u'description_1')
        self.kit_2 = KitPrototype.create(section=self.section_2, caption=u'kit_2', description=u'description_2')



class SectionVisibilityAllMixin(object):

    def test_visible_sections__all(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url), texts=[self.section_1.caption,
                                                                    self.section_2.caption])


class SectionVisibilityApprovedMixin(SectionVisibilityAllMixin):

    def test_visible_sections__aproved_only(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url), texts=[(self.section_1.caption, 0),
                                                                    self.section_2.caption])



class SectionsIndexTests(BaseRequestTests, SectionVisibilityAllMixin):

    def setUp(self):
        super(SectionsIndexTests, self).setUp()
        self.test_url = url('achievements:sections:')

    def test_login_required(self):
        self.check_redirect(self.test_url, login_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('achievements.sections.no_edit_rights', 1)])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('achievements.sections.no_edit_rights', 0)])



class SectionsNewTests(BaseRequestTests, SectionVisibilityAllMixin):

    def setUp(self):
        super(SectionsNewTests, self).setUp()
        self.test_url = url('achievements:sections:new')

    def test_login_required(self):
        self.check_redirect(self.test_url, login_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('achievements.sections.no_edit_rights', 1)])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('achievements.sections.no_edit_rights', 0)])



class SectionsCreateTests(BaseRequestTests):

    def setUp(self):
        super(SectionsCreateTests, self).setUp()
        self.test_url = url('achievements:sections:create')

    def get_post_data(self):
        return {'caption': 'caption_3',
                'description': u'description_3'}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'common.login_required')
        self.assertEqual(SectionPrototype._db_all().count(), 2)

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'achievements.sections.no_edit_rights')
        self.assertEqual(SectionPrototype._db_all().count(), 2)

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, {}),
                              'achievements.sections.create.form_errors')
        self.assertEqual(SectionPrototype._db_all().count(), 2)

    def test_success(self):
        self.request_login(self.account_2.email)

        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()))
        self.assertEqual(SectionPrototype._db_all().count(), 3)

        section = SectionPrototype._db_get_object(2)

        self.assertFalse(section.approved)
        self.assertEqual(section.caption, 'caption_3')
        self.assertEqual(section.description, 'description_3')


class SectionsShowTests(BaseRequestTests, SectionVisibilityApprovedMixin):

    def setUp(self):
        super(SectionsShowTests, self).setUp()
        self.test_url = url('achievements:sections:show', self.section_2.id)

    def test_success(self):
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.section_2.caption,
                                  self.kit_2.caption,
                                  (self.section_1.caption, 0),
                                  (self.kit_1.caption, 0),
                                  ('pgf-no-kits-message', 0)])


    def test_access_restricted(self):
        self.check_html_ok(self.request_html(url('achievements:sections:show', self.section_1.id)),
                           status_code=404,
                           texts=[(self.section_1.caption, 0),
                                  (self.kit_1.caption, 0),
                                  (self.section_2.caption, 0),
                                  (self.kit_2.caption, 0),
                                  ('pgf-no-kits-message', 0),
                                  ('achievements.sections.not_approved', 1)])

    def test_no_kits_in_section(self):
        KitPrototype._db_all().delete()
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.section_2.caption,
                                  (self.kit_2.caption, 0),
                                  (self.section_1.caption, 0),
                                  (self.kit_1.caption, 0),
                                  ('pgf-no-kits-message', 1)])

    def test_buttons__anonymouse(self):
        self.check_html_ok(self.request_html(self.test_url), texts=[('pgf-edit-section-button', 0),
                                                                    ('pgf-approve-section-button', 0),
                                                                    ('pgf-disapprove-section-button', 0)])

    def test_buttons__no_rights(self):
        self.check_html_ok(self.request_html(self.test_url), texts=[('pgf-edit-section-button', 0),
                                                                    ('pgf-approve-section-button', 0),
                                                                    ('pgf-disapprove-section-button', 0)])

    def test_buttons__edit_rights(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url), texts=[('pgf-edit-section-button', 0),
                                                                    ('pgf-approve-section-button', 0),
                                                                    ('pgf-disapprove-section-button', 0)])

        self.section_2.approved = False
        self.section_2.save()

        self.check_html_ok(self.request_html(self.test_url), texts=[('pgf-edit-section-button', 1),
                                                                    ('pgf-approve-section-button', 0),
                                                                    ('pgf-disapprove-section-button', 0)])

    def test_buttons__moderate_rights(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.test_url), texts=[('pgf-edit-section-button', 1),
                                                                    ('pgf-approve-section-button', 0),
                                                                    ('pgf-disapprove-section-button', 1)])
        self.section_2.approved = False
        self.section_2.save()

        self.check_html_ok(self.request_html(self.test_url), texts=[('pgf-edit-section-button', 1),
                                                                    ('pgf-approve-section-button', 1),
                                                                    ('pgf-disapprove-section-button', 0)])


class SectionsEditTests(BaseRequestTests, SectionVisibilityAllMixin):

    def setUp(self):
        super(SectionsEditTests, self).setUp()
        self.test_url = url('achievements:sections:edit', self.section_1.id)

    def test_login_required(self):
        self.check_redirect(self.test_url, login_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=(('achievements.sections.no_edit_rights', 1)))


    def test_moderate_rights_required(self):
        SectionPrototype._db_all().update(approved=True)

        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=(('achievements.sections.no_edit_rights', 1)))

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.section_1.caption,
                                  self.section_1.description])

    def test_success__for_moderate(self):
        SectionPrototype._db_all().update(approved=True)

        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.section_1.caption,
                                  self.section_1.description])


class SectionsUpdateTests(BaseRequestTests):

    def setUp(self):
        super(SectionsUpdateTests, self).setUp()
        self.test_url = url('achievements:sections:update', self.section_1.id)

    def get_post_data(self):
        return {'caption': 'section_edited',
                'description': 'description_edited'}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()), 'common.login_required')

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'achievements.sections.no_edit_rights')

        self.section_1.reload()
        self.assertEqual(self.section_1.caption, 'section_1')
        self.assertEqual(self.section_1.description, 'description_1')


    def test_moderate_rights_required(self):
        SectionPrototype._db_all().update(approved=True)

        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'achievements.sections.no_edit_rights')
        self.section_1.reload()
        self.assertEqual(self.section_1.caption, 'section_1')
        self.assertEqual(self.section_1.description, 'description_1')

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, {}),
                              'achievements.sections.update.form_errors')

        self.section_1.reload()
        self.assertEqual(self.section_1.caption, 'section_1')
        self.assertEqual(self.section_1.description, 'description_1')

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()))

        self.section_1.reload()
        self.assertEqual(self.section_1.caption, 'section_edited')
        self.assertEqual(self.section_1.description, 'description_edited')

    def test_success__for_moderate(self):
        SectionPrototype._db_all().update(approved=True)

        self.request_login(self.account_3.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()))

        self.section_1.reload()
        self.assertEqual(self.section_1.caption, 'section_edited')
        self.assertEqual(self.section_1.description, 'description_edited')



class SectionsApproveTests(BaseRequestTests):

    def setUp(self):
        super(SectionsApproveTests, self).setUp()
        self.approve_url = url('achievements:sections:approve', self.section_1.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.approve_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.approve_url), 'achievements.sections.no_moderate_rights')

    def test_success(self):
        self.request_login(self.account_3.email)
        self.assertFalse(self.section_1.approved)
        self.check_ajax_ok(self.post_ajax_json(self.approve_url))
        self.section_1.reload()
        self.assertTrue(self.section_1.approved)



class SectionsDisapproveTests(BaseRequestTests):

    def setUp(self):
        super(SectionsDisapproveTests, self).setUp()
        self.disapprove_url = url('achievements:sections:disapprove', self.section_1.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.disapprove_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.disapprove_url), 'achievements.sections.no_moderate_rights')

    def test_success(self):
        SectionPrototype._db_all().update(approved=True)
        self.section_1.reload()

        self.request_login(self.account_3.email)

        self.assertTrue(self.section_1.approved)
        self.check_ajax_ok(self.post_ajax_json(self.disapprove_url))
        self.section_1.reload()
        self.assertFalse(self.section_1.approved)
