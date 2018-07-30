
import smart_imports

smart_imports.all()


class BaseRequestTests(utils_testcase.TestCase):

    def setUp(self):
        super(BaseRequestTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        group_edit_item = utils_permissions.sync_group('edit item', ['collections.edit_item'])
        group_moderate_item = utils_permissions.sync_group('moderate item', ['collections.moderate_item'])

        group_edit = utils_permissions.sync_group('edit kit', ['collections.edit_kit'])
        group_moderate = utils_permissions.sync_group('moderate kit', ['collections.moderate_kit'])

        group_edit_item.user_set.add(self.account_2._model)
        group_moderate_item.user_set.add(self.account_3._model)

        group_edit.user_set.add(self.account_2._model)
        group_moderate.user_set.add(self.account_3._model)

        self.collection_1 = prototypes.CollectionPrototype.create(caption='collection_1', description='description_1')
        self.collection_2 = prototypes.CollectionPrototype.create(caption='collection_2', description='description_2')

        self.kit_1 = prototypes.KitPrototype.create(collection=self.collection_1, caption='kit_1', description='description_1', approved=True)
        self.kit_2 = prototypes.KitPrototype.create(collection=self.collection_1, caption='kit_2', description='description_2')

        self.item_1_1 = prototypes.ItemPrototype.create(kit=self.kit_1, caption='item_1_1', text='text_1_1')
        self.item_1_2 = prototypes.ItemPrototype.create(kit=self.kit_1, caption='item_1_2', text='text_1_2', approved=True)


class KitsNewTests(BaseRequestTests):

    def setUp(self):
        super(KitsNewTests, self).setUp()
        self.test_url = dext_urls.url('collections:kits:new')

    def test_login_required(self):
        self.check_redirect(self.test_url, accounts_logic.login_page_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('collections.kits.no_edit_rights', 1)])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('collections.kits.no_edit_rights', 0)])


class KitsCreateTests(BaseRequestTests):

    def setUp(self):
        super(KitsCreateTests, self).setUp()
        self.create_url = dext_urls.url('collections:kits:create')

    def get_post_data(self):
        return {'collection': self.collection_1.id,
                'caption': 'caption_3',
                'description': 'description_3'}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.create_url, self.get_post_data()),
                              'common.login_required')
        self.assertEqual(prototypes.KitPrototype._db_all().count(), 2)

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.create_url, self.get_post_data()),
                              'collections.kits.no_edit_rights')
        self.assertEqual(prototypes.KitPrototype._db_all().count(), 2)

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.create_url, {}),
                              'collections.kits.create.form_errors')
        self.assertEqual(prototypes.KitPrototype._db_all().count(), 2)

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_ajax_ok(self.post_ajax_json(self.create_url, self.get_post_data()))
        self.assertEqual(prototypes.KitPrototype._db_all().count(), 3)

        kit = prototypes.KitPrototype._db_get_object(2)

        self.assertFalse(kit.approved)
        self.assertEqual(kit.collection_id, self.collection_1.id)
        self.assertEqual(kit.caption, 'caption_3')
        self.assertEqual(kit.description, 'description_3')


class KitsEditTests(BaseRequestTests):

    def setUp(self):
        super(KitsEditTests, self).setUp()
        self.test_url = dext_urls.url('collections:kits:edit', self.kit_2.id)

    def test_login_required(self):
        self.check_redirect(self.test_url, accounts_logic.login_page_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('collections.kits.no_edit_rights', 1)])

    def test_moderate_rights_required(self):
        self.kit_2.approved = True
        self.kit_2.save()

        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('collections.kits.no_edit_rights', 1)])

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.kit_2.caption,
                                  self.kit_2.description,
                                  ('collections.kits.no_edit_rights', 0)])

    def test_success__for_moderate(self):
        prototypes.KitPrototype._db_all().update(approved=True)
        storage.kits.refresh()

        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.kit_2.description,
                                  self.kit_2.caption])


class KitsUpdateTests(BaseRequestTests):

    def setUp(self):
        super(KitsUpdateTests, self).setUp()
        self.test_url = dext_urls.url('collections:kits:update', self.kit_2.id)

    def get_post_data(self):
        return {'caption': 'kit_edited',
                'description': 'description_edited',
                'collection': self.collection_2.id}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()), 'common.login_required')

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'collections.kits.no_edit_rights')

        self.kit_2.reload()
        self.assertEqual(self.kit_2.caption, 'kit_2')
        self.assertEqual(self.kit_2.description, 'description_2')
        self.assertEqual(self.kit_2.collection_id, self.collection_1.id)

    def test_moderate_rights_required(self):
        prototypes.KitPrototype._db_all().update(approved=True)
        storage.kits.refresh()

        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'collections.kits.no_edit_rights')

        self.kit_2.reload()
        self.assertEqual(self.kit_2.caption, 'kit_2')
        self.assertEqual(self.kit_2.description, 'description_2')
        self.assertEqual(self.kit_2.collection_id, self.collection_1.id)

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, {}),
                              'collections.kits.update.form_errors')

        self.kit_2.reload()
        self.assertEqual(self.kit_2.caption, 'kit_2')
        self.assertEqual(self.kit_2.description, 'description_2')
        self.assertEqual(self.kit_2.collection_id, self.collection_1.id)

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()))

        self.kit_2.reload()
        self.assertEqual(self.kit_2.caption, 'kit_edited')
        self.assertEqual(self.kit_2.description, 'description_edited')
        self.assertEqual(self.kit_2.collection_id, self.collection_2.id)

    def test_success__for_moderate(self):
        prototypes.KitPrototype._db_all().update(approved=True)
        storage.kits.refresh()

        self.request_login(self.account_3.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()),
                           data={'next_url': dext_urls.url('collections:collections:show', self.collection_2.id)})

        self.kit_2.reload()
        self.assertEqual(self.kit_2.caption, 'kit_edited')
        self.assertEqual(self.kit_2.description, 'description_edited')
        self.assertEqual(self.kit_2.collection_id, self.collection_2.id)


class KitsApproveTests(BaseRequestTests):

    def setUp(self):
        super(KitsApproveTests, self).setUp()
        self.approve_url = dext_urls.url('collections:kits:approve', self.kit_2.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.approve_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.approve_url), 'collections.kits.no_moderate_rights')

    def test_success(self):
        self.request_login(self.account_3.email)
        self.assertFalse(self.kit_2.approved)
        self.check_ajax_ok(self.post_ajax_json(self.approve_url))
        self.kit_2.reload()
        self.assertTrue(self.kit_2.approved)


class KitsDisapproveTests(BaseRequestTests):

    def setUp(self):
        super(KitsDisapproveTests, self).setUp()
        self.disapprove_url = dext_urls.url('collections:kits:disapprove', self.kit_2.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.disapprove_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.disapprove_url), 'collections.kits.no_moderate_rights')

    def test_success(self):
        prototypes.KitPrototype._db_all().update(approved=True)
        storage.kits.refresh()
        self.kit_2.reload()

        self.request_login(self.account_3.email)

        self.assertTrue(self.kit_2.approved)
        self.check_ajax_ok(self.post_ajax_json(self.disapprove_url))
        self.kit_2.reload()
        self.assertFalse(self.kit_2.approved)
