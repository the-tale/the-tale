# coding: utf-8

import datetime

from dext.common.utils.urls import url

from the_tale.common.utils import testcase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.logic import login_page_url
from the_tale.game.logic import create_test_map

from the_tale.post_service import models as post_service_models
from the_tale.post_service import prototypes as post_service_prototypes

from the_tale.cms.news import models
from the_tale.cms.news import conf
from the_tale.cms.news import logic
from the_tale.cms.news import relations

from the_tale.forum import models as forum_models



class TestRequestsBase(testcase.TestCase):

    def setUp(self):
        super(TestRequestsBase, self).setUp()

        create_test_map()

        forum_category = forum_models.Category.objects.create(caption='category-1', slug='category-1')
        forum_models.SubCategory.objects.create(caption=conf.settings.FORUM_CATEGORY_UID,
                                   uid=conf.settings.FORUM_CATEGORY_UID,
                                   category=forum_category)

        self.assertEqual(forum_models.Thread.objects.all().count(), 0)

        self.user = self.accounts_factory.create_account()
        self.editor = self.accounts_factory.create_account()

        self.news1 = logic.create_news(caption='news1-caption', description='news1-description', content='news1-content')
        self.news2 = logic.create_news(caption='news2-caption', description='news2-description', content='news2-content')
        self.news3 = logic.create_news(caption='news3-caption', description='news3-description', content='news3-content')


        group_edit = sync_group('edit news', ['news.edit_news'])
        group_edit.user_set.add(self.editor._model)

    def create_news(self, index):
        return logic.create_news(caption='caption-%d' % index, description='description-%d' % index, content='content-%d' % index)


class TestIndexRequests(TestRequestsBase):

    def test_index_page(self):
        texts = []

        for i in xrange(1, 4):
            texts.extend(['news%d-caption' %i,
                          'news%d-description' %i,
                          ('news%d-content' %i, 0)])

        self.check_html_ok(self.client.get(url('news:')), texts=texts)

    def test_second_page(self):
        for i in xrange(conf.settings.NEWS_ON_PAGE):
            self.create_news(i)

        first_page_texts = []

        for i in xrange(conf.settings.NEWS_ON_PAGE):
            first_page_texts.extend([('caption-%d' % i, 1), ('description-%d' % i, 1)])

        self.check_html_ok(self.request_html(url('news:', page=1)), texts=first_page_texts)

        self.check_html_ok(self.request_html(url('news:', page=2)), texts=[('news1-caption', 1), ('news1-description', 1),
                                                                           ('news2-caption', 1), ('news2-description', 1),
                                                                           ('news3-caption', 1), ('news3-description', 1) ])

    def test_big_page_number(self):
        self.check_redirect(url('news:')+'?page=666', url('news:')+'?page=1')


class TestFeedRequests(TestRequestsBase):

    def test_feed_page(self):

        models.News.objects.filter(id=self.news1.id).update(created_at=self.news1.created_at - datetime.timedelta(seconds=conf.settings.FEED_ITEMS_DELAY+1))
        models.News.objects.filter(id=self.news3.id).update(created_at=self.news3.created_at - datetime.timedelta(seconds=conf.settings.FEED_ITEMS_DELAY+1))

        texts = [('news1-caption', 1),
                 ('news1-description', 0),
                 ('news1-content', 1),

                 ('news2-caption', 0), # not pass throught time limit
                 ('news2-description', 0),
                 ('news2-content', 0),

                 ('news3-caption', 1),
                 ('news3-description', 0),
                 ('news3-content', 1)]

        self.check_html_ok(self.request_html(url('news:feed')), texts=texts, content_type='application/atom+xml')



class TestShowRequests(TestRequestsBase):

    def test_show_page(self):
        self.check_html_ok(self.client.get(url('news:show', self.news1.id)), texts=(('news1-caption', 4), # third caption in addthis widget
                                                                                               ('news1-description', 1), # description in addthis widget
                                                                                               ('news1-content', 1),
                                                                                               ('pgf-forum-block', 0),))


