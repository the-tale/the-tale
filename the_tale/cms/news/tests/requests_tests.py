# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate as django_authenticate

from common.utils.testcase import TestCase

from accounts.logic import register_user, login_url
from game.logic import create_test_map

from cms.news.models import News
from cms.news.conf import news_settings

from forum.models import Category, SubCategory, Thread

class TestRequests(TestCase):

    def setUp(self):
        super(TestRequests, self).setUp()
        self.client = client.Client()

        self.news1 = News.objects.create(caption='news1-caption', description='news1-description', content='news1-content')
        self.news2 = News.objects.create(caption='news2-caption', description='news2-description', content='news2-content')
        self.news3 = News.objects.create(caption='news3-caption', description='news3-description', content='news3-content')

    def test_index_page(self):
        texts = []

        for i in xrange(1, 4):
            texts.extend([('news%d-caption' %i, 1),
                          ('news%d-description' %i, 1),
                          ('news%d-content' %i, 0)])

        self.check_html_ok(self.client.get(reverse('news:')), texts=texts)

    def create_news(self, index):
        return News.objects.create(caption='caption-%d' % index, description='description-%d' % index, content='content-%d' % index)

    def test_second_page(self):
        for i in xrange(news_settings.NEWS_ON_PAGE):
            self.create_news(i)

        first_page_texts = []

        for i in xrange(news_settings.NEWS_ON_PAGE):
            first_page_texts.extend([('caption-%d' % i, 1), ('description-%d' % i, 1)])

        self.check_html_ok(self.client.get(reverse('news:')+'?page=1'), texts=first_page_texts)

        self.check_html_ok(self.client.get(reverse('news:')+'?page=2'), texts=[('news1-caption', 1), ('news1-description', 1),
                                                                               ('news2-caption', 1), ('news2-description', 1),
                                                                               ('news3-caption', 1), ('news3-description', 1) ])

    def test_big_page_number(self):
        self.check_redirect(reverse('news:')+'?page=666', reverse('news:')+'?page=1')

    def test_feed_page(self):
        texts = []

        for i in xrange(1, 4):
            texts.extend([('news%d-caption' %i, 1),
                          ('news%d-description' %i, 0),
                          ('news%d-content' %i, 1)])

        self.check_html_ok(self.client.get(reverse('news:feed')), texts=texts, content_type='application/atom+xml')


    def test_show_page(self):
        self.check_html_ok(self.client.get(reverse('news:show', args=[self.news1.id])), texts=(('news1-caption', 3), # third caption in addthis widget
                                                                                               ('news1-description', 1), # description in addthis widget
                                                                                               ('news1-content', 1)))

    def prepair_forum(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')

        self.user = django_authenticate(username='test_user', password='111111')
        self.user.is_staff = True
        self.user.save()

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=news_settings.FORUM_CATEGORY_SLUG,
                                   slug=news_settings.FORUM_CATEGORY_SLUG,
                                   category=forum_category)

        self.assertEqual(Thread.objects.all().count(), 0)


    def test_post_on_forum_success(self):
        self.prepair_forum()
        self.request_login('test_user@test.com')

        response = self.client.get(reverse('news:publish-on-forum', args=[self.news1.id]))

        self.assertEqual(Thread.objects.all().count(), 1)

        thread = Thread.objects.all()[0]

        self.assertRedirects(response, reverse('forum:threads:show', args=[thread.id]), status_code=302, target_status_code=200)

        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[thread.id])), texts=(('news1-caption', 3),
                                                                                                    ('news1-description', 0),
                                                                                                    ('news1-content', 1)))

        self.check_html_ok(self.client.get(reverse('news:show', args=[self.news1.id])), texts=(('pgf-forum-link', 1), ))
        self.check_html_ok(self.client.get(reverse('news:')), texts=(('pgf-forum-link', 1), ))

    def test_post_on_forum_unloggined(self):
        self.prepair_forum()

        self.check_redirect(reverse('news:publish-on-forum', args=[self.news1.id]), login_url(reverse('news:publish-on-forum', args=[self.news1.id])))

        self.assertEqual(Thread.objects.all().count(), 0)

        self.check_html_ok(self.client.get(reverse('news:show', args=[self.news1.id])), texts=(('pgf-forum-link', 0), ))
        self.check_html_ok(self.client.get(reverse('news:')), texts=(('pgf-forum-link', 0), ))


    def test_post_on_forum_unexisting_category(self):
        self.prepair_forum()
        self.request_login('test_user@test.com')

        SubCategory.objects.all().delete()

        self.check_ajax_error(self.client.get(reverse('news:publish-on-forum', args=[self.news1.id])),
                              'news.publish_on_forum.forum_category_not_exists')

        self.assertEqual(Thread.objects.all().count(), 0)

        self.check_html_ok(self.client.get(reverse('news:show', args=[self.news1.id])), texts=(('pgf-forum-link', 0), ))
        self.check_html_ok(self.client.get(reverse('news:')), texts=(('pgf-forum-link', 0), ))

    def test_post_on_forum_already_publish(self):
        self.prepair_forum()
        self.request_login('test_user@test.com')
        self.client.get(reverse('news:publish-on-forum', args=[self.news1.id]))

        self.check_ajax_error(self.client.get(reverse('news:publish-on-forum', args=[self.news1.id])),
                              'news.publish_on_forum.forum_thread_already_exists')
