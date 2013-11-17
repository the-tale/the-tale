# coding: utf-8

from dext.utils.urls import url

from the_tale.common.utils import testcase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url
from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE
from the_tale.accounts.achievements.prototypes import AchievementPrototype, AccountAchievementsPrototype, GiveAchievementTaskPrototype

from the_tale.game.logic import create_test_map



class _BaseRequestTests(testcase.TestCase):

    def setUp(self):
        super(_BaseRequestTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        group_edit = sync_group('edit achievement', ['achievements.edit_achievement'])

        group_edit.user_set.add(self.account_2._model)

        self.achievement_1 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=0, points=10,
                                                         caption=u'achievement_1', description=u'description_1', approved=True)
        self.achievement_2 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=2, points=10,
                                                         caption=u'achievement_2', description=u'description_2', approved=False)
        self.achievement_3 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.TIME, type=ACHIEVEMENT_TYPE.TIME, barrier=3, points=10,
                                                         caption=u'achievement_3', description=u'description_3', approved=True)


        self.account_achievements_1 = AccountAchievementsPrototype.get_by_account_id(self.account_1.id)
        self.account_achievements_1.achievements.add_achievement(self.achievement_1)
        self.account_achievements_1.save()


class AchievementsIndexTests(_BaseRequestTests):

    def setUp(self):
        super(AchievementsIndexTests, self).setUp()
        self.test_url = url('accounts:achievements:')

    def test_redirect(self):
        self.check_redirect(self.test_url, url('accounts:achievements:group', sorted(ACHIEVEMENT_GROUP._records, key=lambda group: group.name)[0].slug))



class AchievementsGroupTests(_BaseRequestTests):

    def setUp(self):
        super(AchievementsGroupTests, self).setUp()
        self.test_url = url('accounts:achievements:group', ACHIEVEMENT_GROUP.MONEY.slug)

    def test__for_no_user(self):
        self.check_html_ok(self.request_html(self.test_url), texts=[self.achievement_1.caption,
                                                                    ACHIEVEMENT_GROUP.MONEY.text,
                                                                    (self.achievement_2.caption, 0),
                                                                    (self.achievement_3.caption, 0),
                                                                    ('pgf-owned', 0),
                                                                    ('pgf-add-achievement-button', 0),
                                                                    ('pgf-edit-achievement-button', 0)])

    def test__for_normal_user(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url), texts=[self.achievement_1.caption,
                                                                    ACHIEVEMENT_GROUP.MONEY.text,
                                                                    (self.achievement_2.caption, 0),
                                                                    (self.achievement_3.caption, 0),
                                                                    'pgf-owned',
                                                                    ('pgf-add-achievement-button', 0),
                                                                    ('pgf-edit-achievement-button', 0)])

    def test__for_editor(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url), texts=[self.achievement_1.caption,
                                                                    ACHIEVEMENT_GROUP.MONEY.text,
                                                                    self.achievement_2.caption,
                                                                    ('pgf-owned', 0),
                                                                    (self.achievement_3.caption, 0),
                                                                    'pgf-add-achievement-button',
                                                                    'pgf-edit-achievement-button'])




class AchievementsNewTests(_BaseRequestTests):

    def setUp(self):
        super(AchievementsNewTests, self).setUp()
        self.test_url = url('accounts:achievements:new')

    def test_login_required(self):
        self.check_redirect(self.test_url, login_page_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url), texts=['accounts.achievements.no_edit_rights'])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url), texts=[('accounts.achievements.no_edit_rights', 0)])



