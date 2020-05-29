
import smart_imports

smart_imports.all()


class SubcategoryPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(SubcategoryPrototypeTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_subcategories_visible_to_account_with_permissions(self):
        granted_account = self.accounts_factory.create_account()
        wrong_account = self.accounts_factory.create_account()

        category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        subcategory_1 = prototypes.SubCategoryPrototype.create(category=category, caption='subcat-1-caption', order=2)

        prototypes.SubCategoryPrototype.create(category=category, caption='subcat-2-caption', order=1, restricted=True)

        restricted_subcategory = prototypes.SubCategoryPrototype.create(category=category, caption='subcat-restricted-caption', order=0, restricted=True)

        prototypes.PermissionPrototype.create(granted_account, restricted_subcategory)

        self.assertEqual([s.id for s in prototypes.SubCategoryPrototype.subcategories_visible_to_account(account=None)],
                         [subcategory_1.id])

        self.assertEqual([s.id for s in prototypes.SubCategoryPrototype.subcategories_visible_to_account(account=granted_account)],
                         [restricted_subcategory.id, subcategory_1.id])

        self.assertEqual([s.id for s in prototypes.SubCategoryPrototype.subcategories_visible_to_account(account=wrong_account)],
                         [subcategory_1.id])

    def test_delete(self):
        category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)

        subcategory_1 = prototypes.SubCategoryPrototype.create(category=category, caption='subcat-1-caption', order=2)
        subcategory_2 = prototypes.SubCategoryPrototype.create(category=category, caption='subcat-2-caption', order=1)

        thread_1_1 = prototypes.ThreadPrototype.create(subcategory_1, 'thread-1_1-caption', self.account, 'thread-1_1-text')
        thread_1_2 = prototypes.ThreadPrototype.create(subcategory_1, 'thread-1_2-caption', self.account, 'thread-1_2-text')
        thread_2_1 = prototypes.ThreadPrototype.create(subcategory_2, 'thread-2_1-caption', self.account, 'thread-2_1-text')

        subcategory_1.delete()

        self.assertFalse(prototypes.ThreadPrototype._db_filter(id__in=(thread_1_1.id, thread_1_2.id)).exists())
        self.assertTrue(prototypes.ThreadPrototype._db_filter(id=thread_2_1.id).exists())

        self.assertFalse(prototypes.SubCategoryPrototype._db_filter(id=subcategory_1.id).exists())
        self.assertTrue(prototypes.SubCategoryPrototype._db_filter(id=subcategory_2.id).exists())


class SubcategoryPrototypeUpdateTests(utils_testcase.TestCase):

    def setUp(self):
        super(SubcategoryPrototypeUpdateTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.checked_account = self.accounts_factory.create_account()

        self.category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=2)

        self.thread_1 = prototypes.ThreadPrototype.create(self.subcategory, 'thread-1-caption', self.account, 'thread-1-text')
        self.thread_2 = prototypes.ThreadPrototype.create(self.subcategory, 'thread-2-caption', self.account, 'thread-2-text')

    def test_automatic_update_on_post_creating(self):

        old_time = datetime.datetime.now()

        prototypes.PostPrototype.create(thread=self.thread_2, author=self.checked_account, text='post-1-text')

        self.subcategory.reload()

        self.assertEqual(self.subcategory.threads_count, 2)
        self.assertEqual(self.subcategory.posts_count, 1)
        self.assertEqual(self.subcategory.last_poster.id, self.checked_account.id)
        self.assertEqual(self.subcategory.last_thread.id, self.thread_2.id)
        self.assertTrue(self.subcategory.updated_at > old_time)
        self.assertEqual(self.subcategory.last_thread_created_at, self.thread_2.created_at)

    def test_automatic_raw_update(self):
        old_time = datetime.datetime.now()

        prototypes.PostPrototype._model_class.objects.create(thread=self.thread_1._model,
                                                             author=self.checked_account._model,
                                                             markup_method=relations.MARKUP_METHOD.MARKDOWN,
                                                             technical=False,
                                                             text='post-2-text',
                                                             state=relations.POST_STATE.DEFAULT)

        self.subcategory.reload()

        self.assertEqual(self.subcategory.posts_count, 0)
        self.assertEqual(self.subcategory.last_poster.id, self.account.id)
        self.assertEqual(self.subcategory.last_thread.id, self.thread_2.id)
        self.assertTrue(self.subcategory.updated_at < old_time)

        self.subcategory.update()
        self.subcategory.reload()

        self.assertEqual(self.subcategory.posts_count, 1)
        self.assertEqual(self.subcategory._model.last_poster_id, self.checked_account.id)
        self.assertEqual(self.subcategory._model.last_thread_id, self.thread_1.id)
        self.assertTrue(old_time < self.subcategory.updated_at)

    def test_automatic_update_on_post_deleting(self):

        old_time = datetime.datetime.now()

        self.test_automatic_update_on_post_creating()

        prototypes.PostPrototype._db_get_object(2).delete(self.checked_account)

        self.subcategory.update()

        self.assertEqual(self.subcategory.posts_count, 1)
        self.assertEqual(self.subcategory._model.last_poster.id, self.account.id)
        self.assertEqual(self.subcategory._model.last_thread.id, self.thread_2.id)
        self.assertTrue(self.subcategory.updated_at < old_time)

        prototypes.PostPrototype._db_get_object(1).delete(self.checked_account)

        self.subcategory.update()

        self.assertEqual(self.subcategory.posts_count, 1)
        self.assertEqual(self.subcategory._model.last_poster.id, self.account.id)
        self.assertEqual(self.subcategory._model.last_thread.id, self.thread_1.id)
        self.assertTrue(self.subcategory.updated_at < old_time)


class ThreadPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(ThreadPrototypeTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=0)

        self.thread = prototypes.ThreadPrototype.create(self.subcategory, 'thread-caption', self.account, 'thread-text')

    def test_get_new_thread_delay__no_threads__new_account(self):
        new_account = self.accounts_factory.create_account()
        self.assertTrue(prototypes.ThreadPrototype.get_new_thread_delay(new_account) > 0)

    def test_get_new_thread_delay__no_threads__old_account(self):
        new_account = self.accounts_factory.create_account()
        new_account._model.created_at = datetime.datetime.now() - datetime.timedelta(days=30)
        self.assertFalse(prototypes.ThreadPrototype.get_new_thread_delay(new_account), 0)

    def test_get_new_thread_delay__has_old_thread(self):
        prototypes.ThreadPrototype._db_all().update(created_at=datetime.datetime.now() - datetime.timedelta(days=30))
        self.assertEqual(prototypes.ThreadPrototype.get_new_thread_delay(self.account), 0)

    def test_get_new_thread_delay__has_new_thread(self):
        self.assertTrue(prototypes.ThreadPrototype.get_new_thread_delay(self.account) > 0)

    def test_last_forum_posts_with_permissions(self):
        granted_account = self.accounts_factory.create_account()
        wrong_account = self.accounts_factory.create_account()

        restricted_subcategory = prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat2-caption', order=1, restricted=True)

        prototypes.PermissionPrototype.create(granted_account, restricted_subcategory)

        restricted_thread = prototypes.ThreadPrototype.create(restricted_subcategory, 'thread-restricted-caption', self.account, 'thread-text')

        self.assertEqual(set(t.id for t in prototypes.ThreadPrototype.get_last_threads(account=None, limit=3)),
                         set([self.thread.id]))

        self.assertEqual(set(t.id for t in prototypes.ThreadPrototype.get_last_threads(account=granted_account, limit=3)),
                         set([self.thread.id, restricted_thread.id]))

        self.assertEqual(set(t.id for t in prototypes.ThreadPrototype.get_last_threads(account=wrong_account, limit=3)),
                         set([self.thread.id]))

    def test_update_subcategory_on_delete(self):
        with mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.update') as subcategory_update:
            self.thread.delete()

        self.assertEqual(subcategory_update.call_count, 1)

    def test_update_subcategory_on_create(self):
        with mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.update') as subcategory_update:
            prototypes.ThreadPrototype.create(self.subcategory, 'thread-2-caption', self.account, 'thread-2-text')

        self.assertEqual(subcategory_update.call_count, 1)

    def test_post_created_at_turn(self):
        game_turn.increment(2)

        prototypes.ThreadPrototype.create(self.subcategory, 'thread-2-caption', self.account, 'thread-2-text')

        self.assertEqual(prototypes.PostPrototype._db_latest().created_at_turn, game_turn.number())


