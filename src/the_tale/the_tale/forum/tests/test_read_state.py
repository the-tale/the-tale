
import smart_imports

smart_imports.all()


class ReadStateTests(utils_testcase.TestCase):

    def setUp(self):
        super(ReadStateTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = prototypes.SubCategoryPrototype.create(category=category, caption='subcat-caption', order=0)
        self.subcategory_2 = prototypes.SubCategoryPrototype.create(category=category, caption='subcat-2-caption', order=0)

        self.thread = prototypes.ThreadPrototype.create(self.subcategory, 'thread1-caption', self.account_2, 'thread-text')
        self.thread_2 = prototypes.ThreadPrototype.create(self.subcategory, 'thread2-caption', self.account_2, 'thread-2-text')
        self.thread_3 = prototypes.ThreadPrototype.create(self.subcategory_2, 'thread2-caption', self.account, 'thread-2-text')

    def get_read_state(self, account=None):
        return read_state.ReadState(self.account if account is None else account)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', False)
    def test_thread_has_new_messages__unauthenticated(self):
        read_state = self.get_read_state()
        self.assertFalse(read_state.thread_has_new_messages(self.thread))

    def test_thread_has_new_messages__never_read(self):
        read_state = self.get_read_state()
        self.assertTrue(read_state.thread_has_new_messages(self.thread))
        self.account._model.created_at = datetime.datetime.now()
        self.account.save()
        self.assertFalse(read_state.thread_has_new_messages(self.thread))

    def test_thread_has_new_messages__read(self):
        prototypes.ThreadReadInfoPrototype.read_thread(self.thread, self.account)

        read_state = self.get_read_state()

        self.assertFalse(read_state.thread_has_new_messages(self.thread))

        self.thread._model.updated_at = datetime.datetime.now()
        self.thread.save()

        self.assertTrue(read_state.thread_has_new_messages(self.thread))

    @mock.patch('the_tale.forum.conf.settings.UNREAD_STATE_EXPIRE_TIME', 0)
    def test_thread_has_new_messages__unread_state_expired(self):
        read_state = self.get_read_state()
        self.assertFalse(read_state.thread_has_new_messages(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', False)
    def test_thread_is_new__unauthenticated(self):
        read_state = self.get_read_state()
        self.assertFalse(read_state.thread_is_new(self.thread))

    def test_thread_is_new__author(self):
        read_state = self.get_read_state(account=self.account_2)
        self.assertFalse(read_state.thread_is_new(self.thread))

    def test_thread_is_new__never_read(self):
        read_state = self.get_read_state()
        self.assertTrue(read_state.thread_is_new(self.thread))
        self.account._model.created_at = datetime.datetime.now()
        self.account.save()
        self.assertFalse(read_state.thread_is_new(self.thread))

    def test_thread_is_new__read(self):
        prototypes.SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)

        read_state = self.get_read_state()

        self.assertFalse(read_state.thread_is_new(self.thread))

        self.thread._model.created_at = datetime.datetime.now()
        self.thread.save()

        self.assertTrue(read_state.thread_is_new(self.thread))

    @mock.patch('the_tale.forum.conf.settings.UNREAD_STATE_EXPIRE_TIME', 0)
    def test_thread_is_new__unread_state_expired(self):
        read_state = self.get_read_state()
        self.assertFalse(read_state.thread_is_new(self.thread))

    def test_thread_has_new_messages__category_read(self):
        read_state = self.get_read_state()
        self.assertTrue(read_state.thread_is_new(self.thread))

        prototypes.SubCategoryReadInfoPrototype.read_all_in_subcategory(self.subcategory, self.account)
        read_state = self.get_read_state()

        self.assertFalse(read_state.thread_has_new_messages(self.thread))

    def test_thread_is_new_messages__thread_read(self):
        read_state = self.get_read_state()
        self.assertTrue(read_state.thread_is_new(self.thread))

        prototypes.ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        read_state = self.get_read_state()

        self.assertFalse(read_state.thread_is_new(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', False)
    def test_subcategory_has_new_messages__unauthenticated(self):
        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    def test_subcategory_has_new_messages__not_read(self):
        self.assertTrue(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    def test_subcategory_has_new_messages__read(self):
        prototypes.SubCategoryReadInfoPrototype.read_subcategory(subcategory=self.subcategory, account=self.account)
        self.assertTrue(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    def test_subcategory_has_new_messages__read_all(self):
        prototypes.SubCategoryReadInfoPrototype.read_all_in_subcategory(subcategory=self.subcategory, account=self.account)
        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    @mock.patch('the_tale.forum.conf.settings.UNREAD_STATE_EXPIRE_TIME', 0)
    def test_subcategory_has_new_messages__unread_state_expired(self):
        prototypes.SubCategoryReadInfoPrototype.read_subcategory(subcategory=self.subcategory, account=self.account)
        self.subcategory._model.updated_at = datetime.datetime.now()
        self.subcategory.save()

        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    def test_subcategory_has_new_messages__new_thread(self):
        prototypes.SubCategoryReadInfoPrototype.read_all_in_subcategory(subcategory=self.subcategory, account=self.account)
        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))
        prototypes.ThreadPrototype.create(self.subcategory, 'new-threwad', self.account_2, 'thread-new-text')
        self.assertTrue(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    def test_subcategory_has_new_messages__new_post(self):
        prototypes.SubCategoryReadInfoPrototype.read_all_in_subcategory(subcategory=self.subcategory, account=self.account)
        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))
        prototypes.PostPrototype.create(self.thread, self.account_2, 'post-new-text')
        self.assertTrue(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    @mock.patch('the_tale.forum.conf.settings.POST_DELAY', 0)
    @mock.patch('the_tale.forum.conf.settings.FIRST_POST_DELAY', 0)
    def test_subcategory_has_new_messages__new_post_from_request(self):
        prototypes.SubCategoryReadInfoPrototype.read_all_in_subcategory(subcategory=self.subcategory, account=self.account)
        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))

        self.request_login(self.account_2.email)
        self.client.post(utils_urls.url('forum:threads:create-post', self.thread.id), {'text': 'thread3-test-post'})

        self.assertTrue(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    def test_subcategory_has_new_messages__new_post_from_request_from_read_account(self):
        prototypes.SubCategoryReadInfoPrototype.read_all_in_subcategory(subcategory=self.subcategory, account=self.account)
        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))

        self.request_login(self.account.email)
        self.client.post(utils_urls.url('forum:threads:create-post', self.thread.id), {'text': 'thread3-test-post'})

        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    def test_subcategory_has_new_messages__unread_but_thread_read(self):
        prototypes.SubCategoryReadInfoPrototype.read_subcategory(subcategory=self.subcategory, account=self.account)
        self.subcategory._model.updated_at = datetime.datetime.now()
        self.subcategory.save()
        self.assertTrue(self.get_read_state().subcategory_has_new_messages(self.subcategory))
        prototypes.ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        prototypes.ThreadReadInfoPrototype.read_thread(self.thread_2, self.account)
        prototypes.ThreadReadInfoPrototype.read_thread(self.thread_3, self.account)
        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))

    @mock.patch('the_tale.forum.conf.settings.UNREAD_STATE_EXPIRE_TIME', 0)
    def test_subcategory_expired__no_read_info(self):
        prototypes.SubCategoryReadInfoPrototype._db_all().delete()
        self.assertFalse(self.get_read_state().subcategory_has_new_messages(self.subcategory))
