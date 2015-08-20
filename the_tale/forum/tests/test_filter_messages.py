# coding: utf-8
import mock

from django.test import client

from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url
from the_tale.game.logic import create_test_map

from the_tale.forum.models import Category, SubCategory, Thread, Post
from the_tale.forum.prototypes import ThreadPrototype, PostPrototype, CategoryPrototype, SubCategoryPrototype
from the_tale.forum.conf import forum_settings
from the_tale.forum.views import ThreadPageData

class TestFilterMessages(TestCase):

    def setUp(self):
        super(TestFilterMessages, self).setUp()
        
        create_test_map()
        
        register_user('admin', 'admin@test.com', '111111')
        register_user('main_user', 'main_user@test.com', '111111')
        register_user('second_user', 'second_user@test.com', '111111')
        register_user('nomsg_user', 'nomsg_user@test.com', '111111')
        
        self.admin = AccountPrototype.get_by_nick('admin')
        self.main_user = AccountPrototype.get_by_nick('main_user')
        self.second_user = AccountPrototype.get_by_nick('second_user')
        self.nomsg_user = AccountPrototype.get_by_nick('nomsg_user')
        
        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=2)
        
        self.thread = ThreadPrototype.create(self.subcategory, 'thread-caption', self.main_user, 'thread-text')
        
        self.client = client.Client()
        
        self.post = PostPrototype.create(self.thread, self.main_user, 'post1-text')
        self.post2 = PostPrototype.create(self.thread, self.second_user, 'post2-text')
        self.post3 = PostPrototype.create(self.thread, self.second_user, 'post3-text')
        self.post4 = PostPrototype.create(self.thread, self.main_user, 'post4-text')
        self.post5 = PostPrototype.create(self.thread, self.admin, 'post5-text')
        
        self.post3.delete(self.thread.author)
        
class TestTestData(TestFilterMessages):
    
    def test_initialization(self):
        self.assertEqual(Category.objects.all().count(), 1)
        self.assertEqual(SubCategory.objects.all().count(), 1)
        self.assertEqual(Thread.objects.all().count(), 1)
        self.assertEqual(Post.objects.all().count(), 6)
        
class TestFilterCount(TestFilterMessages):
    
    def test_unlogined_has_filters_count(self):
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=('pgf-filter-option', 3))
        
    def test_logined_has_filters_count(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=('pgf-filter-option', 4))
        
class TestFiltersWorking(TestFilterMessages):

    all_texts = ['thread-text', 'post1-text', 'post2-text', (u'Соообщение удалено владельцем темы', 1), 'post4-text', 'post5-text']
    
    def test_filter_all_messages(self):      
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=self.all_texts)
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)+'?filter_type=0'), texts=self.all_texts)
            
    def test_filter_admin_messages(self):
        admin_user_texts = [('thread-text', 0),
                             ('post1-text', 0), 
                             ('post2-text', 0),
                             ('post3-text', 0),
                             ('post4-text', 0),
                             ('post5-text', 1)]
                               
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)+'?filter_type=1'), texts=admin_user_texts)

    def test_filter_user_messages(self):
        main_user_texts = ['thread-text',
                           'post1-text', 
                          ('post2-text', 0),
                          ('post3-text', 0),
                           'post4-text',
                          ('post5-text', 0)]
                       
        self.request_login('main_user@test.com')               
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)+'?filter_type=2'), texts=main_user_texts)
        
    def test_filter_no_removed_messages(self):
        no_removed_texts = [('thread-text', 1),
                            ('post1-text', 1), 
                            ('post2-text', 1),
                            (u'Соообщение удалено владельцем темы', 0),
                            ('post4-text', 1),
                            ('post5-text', 1)]

        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)+'?filter_type=3'), texts=no_removed_texts)
    
    def test_no_messages_by_filter(self):
        self.request_login('nomsg_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)+'?filter_type=2'), texts=[(self.all_texts, 0), ('alert-info', 1)])
