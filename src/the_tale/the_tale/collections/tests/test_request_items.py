
import smart_imports

smart_imports.all()


class BaseRequestTests(utils_testcase.TestCase):

    def setUp(self):
        super(BaseRequestTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit item', ['collections.edit_item'])
        group_moderate = utils_permissions.sync_group('moderate item', ['collections.moderate_item'])

        group_edit.user_set.add(self.account_2._model)
        group_moderate.user_set.add(self.account_3._model)

        self.collection_1 = prototypes.CollectionPrototype.create(caption='collection_1', description='description_1')
        self.collection_2 = prototypes.CollectionPrototype.create(caption='collection_2', description='description_2')

        self.kit_1 = prototypes.KitPrototype.create(collection=self.collection_1, caption='kit_1', description='description_1')
        self.kit_2 = prototypes.KitPrototype.create(collection=self.collection_1, caption='kit_2', description='description_2')

        self.item_1_1 = prototypes.ItemPrototype.create(kit=self.kit_1, caption='item_1_1', text='text_1_1')
        self.item_1_2 = prototypes.ItemPrototype.create(kit=self.kit_1, caption='item_1_2', text='text_1_2')


class ItemsNewTests(BaseRequestTests):

    def setUp(self):
        super(ItemsNewTests, self).setUp()
        self.test_url = dext_urls.url('collections:items:new')

    def test_login_required(self):
        self.check_redirect(self.test_url, accounts_logic.login_page_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('collections.items.no_edit_rights', 1)])

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('collections.items.no_edit_rights', 0)])


class ItemsCreateTests(BaseRequestTests):

    def setUp(self):
        super(ItemsCreateTests, self).setUp()
        self.test_url = dext_urls.url('collections:items:create')

    def get_post_data(self):
        return {'kit': self.kit_1.id,
                'caption': 'caption_3',
                'text': 'text_3'}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'common.login_required')
        self.assertEqual(prototypes.ItemPrototype._db_all().count(), 2)

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'collections.items.no_edit_rights')
        self.assertEqual(prototypes.ItemPrototype._db_all().count(), 2)

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, {}),
                              'collections.items.create.form_errors')
        self.assertEqual(prototypes.ItemPrototype._db_all().count(), 2)

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()), {'next_url': dext_urls.url('collections:collections:show', self.kit_1.collection_id)})
        self.assertEqual(prototypes.ItemPrototype._db_all().count(), 3)

        item = prototypes.ItemPrototype._db_get_object(2)

        self.assertFalse(item.approved)
        self.assertEqual(item.kit_id, self.kit_1.id)
        self.assertEqual(item.caption, 'caption_3')
        self.assertEqual(item.text, 'text_3')


class ItemsEditTests(BaseRequestTests):

    def setUp(self):
        super(ItemsEditTests, self).setUp()
        self.test_url = dext_urls.url('collections:items:edit', self.item_1_1.id)

    def test_login_required(self):
        self.check_redirect(self.test_url, accounts_logic.login_page_url(self.test_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=(('collections.items.no_edit_rights', 1)))

    def test_moderate_rights_required(self):
        prototypes.ItemPrototype._db_all().update(approved=True)
        storage.items.refresh()

        self.request_login(self.account_2.email)

        self.check_html_ok(self.request_html(self.test_url),
                           texts=[('collections.items.no_edit_rights', 1)])

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.kit_1.caption,
                                  self.item_1_1.caption,
                                  self.item_1_1.text])

    def test_success__for_moderate(self):
        prototypes.KitPrototype._db_all().update(approved=True)
        storage.kits.refresh()

        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.test_url),
                           texts=[self.kit_1.caption,
                                  self.item_1_1.caption,
                                  self.item_1_1.text])


class ItemsUpdateTests(BaseRequestTests):

    def setUp(self):
        super(ItemsUpdateTests, self).setUp()
        self.test_url = dext_urls.url('collections:items:update', self.item_1_1.id)

    def get_post_data(self):
        return {'caption': 'caption_edited',
                'text': 'text_edited',
                'kit': self.kit_2.id}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()), 'common.login_required')

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'collections.items.no_edit_rights')

        self.item_1_1.reload()
        self.assertEqual(self.item_1_1.caption, 'item_1_1')
        self.assertEqual(self.item_1_1.text, 'text_1_1')
        self.assertEqual(self.item_1_1.kit_id, self.kit_1.id)

    def test_moderate_rights_required(self):
        prototypes.ItemPrototype._db_all().update(approved=True)
        storage.items.refresh()

        self.request_login(self.account_2.email)

        self.check_ajax_error(self.post_ajax_json(self.test_url, self.get_post_data()),
                              'collections.items.no_edit_rights')

        self.item_1_1.reload()
        self.assertEqual(self.item_1_1.caption, 'item_1_1')
        self.assertEqual(self.item_1_1.text, 'text_1_1')
        self.assertEqual(self.item_1_1.kit_id, self.kit_1.id)

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url, {}),
                              'collections.items.update.form_errors')

        self.item_1_1.reload()
        self.assertEqual(self.item_1_1.caption, 'item_1_1')
        self.assertEqual(self.item_1_1.text, 'text_1_1')
        self.assertEqual(self.item_1_1.kit_id, self.kit_1.id)

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()))

        self.item_1_1.reload()
        self.assertEqual(self.item_1_1.caption, 'caption_edited')
        self.assertEqual(self.item_1_1.text, 'text_edited')
        self.assertEqual(self.item_1_1.kit_id, self.kit_2.id)

    def test_success__for_moderate(self):
        prototypes.ItemPrototype._db_all().update(approved=True)
        storage.items.refresh()

        self.request_login(self.account_3.email)
        self.check_ajax_ok(self.post_ajax_json(self.test_url, self.get_post_data()))

        self.item_1_1.reload()
        self.assertEqual(self.item_1_1.caption, 'caption_edited')
        self.assertEqual(self.item_1_1.text, 'text_edited')
        self.assertEqual(self.item_1_1.kit_id, self.kit_2.id)


class ItemsApproveTests(BaseRequestTests):

    def setUp(self):
        super(ItemsApproveTests, self).setUp()
        self.test_url = dext_urls.url('collections:items:approve', self.item_1_1.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url), 'collections.items.no_moderate_rights')

    def test_success(self):
        self.request_login(self.account_3.email)
        self.assertFalse(self.item_1_1.approved)
        self.check_ajax_ok(self.post_ajax_json(self.test_url))
        self.item_1_1.reload()
        self.assertTrue(self.item_1_1.approved)


class ItemsDisapproveTests(BaseRequestTests):

    def setUp(self):
        super(ItemsDisapproveTests, self).setUp()
        self.test_url = dext_urls.url('collections:items:disapprove', self.item_1_1.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.test_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.test_url), 'collections.items.no_moderate_rights')

    def test_success(self):
        prototypes.ItemPrototype._db_all().update(approved=True)
        storage.items.refresh()

        self.item_1_1.reload()

        self.request_login(self.account_3.email)

        self.assertTrue(self.item_1_1.approved)
        self.check_ajax_ok(self.post_ajax_json(self.test_url))
        self.item_1_1.reload()
        self.assertFalse(self.item_1_1.approved)