class TestNewRequests(TestRequestsBase):

    def test_no_rights(self):
        self.check_redirect(url('news:new'), login_page_url(url('news:new')))
        self.request_login(self.user.email)
        self.check_html_ok(self.request_html(url('news:new')), texts=['news.no_edit_rights'])

    def test_success(self):
        self.request_login(self.editor.email)
        self.check_html_ok(self.request_html(url('news:new')), texts=[('news.no_edit_rights', 0)])


class TestCreateRequests(TestRequestsBase):

    def test_no_rights(self):
        self.check_ajax_error(self.post_ajax_json(url('news:create'), {}), 'common.login_required')
        self.request_login(self.user.email)
        self.check_ajax_error(self.post_ajax_json(url('news:create'), {}),
                              'news.no_edit_rights')

    def test_form_errors(self):
        self.request_login(self.editor.email)
        self.check_ajax_error(self.post_ajax_json(url('news:create'), {}),
                              'form_errors')

    def test_success(self):
        self.request_login(self.editor.email)

        with self.check_delta(models.News.objects.all().count, 1):
            self.check_ajax_ok(self.post_ajax_json(url('news:create'), {'caption': 'new-news-caption',
                                                                        'description': 'new-news-description',
                                                                        'content': 'new-news-content'}))

        last_news = logic.load_last_news()

        self.assertEqual(last_news.caption, 'new-news-caption')
        self.assertEqual(last_news.description, 'new-news-description')
        self.assertEqual(last_news.content, 'new-news-content')


class TestEditRequests(TestRequestsBase):

    def test_no_rights(self):
        self.check_redirect(url('news:edit', self.news1.id), login_page_url(url('news:edit', self.news1.id)))
        self.request_login(self.user.email)
        self.check_html_ok(self.request_html(url('news:edit', self.news1.id)), texts=['news.no_edit_rights'])

    def test_success(self):
        self.request_login(self.editor.email)
        self.check_html_ok(self.request_html(url('news:edit', self.news1.id)), texts=[('news.no_edit_rights', 0)])

    def test_no_item(self):
        self.request_login(self.editor.email)
        self.check_html_ok(self.request_html(url('news:edit', 666)), texts=[('news.no_edit_rights', 0)])


class TestSendMailsRequests(TestRequestsBase):

    def test_no_rights(self):
        self.check_ajax_error(self.post_ajax_json(url('news:send-mails', self.news1.id), {}), 'common.login_required')
        self.request_login(self.user.email)
        self.check_ajax_error(self.post_ajax_json(url('news:send-mails', self.news1.id), {}),
                              'news.no_edit_rights')

    def test_success(self):
        self.request_login(self.editor.email)

        with self.check_delta(post_service_models.Message.objects.count, 1):
            self.check_ajax_ok(self.post_ajax_json(url('news:send-mails', self.news1.id)))

        last_message = post_service_prototypes.MessagePrototype._db_latest()

        self.assertEqual(last_message.handler.news_id, self.news1.id)

        news = logic.load_news(self.news1.id)

        self.assertTrue(news.emailed.is_EMAILED)


    def test_restricted(self):
        self.request_login(self.editor.email)

        self.news1.emailed = relations.EMAILED_STATE.random(exclude=(relations.EMAILED_STATE.NOT_EMAILED,))
        logic.save_news(self.news1)

        with self.check_not_changed(post_service_models.Message.objects.count):
            self.check_ajax_error(self.post_ajax_json(url('news:send-mails', self.news1.id)),
                                  'wrong_mail_state')


class TestDisableSendMailsRequests(TestRequestsBase):

    def test_no_rights(self):
        self.check_ajax_error(self.post_ajax_json(url('news:disable-send-mails', self.news1.id), {}), 'common.login_required')
        self.request_login(self.user.email)
        self.check_ajax_error(self.post_ajax_json(url('news:disable-send-mails', self.news1.id), {}),
                              'news.no_edit_rights')

    def test_success(self):
        self.request_login(self.editor.email)

        self.check_ajax_ok(self.post_ajax_json(url('news:disable-send-mails', self.news1.id)))

        news = logic.load_news(self.news1.id)
        self.assertTrue(news.emailed.is_DISABLED)


    def test_restricted(self):
        self.request_login(self.editor.email)

        self.news1.emailed = relations.EMAILED_STATE.random(exclude=(relations.EMAILED_STATE.NOT_EMAILED,))
        logic.save_news(self.news1)

        self.check_ajax_error(self.post_ajax_json(url('news:disable-send-mails', self.news1.id)),
                              'wrong_mail_state')