class AchievementsCreateTests(_BaseRequestTests):

    def setUp(self):
        super(AchievementsCreateTests, self).setUp()
        self.test_url = url('accounts:achievements:create')

    def get_post_data(self):
        return {'caption': 'caption_create',
                'description': u'description_create',
                'order': 666,
                'barrier': 777,
                'type': ACHIEVEMENT_TYPE.DEATHS,
                'group': ACHIEVEMENT_GROUP.DEATHS,
                'points': 20}

    def test_login_required(self):
        with self.check_not_changed(AchievementPrototype._db_all().count):
            with self.check_not_changed(GiveAchievementTaskPrototype._db_all().count):
                self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                                      'common.login_required')

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        with self.check_not_changed(AchievementPrototype._db_all().count):
            with self.check_not_changed(GiveAchievementTaskPrototype._db_all().count):
                self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                                      'accounts.achievements.no_edit_rights')

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        with self.check_not_changed(AchievementPrototype._db_all().count):
            with self.check_not_changed(GiveAchievementTaskPrototype._db_all().count):
                self.check_ajax_error(self.post_ajax_json(self.test_url, {}),
                                      'accounts.achievements.create.form_errors')

    def test_success(self):
        self.request_login(self.account_2.email)
        with self.check_delta(AchievementPrototype._db_all().count, 1):
            with self.check_delta(GiveAchievementTaskPrototype._db_all().count, 1):
                response = self.post_ajax_json(self.test_url, self.get_post_data())

        achievement = AchievementPrototype._db_get_object(3)

        self.check_ajax_ok(response, data={'next_url': url('accounts:achievements:group', achievement.group.slug)})

        self.assertEqual(achievement.caption, 'caption_create')
        self.assertEqual(achievement.description, 'description_create')
        self.assertEqual(achievement.type, ACHIEVEMENT_TYPE.DEATHS)
        self.assertEqual(achievement.group, ACHIEVEMENT_GROUP.DEATHS)
        self.assertEqual(achievement.barrier, 777)
        self.assertEqual(achievement.points, 20)
        self.assertFalse(achievement.approved)


class AchievementsEditTests(_BaseRequestTests):

    def setUp(self):
        super(AchievementsEditTests, self).setUp()
        self.test_url = url('accounts:achievements:edit', self.achievement_1.id)

    def test_login_required(self):
        self.check_redirect(self.test_url, login_page_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=(('accounts.achievements.no_edit_rights', 1)))

    def test_wrong_format(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(url('accounts:achievements:edit', 'bla')),
                           texts=(('accounts.achievements.achievement.wrong_format', 1)))

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url), texts=[('pgf-error-page-message', 0)])


class AchievementsUpdateTests(_BaseRequestTests):

    def setUp(self):
        super(AchievementsUpdateTests, self).setUp()
        self.test_url = url('accounts:achievements:update', self.achievement_2.id)

    def get_post_data(self):
        return {'caption': 'caption_edited',
                'description': u'description_edited',
                'order': 666,
                'barrier': 777,
                'type': ACHIEVEMENT_TYPE.DEATHS,
                'group': ACHIEVEMENT_GROUP.DEATHS,
                'approved': True,
                'points': 6}


    def test_login_required(self):
        with self.check_not_changed(GiveAchievementTaskPrototype._db_all().count):
            self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()), 'common.login_required')

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        with self.check_not_changed(GiveAchievementTaskPrototype._db_all().count):
            self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                                  'accounts.achievements.no_edit_rights')

        self.achievement_1.reload()
        self.assertEqual(self.achievement_1.caption, 'achievement_1')
        self.assertEqual(self.achievement_1.description, 'description_1')


    def test_form_errors(self):
        self.request_login(self.account_2.email)
        with self.check_not_changed(GiveAchievementTaskPrototype._db_all().count):
            self.check_ajax_error(self.post_ajax_json(self.test_url, {}),
                                  'accounts.achievements.update.form_errors')

        self.achievement_1.reload()
        self.assertEqual(self.achievement_1.caption, 'achievement_1')
        self.assertEqual(self.achievement_1.description, 'description_1')

    def test_success(self):
        self.request_login(self.account_2.email)
        with self.check_delta(GiveAchievementTaskPrototype._db_all().count, 1):
            response = self.post_ajax_json(self.test_url, self.get_post_data())

        self.achievement_2.reload()

        self.check_ajax_ok(response, data={'next_url': url('accounts:achievements:group', self.achievement_2.group.slug)})

        self.assertEqual(self.achievement_2.caption, 'caption_edited')
        self.assertEqual(self.achievement_2.description, 'description_edited')
        self.assertEqual(self.achievement_2.type, ACHIEVEMENT_TYPE.DEATHS)
        self.assertEqual(self.achievement_2.group, ACHIEVEMENT_GROUP.DEATHS)
        self.assertEqual(self.achievement_2.barrier, 777)
        self.assertTrue(self.achievement_2.approved)
        self.assertEqual(self.achievement_2.points, 6)
