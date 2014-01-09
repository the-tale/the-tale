# coding: utf-8
import mock

from django.test import client

from dext.utils.urls import url

from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url
from the_tale.game.logic import create_test_map

from the_tale.forum.models import Category, SubCategory, Thread, Post
from the_tale.forum.prototypes import ThreadPrototype, PostPrototype, CategoryPrototype, SubCategoryPrototype
from the_tale.forum.conf import forum_settings


class TestModeration(TestCase):

    def setUp(self):
        super(TestModeration, self).setUp()
        create_test_map()
        register_user('main_user', 'main_user@test.com', '111111')
        register_user('moderator', 'moderator@test.com', '111111')
        register_user('second_user', 'second_user@test.com', '111111')

        self.main_account = AccountPrototype.get_by_nick('main_user')
        self.moderator = AccountPrototype.get_by_nick('moderator')
        self.second_account = AccountPrototype.get_by_nick('second_user')

        group = sync_group(forum_settings.MODERATOR_GROUP_NAME, ['forum.moderate_post', 'forum.moderate_thread'])

        group.user_set.add(self.moderator._model)

        self.client = client.Client()

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=0)
        self.subcategory2 = SubCategoryPrototype.create(category=self.category, caption='subcat2-caption', order=1, closed=True)
        self.thread = ThreadPrototype.create(self.subcategory, 'thread-caption', self.main_account, 'thread-text')
        self.post = PostPrototype.create(self.thread, self.main_account, 'post-text')
        self.post2 = PostPrototype.create(self.thread, self.main_account, 'post2-text')
        self.post5 = PostPrototype.create(self.thread, self.main_account, 'post5-text', technical=True)

        self.thread2 = ThreadPrototype.create(self.subcategory, 'thread2-caption', self.main_account, 'thread2-text')
        self.post3 = PostPrototype.create(self.thread2, self.main_account, 'post3-text')
        self.post4 = PostPrototype.create(self.thread2, self.second_account, 'post4-text')

        self.thread3 = ThreadPrototype.create(self.subcategory, 'thread3-caption', self.second_account, 'thread3-text')


class TestModerationRequests(TestModeration):

    def test_initialization(self):
        self.assertEqual(Category.objects.all().count(), 1)
        self.assertEqual(SubCategory.objects.all().count(), 2)
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)