class TestUpdateRequests(TestRequestsBase):

    def test_no_rights(self):
        self.check_ajax_error(self.post_ajax_json(url('news:update', self.news1.id), {}), 'common.login_required')
        self.request_login(self.user.email)
        self.check_ajax_error(self.post_ajax_json(url('news:update', self.news1.id), {}),
                              'news.no_edit_rights')

    def test_form_errors(self):
        self.request_login(self.editor.email)
        self.check_ajax_error(self.post_ajax_json(url('news:update', self.news1.id), {}),
                              'form_errors')

        news = logic.load_news(self.news1.id)

        self.assertEqual(news.caption, self.news1.caption)
        self.assertEqual(news.description, self.news1.description)
        self.assertEqual(news.content, self.news1.content)

    def test_success(self):
        self.request_login(self.editor.email)

        with self.check_delta(models.News.objects.all().count, 0):
            self.check_ajax_ok(self.post_ajax_json(url('news:update', self.news1.id),
                                                   {'caption': 'updated-news-caption',
                                                    'description': 'updated-news-description',
                                                    'content': 'updated-news-content'}))

        news = logic.load_news(self.news1.id)

        self.assertEqual(news.caption, 'updated-news-caption')
        self.assertEqual(news.description, 'updated-news-description')
        self.assertEqual(news.content, 'updated-news-content')



class TestPostOnForumRequests(TestRequestsBase):

    def test_post_on_forum_success(self):
        self.request_login(self.editor.email)

        response = self.post_ajax_json(url('news:publish-on-forum', self.news1.id))

        self.assertEqual(forum_models.Thread.objects.all().count(), 1)

        thread = forum_models.Thread.objects.all()[0]

        self.check_ajax_ok(response, data={'next_url': url('forum:threads:show', thread.id)})

        self.check_html_ok(self.client.get(url('forum:threads:show', thread.id)), texts=(('news1-caption', 6),
                                                                                                    ('news1-description', 0),
                                                                                                    ('news1-content', 1)))

        self.check_html_ok(self.client.get(url('news:show', self.news1.id)), texts=(('pgf-forum-link', 1),
                                                                                               ('pgf-forum-block', 1),))
        self.check_html_ok(self.client.get(url('news:')), texts=(('pgf-forum-link', 1), ))

    def test_post_on_forum_unloggined(self):
        self.check_redirect(url('news:publish-on-forum', self.news1.id),
                            login_page_url(url('news:publish-on-forum', self.news1.id)))

        self.assertEqual(forum_models.Thread.objects.all().count(), 0)

        self.check_html_ok(self.client.get(url('news:show', self.news1.id)), texts=(('pgf-forum-link', 0), ))
        self.check_html_ok(self.client.get(url('news:')), texts=(('pgf-forum-link', 0), ))


    def test_post_on_forum_unexisting_category(self):
        self.request_login(self.editor.email)

        forum_models.SubCategory.objects.all().delete()

        self.check_ajax_error(self.post_ajax_json(url('news:publish-on-forum', self.news1.id)),
                              'forum_category_not_exists')

        self.assertEqual(forum_models.Thread.objects.all().count(), 0)

        self.check_html_ok(self.client.get(url('news:show', self.news1.id)), texts=(('pgf-forum-link', 0), ))
        self.check_html_ok(self.client.get(url('news:')), texts=(('pgf-forum-link', 0), ))

    def test_post_on_forum_already_publish(self):
        self.request_login(self.editor.email)
        self.post_ajax_json(url('news:publish-on-forum', self.news1.id))

        self.check_ajax_error(self.post_ajax_json(url('news:publish-on-forum', self.news1.id)),
                              'forum_thread_already_exists')


    def test_post_on_forum__no_editor_rights(self):
        self.check_ajax_error(self.post_ajax_json(url('news:publish-on-forum', self.news1.id)),
                              'common.login_required')

        self.request_login(self.user.email)

        self.check_ajax_error(self.post_ajax_json(url('news:publish-on-forum', self.news1.id)),
                              'news.no_edit_rights')
