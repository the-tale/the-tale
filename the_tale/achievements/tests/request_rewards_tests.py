# coding: utf-8

from dext.utils.urls import url

from common.utils import testcase
from common.utils.permissions import sync_group

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url


from game.logic import create_test_map


from achievements.prototypes import SectionPrototype, KitPrototype, RewardPrototype


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

        group_edit = sync_group('edit reward', ['achievements.edit_reward'])
        group_moderate = sync_group('moderate reward', ['achievements.moderate_reward'])

        group_edit.account_set.add(self.account_2._model)
        group_moderate.account_set.add(self.account_3._model)

        self.section_1 = SectionPrototype.create(caption=u'section_1', description=u'description_1')
        self.section_2 = SectionPrototype.create(caption=u'section_2', description=u'description_2')

        self.kit_1 = KitPrototype.create(section=self.section_1, caption=u'kit_1', description=u'description_1')
        self.kit_2 = KitPrototype.create(section=self.section_1, caption=u'kit_2', description=u'description_2')

        self.reward_1_1 = RewardPrototype.create(kit=self.kit_1, caption=u'reward_1_1', text=u'text_1_1')
        self.reward_1_2 = RewardPrototype.create(kit=self.kit_1, caption=u'reward_1_2', text=u'text_1_2')


class RewardsNewTests(BaseRequestTests):

    def setUp(self):
        super(RewardsNewTests, self).setUp()
        self.test_url = url('achievements:rewards:new')

    def test_login_required(self):
        self.check_redirect(self.test_url, login_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('achievements.rewards.no_edit_rights', 1)])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('achievements.rewards.no_edit_rights', 0)])


class RewardsCreateTests(BaseRequestTests):

    def setUp(self):
        super(RewardsCreateTests, self).setUp()
        self.test_url = url('achievements:rewards:create')

    def get_post_data(self):
        return {'kit': self.kit_1.id,
                'caption': 'caption_3',
                'text': 'text_3'}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'common.login_required')
        self.assertEqual(RewardPrototype._db_all().count(), 2)

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'achievements.rewards.no_edit_rights')
        self.assertEqual(RewardPrototype._db_all().count(), 2)

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, {}),
                              'achievements.rewards.create.form_errors')
        self.assertEqual(RewardPrototype._db_all().count(), 2)

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()), {'next_url': url('achievements:kits:show', self.kit_1.id)})
        self.assertEqual(RewardPrototype._db_all().count(), 3)

        reward = RewardPrototype._db_get_object(2)

        self.assertFalse(reward.approved)
        self.assertEqual(reward.kit_id, self.kit_1.id)
        self.assertEqual(reward.caption, 'caption_3')
        self.assertEqual(reward.text, 'text_3')



class RewardsEditTests(BaseRequestTests):

    def setUp(self):
        super(RewardsEditTests, self).setUp()
        self.test_url = url('achievements:rewards:edit', self.reward_1_1.id)

    def test_login_required(self):
        self.check_redirect(self.test_url, login_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=(('achievements.rewards.no_edit_rights', 1)))


    def test_moderate_rights_required(self):
        RewardPrototype._db_all().update(approved=True)

        self.request_login(self.account_2.email)

        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('achievements.rewards.no_edit_rights', 1)])

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.kit_1.caption,
                                  self.reward_1_1.caption,
                                  self.reward_1_1.text])

    def test_success__for_moderate(self):
        KitPrototype._db_all().update(approved=True)

        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.kit_1.caption,
                                  self.reward_1_1.caption,
                                  self.reward_1_1.text])


class RewardsUpdateTests(BaseRequestTests):

    def setUp(self):
        super(RewardsUpdateTests, self).setUp()
        self.test_url = url('achievements:rewards:update', self.reward_1_1.id)

    def get_post_data(self):
        return {'caption': 'caption_edited',
                'text': 'text_edited',
                'kit': self.kit_2.id}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()), 'common.login_required')

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'achievements.rewards.no_edit_rights')

        self.reward_1_1.reload()
        self.assertEqual(self.reward_1_1.caption, 'reward_1_1')
        self.assertEqual(self.reward_1_1.text, 'text_1_1')
        self.assertEqual(self.reward_1_1.kit_id, self.kit_1.id)


    def test_moderate_rights_required(self):
        RewardPrototype._db_all().update(approved=True)

        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'achievements.rewards.no_edit_rights')

        self.reward_1_1.reload()
        self.assertEqual(self.reward_1_1.caption, 'reward_1_1')
        self.assertEqual(self.reward_1_1.text, 'text_1_1')
        self.assertEqual(self.reward_1_1.kit_id, self.section_1.id)

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, {}),
                              'achievements.rewards.update.form_errors')

        self.reward_1_1.reload()
        self.assertEqual(self.reward_1_1.caption, 'reward_1_1')
        self.assertEqual(self.reward_1_1.text, 'text_1_1')
        self.assertEqual(self.reward_1_1.kit_id, self.section_1.id)

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()))

        self.reward_1_1.reload()
        self.assertEqual(self.reward_1_1.caption, 'caption_edited')
        self.assertEqual(self.reward_1_1.text, 'text_edited')
        self.assertEqual(self.reward_1_1.kit_id, self.kit_2.id)

    def test_success__for_moderate(self):
        RewardPrototype._db_all().update(approved=True)

        self.request_login(self.account_3.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()))

        self.reward_1_1.reload()
        self.assertEqual(self.reward_1_1.caption, 'caption_edited')
        self.assertEqual(self.reward_1_1.text, 'text_edited')
        self.assertEqual(self.reward_1_1.kit_id, self.kit_2.id)



class RewardsApproveTests(BaseRequestTests):

    def setUp(self):
        super(RewardsApproveTests, self).setUp()
        self.test_url = url('achievements:rewards:approve', self.reward_1_1.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url), 'achievements.rewards.no_moderate_rights')

    def test_success(self):
        self.request_login(self.account_3.email)
        self.assertFalse(self.reward_1_1.approved)
        self.check_ajax_ok(self.post_ajax_json(self.test_url))
        self.reward_1_1.reload()
        self.assertTrue(self.reward_1_1.approved)



class RewardsDisapproveTests(BaseRequestTests):

    def setUp(self):
        super(RewardsDisapproveTests, self).setUp()
        self.test_url = url('achievements:rewards:disapprove', self.reward_1_1.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url), 'achievements.rewards.no_moderate_rights')

    def test_success(self):
        RewardPrototype._db_all().update(approved=True)
        self.reward_1_1.reload()

        self.request_login(self.account_3.email)

        self.assertTrue(self.reward_1_1.approved)
        self.check_ajax_ok(self.post_ajax_json(self.test_url))
        self.reward_1_1.reload()
        self.assertFalse(self.reward_1_1.approved)