class TestModerationSubcategoryRequests(TestModeration):

    ###############################
    # add thread
    ###############################

    #button
    def test_loggined_has_add_thread_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:subcategories:show', self.subcategory.id)), texts=[('pgf-new-thread-button', 1)])

    def test_unlogined_has_add_thread_button(self):
        self.check_html_ok(self.request_html(url('forum:subcategories:show', self.subcategory.id)), texts=[('pgf-new-thread-button', 0)])

    def test_loggined_has_no_add_thread_button_in_closed_theme(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:subcategories:show', self.subcategory2.id)), texts=[('pgf-new-thread-button', 0)])

    def test_moderator_has_add_thread_button_in_closed_theme(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.request_html(url('forum:subcategories:show', self.subcategory2.id)), texts=[('pgf-new-thread-button', 1)])


class TestModerationNewThreadRequests(TestModeration):
    #new page

    def test_loggined_new_thread_page(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:subcategories:new-thread', self.subcategory.id)),
                           texts=[('pgf-new-thread-form', 2)])

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_loggined_new_thread_page__banned(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:subcategories:new-thread', self.subcategory.id)),
                           texts=[('pgf-new-thread-form', 0),
                                  ('common.ban_forum', 1)])

    def test_unlogined_new_thread_page(self):
        request_url = url('forum:subcategories:new-thread', self.subcategory.id)
        self.check_redirect(request_url, login_page_url(request_url))

    def test_loggined_new_thread_page_in_closed_theme(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:subcategories:new-thread', self.subcategory2.id)),
                           texts=[('pgf-new-thread-form', 0), ('forum.new_thread.no_permissions', 1)])

    def test_moderator_new_thread_page_in_closed_theme(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.request_html(url('forum:subcategories:new-thread', self.subcategory2.id)),
                                           texts=[('pgf-new-thread-form', 2)])


class TestModerationCreateThreadRequests(TestModeration):

    @mock.patch('the_tale.forum.conf.forum_settings.THREAD_DELAY', 0)
    def test_loggined_create_thread_page(self):
        self.request_login('main_user@test.com')
        response = self.client.post(url('forum:subcategories:create-thread',  self.subcategory.id),
                                    {'caption': 'thread5-caption', 'text': 'thread5-text'})

        thread = Thread.objects.all().order_by('-created_at')[0]

        self.check_ajax_ok(response, {'thread_id': thread.id,
                                      'thread_url': url('forum:threads:show', thread.id)})

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_loggined_create_thread_page__banned(self):
        old_threads_number = ThreadPrototype._db_count()
        self.request_login('main_user@test.com')
        response = self.client.post(url('forum:subcategories:create-thread', self.subcategory.id),
                                    {'caption': 'thread5-caption', 'text': 'thread5-text'})
        self.check_ajax_error(response, 'common.ban_forum')

        self.assertEqual(old_threads_number, ThreadPrototype._db_count())

    def test_unlogined_create_thread_page(self):
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcategory.id),
                                               {'caption': 'thread5-caption', 'text': 'thread5-text'}),
                              'common.login_required')

    def test_loggined_create_thread_page_in_closed_theme(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcategory2.id),
                                               {'caption': 'thread5-caption', 'text': 'thread5-text'}),
                              'forum.create_thread.no_permissions')

    @mock.patch('the_tale.forum.conf.forum_settings.THREAD_DELAY', 0)
    def test_moderator_create_thread_page_in_closed_theme(self):
        self.request_login('moderator@test.com')
        response = self.client.post(url('forum:subcategories:create-thread',  self.subcategory2.id),
                                    {'caption': 'thread5-caption', 'text': 'thread5-text'})

        thread = Thread.objects.all().order_by('-created_at')[0]

        self.check_ajax_ok(response, {'thread_id': thread.id,
                                      'thread_url': url('forum:threads:show', thread.id)})



class TestModerationShowThreadRequests(TestModeration):
    ###############################
    # thread editing
    ###############################

    # button
    def test_unlogined_user_has_edit_theme_button(self):
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-change-thread-button', 0)])

    def test_main_user_has_edit_theme_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-change-thread-button', 1)])

    def test_second_user_has_edit_theme_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-change-thread-button', 0)])

    def test_moderator_user_has_edit_theme_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-change-thread-button', 1)])

    ###############################
    # thread deletion
    ###############################

    def test_main_user_has_remove_thread_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-remove-thread-button', 0)])

    def test_moderator_has_remove_thread_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-remove-thread-button', 2)])

    def test_second_user_has_remove_thread_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-remove-thread-button', 0)])

    ###############################
    # post deletion
    ###############################

    def test_main_user_has_remove_post_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-remove-post-button', 3)])
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread2.id)), texts=[('pgf-remove-post-button', 3)])

    def test_moderator_has_remove_post_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-remove-post-button', 3)])
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread2.id)), texts=[('pgf-remove-post-button', 3)])

    def test_second_user_has_remove_post_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-remove-post-button', 0)])
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread2.id)), texts=[('pgf-remove-post-button', 2)])

    ###############################
    # post editing
    ###############################

    # button
    def test_main_user_has_edit_post_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-change-post-button', 3)])
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread2.id)), texts=[('pgf-change-post-button', 2)])

    def test_moderator_has_edit_post_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-change-post-button', 3)])
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread2.id)), texts=[('pgf-change-post-button', 3)])

    def test_second_user_has_edit_post_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-change-post-button', 0)])
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread2.id)), texts=[('pgf-change-post-button', 1)])
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread3.id)), texts=[('pgf-change-post-button', 1)])