class ThreadPrototypeUpdateTests(utils_testcase.TestCase):

    def setUp(self):
        super(ThreadPrototypeUpdateTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.checked_account = self.accounts_factory.create_account()

        self.category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=2)

        self.thread = prototypes.ThreadPrototype.create(self.subcategory, 'thread-caption', self.account, 'thread-text')

    def test_automatic_update_on_post_creating(self):

        old_time = datetime.datetime.now()

        prototypes.PostPrototype.create(thread=self.thread, author=self.checked_account, text='post-1-text')

        self.thread.reload()

        self.assertEqual(self.thread.posts_count, 1)
        self.assertEqual(self.thread.last_poster.id, self.checked_account.id)
        self.assertTrue(self.thread.updated_at > old_time)

    def test_automatic_raw_update(self):

        old_time = datetime.datetime.now()

        prototypes.PostPrototype._model_class.objects.create(thread=self.thread._model,
                                                             author=self.checked_account._model,
                                                             markup_method=relations.MARKUP_METHOD.MARKDOWN,
                                                             technical=False,
                                                             text='post-2-text',
                                                             state=relations.POST_STATE.DEFAULT)

        self.thread.reload()

        self.assertEqual(self.thread.posts_count, 0)
        self.assertEqual(self.thread.last_poster.id, self.account.id)
        self.assertTrue(self.thread.updated_at < old_time)

        self.thread.update()
        self.thread.reload()

        self.assertEqual(self.thread.posts_count, 1)
        self.assertEqual(self.thread._model.last_poster.id, self.checked_account.id)
        self.assertTrue(old_time < self.thread.updated_at)

    def test_automatic_update_on_post_deleting(self):

        old_time = datetime.datetime.now()

        self.test_automatic_update_on_post_creating()

        prototypes.PostPrototype._db_get_object(1).delete(self.checked_account)

        self.thread.update()

        self.assertEqual(self.thread.posts_count, 1)
        self.assertEqual(self.thread._model.last_poster.id, self.account.id)
        self.assertTrue(self.thread.updated_at < old_time)

    def test_subcategory_updated(self):
        with mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.update') as subcategory_update:
            self.thread.update()

        self.assertEqual(subcategory_update.call_count, 1)

    def test_2_subcategories_updated(self):
        subcategory_2 = prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat-2-caption', order=3)

        with mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.update') as subcategory_update:
            self.thread.update(new_subcategory_id=subcategory_2.id)

        self.assertEqual(subcategory_update.call_count, 2)


class PostPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(PostPrototypeTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.checked_account = self.accounts_factory.create_account()

        self.category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=2)

        self.thread = prototypes.ThreadPrototype.create(self.subcategory, 'thread-caption', self.account, 'thread-text')

    def test_get_new_post_delay__no_posts__new_account(self):
        new_account = self.accounts_factory.create_account()
        self.assertTrue(prototypes.PostPrototype.get_new_post_delay(new_account) > 0)

    def test_get_new_post_delay__no_posts__old_account(self):
        new_account = self.accounts_factory.create_account()
        new_account._model.created_at = datetime.datetime.now() - datetime.timedelta(days=30)
        self.assertFalse(prototypes.PostPrototype.get_new_post_delay(new_account), 0)

    def test_get_new_post_delay__has_old_post(self):
        prototypes.PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')
        prototypes.PostPrototype._db_all().update(created_at=datetime.datetime.now() - datetime.timedelta(days=30))
        self.assertEqual(prototypes.PostPrototype.get_new_post_delay(self.account), 0)

    def test_get_new_post_delay__has_new_post(self):
        prototypes.PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')
        self.assertTrue(prototypes.PostPrototype.get_new_post_delay(self.account) > 0)

    def test_get_new_post_delay__more_then_one_post(self):
        prototypes.PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')
        delay_1 = prototypes.PostPrototype.get_new_post_delay(self.account)

        prototypes.PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')

        delay_2 = prototypes.PostPrototype.get_new_post_delay(self.account)

        self.assertTrue(delay_1 - delay_2 > 1)

    def test_get_new_post_delay__a_lot_of_posts(self):
        for i in range(100):
            prototypes.PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')

        self.assertTrue(prototypes.PostPrototype.get_new_post_delay(self.account) < conf.settings.POST_DELAY)

    def test_update_thread_on_delete(self):
        with mock.patch('the_tale.forum.prototypes.ThreadPrototype.update') as thread_update:
            prototypes.PostPrototype._db_get_object(0).delete(self.checked_account)

        self.assertEqual(thread_update.call_count, 1)

    def test_reset_text_on_delete(self):
        post = prototypes.PostPrototype._db_get_object(0)

        self.assertNotEqual(post.text, '')

        post.delete(self.checked_account)

        post.reload()

        self.assertEqual(post.text, '')

    def test_created_at_turn(self):
        game_turn.increment()
        game_turn.increment()

        post = prototypes.PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')

        self.assertEqual(post.created_at_turn, game_turn.number())

    def test_update_thread_on_create(self):
        with mock.patch('the_tale.forum.prototypes.ThreadPrototype.update') as thread_update:
            prototypes.PostPrototype.create(thread=self.thread, author=self.checked_account, text='post-1-text')

        self.assertEqual(thread_update.call_count, 1)


class ThreadReadInfoPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(ThreadReadInfoPrototypeTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        subcategory = prototypes.SubCategoryPrototype.create(category=category, caption='subcat-caption', order=0)

        self.thread = prototypes.ThreadPrototype.create(subcategory, 'thread1-caption', self.account, 'thread-text')

    def test_remove_old_infos(self):
        read_info_1 = prototypes.ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        read_info_2 = prototypes.ThreadReadInfoPrototype.read_thread(self.thread, self.account_2)

        removed_time = datetime.datetime.now() - datetime.timedelta(seconds=conf.settings.UNREAD_STATE_EXPIRE_TIME)
        prototypes.ThreadReadInfoPrototype._model_class.objects.filter(id=read_info_2.id).update(read_at=removed_time)

        self.assertEqual(prototypes.ThreadReadInfoPrototype._db_count(), 2)
        prototypes.ThreadReadInfoPrototype.remove_old_infos()
        self.assertEqual(prototypes.ThreadReadInfoPrototype._db_count(), 1)
        self.assertEqual(prototypes.ThreadReadInfoPrototype._db_get_object(0).id, read_info_1.id)

    def test_read_thread__unexisted_info(self):
        self.assertEqual(prototypes.ThreadReadInfoPrototype._db_count(), 0)
        read_info = prototypes.ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        self.assertEqual(prototypes.ThreadReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.thread_id, self.thread.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))

    def test_read_thread__existed_info(self):
        self.assertEqual(prototypes.ThreadReadInfoPrototype._db_count(), 0)
        read_info = prototypes.ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        read_info_2 = prototypes.ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        self.assertEqual(read_info.id, read_info_2.id)
        self.assertEqual(prototypes.ThreadReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.thread_id, self.thread.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))


class SubCategoryReadInfoPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(SubCategoryReadInfoPrototypeTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = prototypes.SubCategoryPrototype.create(category=category, caption='subcat-caption', order=0)

    def test_is_restricted_for__not_restricted(self):
        self.subcategory._model.restricted = False
        self.subcategory.save()
        self.assertFalse(self.subcategory.is_restricted_for(self.account))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: False)
    def test_is_restricted_for__not_authenticated(self):
        self.subcategory._model.restricted = True
        self.subcategory.save()
        self.assertTrue(self.subcategory.is_restricted_for(self.account))

    def test_is_restricted_for__has_permission(self):
        self.subcategory._model.restricted = True
        self.subcategory.save()
        prototypes.PermissionPrototype.create(self.account, self.subcategory)
        self.assertFalse(self.subcategory.is_restricted_for(self.account))

    def test_is_restricted_for__no_permission(self):
        self.subcategory._model.restricted = True
        self.subcategory.save()
        prototypes.PermissionPrototype.create(self.account_2, self.subcategory)
        self.assertTrue(self.subcategory.is_restricted_for(self.account))

    def test_create_when_created(self):
        read_info_1 = prototypes.SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        read_info_2 = prototypes.SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)

        self.assertEqual(read_info_1.id, read_info_2.id)

    def test_remove_old_infos(self):
        read_info_1 = prototypes.SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        read_info_2 = prototypes.SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account_2)

        removed_time = datetime.datetime.now() - datetime.timedelta(seconds=conf.settings.UNREAD_STATE_EXPIRE_TIME)
        prototypes.SubCategoryReadInfoPrototype._model_class.objects.filter(id=read_info_2.id).update(read_at=removed_time)

        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 2)
        prototypes.SubCategoryReadInfoPrototype.remove_old_infos()
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_get_object(0).id, read_info_1.id)

    def test_read_subcategory__unexisted_info(self):
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 0)
        read_info = prototypes.SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.subcategory_id, self.subcategory.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertTrue(read_info.all_read_at < datetime.datetime.now() - datetime.timedelta(seconds=1))

    def test_read_subcategory__existed_info(self):
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 0)
        read_info = prototypes.SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        read_info_2 = prototypes.SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        self.assertEqual(read_info.id, read_info_2.id)
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.subcategory_id, self.subcategory.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info_2.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertTrue(read_info_2.all_read_at < datetime.datetime.now() - datetime.timedelta(seconds=1))

    def test_read_all_in_subcategory__unexisted_info(self):
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 0)
        read_info = prototypes.SubCategoryReadInfoPrototype.read_all_in_subcategory(self.subcategory, self.account)
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.subcategory_id, self.subcategory.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertTrue(read_info.all_read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))

    def test_read_all_in_subcategory__existed_info(self):
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 0)
        read_info = prototypes.SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        read_info_2 = prototypes.SubCategoryReadInfoPrototype.read_all_in_subcategory(self.subcategory, self.account)
        self.assertEqual(read_info.id, read_info_2.id)
        self.assertEqual(prototypes.SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.subcategory_id, self.subcategory.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info_2.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertTrue(read_info_2.all_read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))


class SubscriptionPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(SubscriptionPrototypeTests, self).setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory_1 = prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat-1-caption', order=0)
        self.subcategory_2 = prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat-2-caption', order=1)

        self.thread_1_1 = prototypes.ThreadPrototype.create(self.subcategory_1, 'thread-1-1-caption', self.account, 'thread-1-1-text')
        self.thread_1_2 = prototypes.ThreadPrototype.create(self.subcategory_1, 'thread-1-2-caption', self.account, 'thread-1-2-text')
        self.thread_1_3 = prototypes.ThreadPrototype.create(self.subcategory_1, 'thread-1-3-caption', self.account_2, 'thread-1-3-text')
        self.thread_2_1 = prototypes.ThreadPrototype.create(self.subcategory_2, 'thread-2-1-caption', self.account, 'thread-2-1-text')
        self.thread_2_2 = prototypes.ThreadPrototype.create(self.subcategory_2, 'thread-2-2-caption', self.account, 'thread-2-2-text')

    def test_remove_all_in_subcategory(self):

        prototypes.SubscriptionPrototype.create(account=self.account, subcategory=self.subcategory_1)
        subscr_2 = prototypes.SubscriptionPrototype.create(account=self.account, subcategory=self.subcategory_2)

        prototypes.SubscriptionPrototype.create(account=self.account, thread=self.thread_1_1)
        prototypes.SubscriptionPrototype.create(account=self.account, thread=self.thread_1_2)
        subscr_5 = prototypes.SubscriptionPrototype.create(account=self.account_2, thread=self.thread_1_2)
        subscr_6 = prototypes.SubscriptionPrototype.create(account=self.account_2, thread=self.thread_1_3)

        subscr_7 = prototypes.SubscriptionPrototype.create(account=self.account, thread=self.thread_2_1)

        self.assertEqual(prototypes.SubscriptionPrototype._db_count(), 7)

        prototypes.SubscriptionPrototype.remove_all_in_subcategory(account_id=self.account.id, subcategory_id=self.subcategory_1.id)

        self.assertEqual(prototypes.SubscriptionPrototype._db_count(), 4)
        self.assertEqual(set(s.id for s in prototypes.SubscriptionPrototype._db_all()),
                         set((subscr_2.id, subscr_5.id, subscr_6.id, subscr_7.id)))


class PermissionPrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(PermissionPrototypeTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.category = prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=0)

    def test_remove(self):
        permission = prototypes.PermissionPrototype.create(self.account, self.subcategory)

        with mock.patch('the_tale.forum.prototypes.SubscriptionPrototype.remove_all_in_subcategory') as remove_all_in_subcategory:
            permission.remove()

        self.assertEqual(remove_all_in_subcategory.call_count, 1)
        self.assertEqual(remove_all_in_subcategory.call_args, mock.call(account_id=self.account.id, subcategory_id=self.subcategory.id))
