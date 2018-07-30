
import smart_imports

smart_imports.all()


class NewForumThreadTests(utils_testcase.TestCase):

    def setUp(self):
        super(NewForumThreadTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.category = forum_prototypes.CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = forum_prototypes.SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=0)
        self.thread = forum_prototypes.ThreadPrototype.create(self.subcategory, 'thread_1-caption', self.account_1, 'thread-text')

        self.message = prototypes.MessagePrototype.get_priority_message()

    def test_register_message(self):
        self.assertEqual(models.Message.objects.all().count(), 1)

    def test_no_subscriptions(self):
        self.assertEqual(len(django_mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 0)

    def test_one_subscription(self):
        forum_prototypes.SubscriptionPrototype.create(self.account_1, subcategory=self.subcategory)
        self.assertEqual(len(django_mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 1)
        self.assertEqual(django_mail.outbox[0].to, [self.account_1.email])

        self.assertTrue(self.thread.author.nick in django_mail.outbox[0].body)
        self.assertTrue(self.thread.caption in django_mail.outbox[0].body)
        self.assertTrue(self.thread.paginator.last_page_url in django_mail.outbox[0].body)
        self.assertTrue(self.thread.get_first_post().html in django_mail.outbox[0].body)
        self.assertTrue(django_settings.SITE_URL in django_mail.outbox[0].body)

        self.assertTrue(self.thread.author.nick in django_mail.outbox[0].alternatives[0][0])
        self.assertTrue(self.thread.caption in django_mail.outbox[0].alternatives[0][0])
        self.assertTrue(self.thread.paginator.last_page_url in django_mail.outbox[0].alternatives[0][0])
        self.assertTrue(self.thread.get_first_post().html in django_mail.outbox[0].alternatives[0][0])
        self.assertTrue(django_settings.SITE_URL in django_mail.outbox[0].alternatives[0][0])

    def test_mail_send__to_system_user(self):
        forum_prototypes.SubscriptionPrototype.create(accounts_logic.get_system_user(), subcategory=self.subcategory)
        self.assertEqual(len(django_mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 0)

    def test_many_subscriptions(self):
        account_2 = self.accounts_factory.create_account()

        forum_prototypes.SubscriptionPrototype.create(self.account_1, subcategory=self.subcategory)
        forum_prototypes.SubscriptionPrototype.create(account_2, subcategory=self.subcategory)

        self.assertEqual(len(django_mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(django_mail.outbox), 2)
        self.assertEqual(django_mail.outbox[0].to, [self.account_1.email])
        self.assertEqual(django_mail.outbox[1].to, [account_2.email])