class TestModerationEditThreadRequests(TestModeration):

    # page
    def test_unlogined_user_edit_theme_page(self):
        request_url = url('forum:threads:edit', self.thread.id)
        self.check_redirect(request_url, login_page_url(request_url))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_edit_theme_page__banned(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:edit', self.thread.id)), texts=['common.ban_forum'])

    def test_main_user_edit_theme_page(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:edit', self.thread.id)), texts=[('pgf-edit-thread-form', 2),
                                                                                                ('pgf-thread-subcategory', 0),
                                                                                                ('thread-caption', 3)])

    def test_second_user_edit_theme_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:edit', self.thread.id)), texts=[('pgf-edit-thread-form', 0),
                                                                                                        ('forum.edit_thread.no_permissions', 1),
                                                                                                        ('pgf-thread-subcategory', 0),
                                                                                                        ('thread-caption', 0)])

    def test_moderator_user_edit_theme_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.request_html(url('forum:threads:edit', self.thread.id)), texts=[('pgf-edit-thread-form', 2),
                                                                                                ('pgf-thread-subcategory', 1),
                                                                                                ('thread-caption', 3)])

class TestModerationUpdateThreadRequests(TestModeration):

    # update request
    def test_unlogined_user_update_theme(self):
        self.check_ajax_error(self.client.post(url('forum:threads:update', self.thread.id), {'caption': 'edited caption'}),
                              'common.login_required')
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, self.thread.caption)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_update_theme__banned(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:threads:update', self.thread.id), {'caption': 'edited caption'}),
                              'common.ban_forum')
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, self.thread.caption)

    def test_main_user_update_theme(self):
        self.request_login('main_user@test.com')
        self.check_ajax_ok(self.client.post(url('forum:threads:update', self.thread.id), {'caption': 'edited caption'}))
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, 'edited caption')

    def test_main_user_update_theme_with_subcategory(self):
        self.assertEqual(self.subcategory.posts_count, 5)
        self.assertEqual(self.subcategory.threads_count, 3)
        self.assertEqual(self.subcategory2.posts_count, 0)
        self.assertEqual(self.subcategory2.threads_count, 0)

        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:threads:update', self.thread.id), {'caption': 'edited caption', 'subcategory': self.subcategory2.id}),
                              'forum.update_thread.no_permissions_to_change_subcategory')
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, self.thread.caption)

        self.assertEqual(self.subcategory.posts_count, 5)
        self.assertEqual(self.subcategory.threads_count, 3)
        self.assertEqual(self.subcategory2.posts_count, 0)
        self.assertEqual(self.subcategory2.threads_count, 0)


    def test_main_user_update_theme_with_form_errors(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:threads:update', self.thread.id), {'caption': ''}),
                              'forum.update_thread.form_errors')
        thread = Thread.objects.get(id=self.thread.id)
        self.assertEqual(thread.caption, self.thread.caption)
        self.assertEqual(thread.subcategory_id, self.subcategory.id)

    def test_second_user_update_theme(self):
        self.request_login('second_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:threads:update', self.thread.id), {'caption': 'edited caption'}),
                              'forum.update_thread.no_permissions')
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, self.thread.caption)

    def test_moderator_user_update_theme(self):
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(url('forum:threads:update', self.thread.id), {'caption': 'edited caption'}))
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, 'edited caption')

    def test_moderator_user_update_theme_with_subcategory(self):
        self.assertEqual(self.subcategory.posts_count, 5)
        self.assertEqual(self.subcategory.threads_count, 3)
        self.assertEqual(self.subcategory2.posts_count, 0)
        self.assertEqual(self.subcategory2.threads_count, 0)

        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(url('forum:threads:update', self.thread.id), {'caption': 'edited caption', 'subcategory': self.subcategory2.id}))
        thread = Thread.objects.get(id=self.thread.id)
        self.assertEqual(thread.caption, 'edited caption')
        self.assertEqual(thread.subcategory_id, self.subcategory2.id)

        subcategory = SubCategory.objects.get(id=self.subcategory.id)
        subcategory2 = SubCategory.objects.get(id=self.subcategory2.id)

        self.assertEqual(subcategory.posts_count, 2)
        self.assertEqual(subcategory.threads_count, 2)
        self.assertEqual(subcategory2.posts_count, 3)
        self.assertEqual(subcategory2.threads_count, 1)


class TestModerationDeleteThreadRequests(TestModeration):

    def test_main_user_remove_thread(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:threads:delete', self.thread.id)), 'forum.delete_thread.no_permissions')
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)

    def test_main_user_remove_thread_in_closed_subcategory(self):
        self.subcategory._model.closed = True
        self.subcategory.save()

        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:threads:delete', self.thread.id)), 'forum.delete_thread.no_permissions')
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)

    def test_moderator_remove_thread(self):
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(url('forum:threads:delete', self.thread.id)))
        self.assertEqual(Thread.objects.all().count(), 2)
        self.assertEqual(Post.objects.all().count(), 4)

    def test_second_user_remove_thread(self):
        self.request_login('second_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:threads:delete', self.thread.id)), 'forum.delete_thread.no_permissions')
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)

    def test_second_user_remove_unlogined(self):
        self.check_ajax_error(self.client.post(url('forum:threads:delete', self.thread.id)), 'common.login_required')
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)

    def test_second_user_remove_fast_account(self):
        self.request_login('main_user@test.com')

        self.main_account.is_fast = True
        self.main_account.save()

        self.check_ajax_error(self.client.post(url('forum:threads:delete', self.thread.id)), 'common.fast_account')
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_second_user_remove_banned(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:threads:delete', self.thread.id)), 'common.ban_forum')
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)


class TestModerationDeletePostRequests(TestModeration):

    # main user
    def test_main_user_remove_post(self):
        self.request_login('main_user@test.com')
        self.assertEqual(Thread.objects.get(id=self.thread.id).posts_count, 3)
        self.assertEqual(SubCategory.objects.get(id=self.subcategory.id).posts_count, 5)

        self.check_ajax_ok(self.client.post(url('forum:posts:delete', self.post.id)))
        self.assertTrue(PostPrototype.get_by_id(self.post.id).is_removed)

        # check if edit & remove buttons has dissapeared
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-remove-post-button', 2),
                                                                                                         ('pgf-change-post-button', 2)])


    def test_main_user_remove_post_of_second_user(self):
        self.assertEqual(self.second_account, self.post4.author)
        self.request_login('main_user@test.com')
        self.check_ajax_ok(self.client.post(url('forum:posts:delete', self.post4.id)))
        self.assertEqual(Post.objects.all().count(), 8)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_banned_main_user_remove_post_of_second_user(self):
        old_posts_count = PostPrototype._db_count()
        self.assertEqual(self.second_account, self.post4.author)
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:posts:delete', self.post4.id)), 'common.ban_forum')
        self.assertEqual(old_posts_count, PostPrototype._db_count())

    def test_main_user_remove_first_post(self):
        self.request_login('main_user@test.com')
        post = Post.objects.filter(thread=self.thread.id).order_by('created_at')[0]
        self.check_ajax_error(self.client.post(url('forum:posts:delete', post.id)), 'forum.delete_post.remove_first_post')
        self.assertEqual(Post.objects.all().count(), 8)

    def test_main_user_remove_moderators_post(self):
        post = PostPrototype.create(self.thread, self.moderator, 'moderator-post-text')
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:posts:delete', post.id)), 'forum.delete_post.remove_moderator_post')
        self.assertEqual(Post.objects.all().count(), 9)

    # moderator
    def test_moderator_remove_post(self):
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(url('forum:posts:delete', self.post.id)))
        self.assertEqual(Post.objects.all().count(), 8)

        # check if edit & remove buttons has dissapeared
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread.id)), texts=[('pgf-remove-post-button', 2),
                                                                                                         ('pgf-change-post-button', 2)])

    def test_moderator_remove_post_of_second_user(self):
        self.assertEqual(self.second_account, self.post4.author)
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(url('forum:posts:delete', self.post4.id)))
        self.assertEqual(Post.objects.all().count(), 8)

    def test_moderator_remove_first_post(self):
        self.request_login('moderator@test.com')
        post = Post.objects.filter(thread=self.thread.id).order_by('created_at')[0]
        self.check_ajax_error(self.client.post(url('forum:posts:delete', post.id)), 'forum.delete_post.remove_first_post')
        self.assertEqual(Post.objects.all().count(), 8)

    # second user
    def test_second_user_remove_post(self):
        self.request_login('second_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:posts:delete', self.post.id)), 'forum.delete_post.no_permissions')
        self.assertEqual(Post.objects.all().count(), 8)

    def test_second_user_remove_post_of_second_user(self):
        self.assertEqual(self.second_account, self.post4.author)
        self.request_login('second_user@test.com')
        self.check_ajax_ok(self.client.post(url('forum:posts:delete', self.post4.id)))
        self.assertEqual(Post.objects.all().count(), 8)

    def test_second_user_remove_first_post(self):
        self.request_login('second_user@test.com')
        post = Post.objects.filter(thread=self.thread3.id).order_by('created_at')[0]
        self.check_ajax_error(self.client.post(url('forum:posts:delete', post.id)), 'forum.delete_post.remove_first_post')
        self.assertEqual(Post.objects.all().count(), 8)


class TestModerationEditPostRequests(TestModeration):

    # edit post page
    def test_edit_page_unlogined(self):
        request_url = url('forum:posts:edit', self.post.id)
        self.check_redirect(request_url, login_page_url(request_url))

    def test_edit_page_fast_account(self):
        self.request_login('main_user@test.com')

        self.main_account.is_fast = True
        self.main_account.save()

        self.check_html_ok(self.request_html(url('forum:posts:edit', self.post.id)), texts=['common.fast_account'])

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_edit_page_banned(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:posts:edit', self.post.id)), texts=['common.ban_forum'])

    def test_edit_page_no_permissions(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:posts:edit', self.post4.id)), texts=['forum.edit_thread.no_permissions'])

    def test_edit_page_moderator_access(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.request_html(url('forum:posts:edit', self.post.id)), texts=[('pgf-change-post-form', 2), ('post-text', 1)])

    def test_edit_page_author_access(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.request_html(url('forum:posts:edit', self.post.id)), texts=[('pgf-change-post-form', 2), ('post-text', 1)])



class TestModerationUpdatePostRequests(TestModeration):
    # update post

    def test_update_post_unlogined(self):
        self.check_ajax_error(self.client.post(url('forum:posts:update', self.post.id)), 'common.login_required')
        self.assertEqual(self.post.text, Post.objects.get(id=self.post.id).text)

    def test_update_post_fast_account(self):
        self.request_login('main_user@test.com')

        self.main_account.is_fast = True
        self.main_account.save()

        self.check_ajax_error(self.client.post(url('forum:posts:update', self.post.id)), 'common.fast_account')
        self.assertEqual(self.post.text, Post.objects.get(id=self.post.id).text)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_update_post_banned(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:posts:update', self.post.id)), 'common.ban_forum')
        self.assertEqual(self.post.text, Post.objects.get(id=self.post.id).text)

    def test_update_post_no_permissions(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(url('forum:posts:update', self.post4.id)), 'forum.update_post.no_permissions')
        self.assertEqual(self.post4.text, Post.objects.get(id=self.post4.id).text)

    def test_update_post_form_errors(self):
        self.request_login('moderator@test.com')
        self.check_ajax_error(self.client.post(url('forum:posts:update', self.post.id)), 'forum.update_post.form_errors')

    def test_update_post_moderator_access(self):
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(url('forum:posts:update', self.post.id), {'text': 'new text'}))
        self.assertEqual(Post.objects.get(id=self.post.id).text, 'new text')

    def test_update_post_author_access(self):
        self.request_login('main_user@test.com')
        self.check_ajax_ok(self.client.post(url('forum:posts:update', self.post.id), {'text': 'new text'}))
        self.assertEqual(Post.objects.get(id=self.post.id).text, 'new text')
