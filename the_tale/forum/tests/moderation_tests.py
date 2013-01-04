# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase
from common.utils.permissions import sync_group

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url
from game.logic import create_test_map

from forum.models import Category, SubCategory, Thread, Post
from forum.prototypes import ThreadPrototype, PostPrototype, CategoryPrototype, SubCategoryPrototype


class TestModeration(TestCase):

    def setUp(self):
        create_test_map()
        register_user('main_user', 'main_user@test.com', '111111')
        register_user('moderator', 'moderator@test.com', '111111')
        register_user('second_user', 'second_user@test.com', '111111')

        self.main_account = AccountPrototype.get_by_nick('main_user')
        self.moderator = AccountPrototype.get_by_nick('moderator')
        self.second_account = AccountPrototype.get_by_nick('second_user')

        group = sync_group('forum moderators group', ['forum.moderate_post', 'forum.moderate_thread'])

        group.user_set.add(self.moderator.user)

        self.client = client.Client()

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', slug='subcat-slug', order=0)
        self.subcategory2 = SubCategoryPrototype.create(category=self.category, caption='subcat2-caption', slug='subcat2-slug', order=1, closed=True)
        self.thread = ThreadPrototype.create(self.subcategory, 'thread-caption', self.main_account, 'thread-text')
        self.post = PostPrototype.create(self.thread, self.main_account, 'post-text')
        self.post2 = PostPrototype.create(self.thread, self.main_account, 'post2-text')
        self.post5 = PostPrototype.create(self.thread, self.main_account, 'post5-text', technical=True)

        self.thread2 = ThreadPrototype.create(self.subcategory, 'thread2-caption', self.main_account, 'thread2-text')
        self.post3 = PostPrototype.create(self.thread2, self.main_account, 'post3-text')
        self.post4 = PostPrototype.create(self.thread2, self.second_account, 'post4-text')

        self.thread3 = ThreadPrototype.create(self.subcategory, 'thread3-caption', self.second_account, 'thread3-text')

    def test_initialization(self):
        self.assertEqual(Category.objects.all().count(), 1)
        self.assertEqual(SubCategory.objects.all().count(), 2)
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)

    ###############################
    # add thread
    ###############################

    #button
    def test_loggined_has_add_thread_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=[self.subcategory.slug])), texts=[('pgf-new-thread-button', 1)])

    def test_unlogined_has_add_thread_button(self):
        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=[self.subcategory.slug])), texts=[('pgf-new-thread-button', 0)])

    def test_loggined_has_no_add_thread_button_in_closed_theme(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=[self.subcategory2.slug])), texts=[('pgf-new-thread-button', 0)])

    def test_moderator_has_add_thread_button_in_closed_theme(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=[self.subcategory2.slug])), texts=[('pgf-new-thread-button', 1)])

    #new page

    def test_loggined_new_thread_page(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:new') + ('?subcategory=%s' % self.subcategory.slug)),
                           texts=[('pgf-new-thread-form', 4)])

    def test_unlogined_new_thread_page(self):
        request_url = reverse('forum:threads:new') + ('?subcategory=%s' % self.subcategory.slug)
        self.assertRedirects(self.client.get(request_url), login_url(request_url), status_code=302, target_status_code=200)

    def test_loggined_new_thread_page_in_closed_theme(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:new') + ('?subcategory=%s' % self.subcategory2.slug)),
                           texts=[('pgf-new-thread-form', 0), ('forum.new_thread.no_permissions', 1)])

    def test_moderator_new_thread_page_in_closed_theme(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:new') + ('?subcategory=%s' % self.subcategory2.slug)),
                                           texts=[('pgf-new-thread-form', 4)])

    # create request
    def test_loggined_create_thread_page(self):
        self.request_login('main_user@test.com')
        response = self.client.post(reverse('forum:threads:create') + ('?subcategory=%s' % self.subcategory.slug),
                                    {'caption': 'thread5-caption', 'text': 'thread5-text'})

        thread = Thread.objects.all().order_by('-created_at')[0]

        self.check_ajax_ok(response, {'thread_id': thread.id,
                                      'thread_url': reverse('forum:threads:show', args=[thread.id])})

    def test_unlogined_create_thread_page(self):
        self.check_ajax_error(self.client.post(reverse('forum:threads:create') + ('?subcategory=%s' % self.subcategory.slug),
                                               {'caption': 'thread5-caption', 'text': 'thread5-text'}),
                              'common.login_required')

    def test_loggined_create_thread_page_in_closed_theme(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(reverse('forum:threads:create') + ('?subcategory=%s' % self.subcategory2.slug),
                                               {'caption': 'thread5-caption', 'text': 'thread5-text'}),
                              'forum.create_thread.no_permissions')

    def test_moderator_create_thread_page_in_closed_theme(self):
        self.request_login('moderator@test.com')
        response = self.client.post(reverse('forum:threads:create') + ('?subcategory=%s' % self.subcategory2.slug),
                                    {'caption': 'thread5-caption', 'text': 'thread5-text'})

        thread = Thread.objects.all().order_by('-created_at')[0]

        self.check_ajax_ok(response, {'thread_id': thread.id,
                                      'thread_url': reverse('forum:threads:show', args=[thread.id])})


    ###############################
    # thread editing
    ###############################

    # button
    def test_unlogined_user_has_edit_theme_button(self):
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-change-thread-button', 0)])

    def test_main_user_has_edit_theme_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-change-thread-button', 1)])

    def test_second_user_has_edit_theme_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-change-thread-button', 0)])

    def test_moderator_user_has_edit_theme_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-change-thread-button', 1)])

    # page
    def test_unlogined_user_edit_theme_page(self):
        request_url = reverse('forum:threads:edit', args=[self.thread.id])
        self.assertRedirects(self.client.get(request_url), login_url(request_url), status_code=302, target_status_code=200)

    def test_main_user_edit_theme_page(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:edit', args=[self.thread.id])), texts=[('pgf-edit-thread-form', 2),
                                                                                                        ('pgf-thread-subcategory', 0),
                                                                                                        ('thread-caption', 2)])

    def test_second_user_edit_theme_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:edit', args=[self.thread.id])), texts=[('pgf-edit-thread-form', 0),
                                                                                                        ('forum.edit_thread.no_permissions', 1),
                                                                                                        ('pgf-thread-subcategory', 0),
                                                                                                        ('thread-caption', 0)])

    def test_moderator_user_edit_theme_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:edit', args=[self.thread.id])), texts=[('pgf-edit-thread-form', 2),
                                                                                                        ('pgf-thread-subcategory', 1),
                                                                                                        ('thread-caption', 2)])
    # update request
    def test_unlogined_user_update_theme(self):
        self.check_ajax_error(self.client.post(reverse('forum:threads:update', args=[self.thread.id]), {'caption': 'edited caption'}),
                              'common.login_required')
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, self.thread.caption)

    def test_main_user_update_theme(self):
        self.request_login('main_user@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:threads:update', args=[self.thread.id]), {'caption': 'edited caption'}))
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, 'edited caption')

    def test_main_user_update_theme_with_subcategory(self):
        self.assertEqual(self.subcategory.posts_count, 5)
        self.assertEqual(self.subcategory.threads_count, 3)
        self.assertEqual(self.subcategory2.posts_count, 0)
        self.assertEqual(self.subcategory2.threads_count, 0)

        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(reverse('forum:threads:update', args=[self.thread.id]), {'caption': 'edited caption', 'subcategory': self.subcategory2.id}),
                              'forum.update_thread.no_permissions_to_change_subcategory')
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, self.thread.caption)

        self.assertEqual(self.subcategory.posts_count, 5)
        self.assertEqual(self.subcategory.threads_count, 3)
        self.assertEqual(self.subcategory2.posts_count, 0)
        self.assertEqual(self.subcategory2.threads_count, 0)


    def test_main_user_update_theme_with_form_errors(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(reverse('forum:threads:update', args=[self.thread.id]), {'caption': ''}),
                              'forum.update_thread.form_errors')
        thread = Thread.objects.get(id=self.thread.id)
        self.assertEqual(thread.caption, self.thread.caption)
        self.assertEqual(thread.subcategory_id, self.subcategory.id)

    def test_second_user_update_theme(self):
        self.request_login('second_user@test.com')
        self.check_ajax_error(self.client.post(reverse('forum:threads:update', args=[self.thread.id]), {'caption': 'edited caption'}),
                              'forum.update_thread.no_permissions')
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, self.thread.caption)

    def test_moderator_user_update_theme(self):
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:threads:update', args=[self.thread.id]), {'caption': 'edited caption'}))
        self.assertEqual(Thread.objects.get(id=self.thread.id).caption, 'edited caption')

    def test_moderator_user_update_theme_with_subcategory(self):
        self.assertEqual(self.subcategory.posts_count, 5)
        self.assertEqual(self.subcategory.threads_count, 3)
        self.assertEqual(self.subcategory2.posts_count, 0)
        self.assertEqual(self.subcategory2.threads_count, 0)

        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:threads:update', args=[self.thread.id]), {'caption': 'edited caption', 'subcategory': self.subcategory2.id}))
        thread = Thread.objects.get(id=self.thread.id)
        self.assertEqual(thread.caption, 'edited caption')
        self.assertEqual(thread.subcategory_id, self.subcategory2.id)

        subcategory = SubCategory.objects.get(id=self.subcategory.id)
        subcategory2 = SubCategory.objects.get(id=self.subcategory2.id)

        self.assertEqual(subcategory.posts_count, 2)
        self.assertEqual(subcategory.threads_count, 2)
        self.assertEqual(subcategory2.posts_count, 3)
        self.assertEqual(subcategory2.threads_count, 1)


    ###############################
    # thread deletion
    ###############################

    def test_main_user_has_remove_thread_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-remove-thread-button', 2)])

    def test_moderator_has_remove_thread_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-remove-thread-button', 2)])

    def test_second_user_has_remove_thread_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-remove-thread-button', 0)])

    def test_main_user_remove_thread(self):
        self.request_login('main_user@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:threads:delete', args=[self.thread.id])))
        self.assertEqual(Thread.objects.all().count(), 2)
        self.assertEqual(Post.objects.all().count(), 4)

    def test_moderator_remove_thread(self):
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:threads:delete', args=[self.thread.id])))
        self.assertEqual(Thread.objects.all().count(), 2)
        self.assertEqual(Post.objects.all().count(), 4)

    def test_second_user_remove_thread(self):
        self.request_login('second_user@test.com')
        self.check_ajax_error(self.client.post(reverse('forum:threads:delete', args=[self.thread.id])), 'forum.delete_thread.no_permissions')
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)

    def test_second_user_remove_unlogined(self):
        self.check_ajax_error(self.client.post(reverse('forum:threads:delete', args=[self.thread.id])), 'common.login_required')
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)

    def test_second_user_remove_fast_account(self):
        self.request_login('main_user@test.com')

        self.main_account.is_fast = True
        self.main_account.save()

        self.check_ajax_error(self.client.post(reverse('forum:threads:delete', args=[self.thread.id])), 'forum.delete_thread.fast_account')
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 8)

    ###############################
    # post deletion
    ###############################

    def test_main_user_has_remove_post_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-remove-post-button', 3)])
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread2.id])), texts=[('pgf-remove-post-button', 3)])

    def test_moderator_has_remove_post_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-remove-post-button', 3)])
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread2.id])), texts=[('pgf-remove-post-button', 3)])

    def test_second_user_has_remove_post_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-remove-post-button', 0)])
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread2.id])), texts=[('pgf-remove-post-button', 2)])

    # main user
    def test_main_user_remove_post(self):
        self.request_login('main_user@test.com')
        self.assertEqual(Thread.objects.get(id=self.thread.id).posts_count, 3)
        self.assertEqual(SubCategory.objects.get(id=self.subcategory.id).posts_count, 5)

        self.check_ajax_ok(self.client.post(reverse('forum:posts:delete', args=[self.post.id])))
        self.assertTrue(PostPrototype.get_by_id(self.post.id).is_removed)

        # check if edit & remove buttons has dissapeared
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-remove-post-button', 2),
                                                                                                         ('pgf-change-post-button', 2)])


    def test_main_user_remove_post_of_second_user(self):
        self.assertEqual(self.second_account, self.post4.author)
        self.request_login('main_user@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:posts:delete', args=[self.post4.id])))
        self.assertEqual(Post.objects.all().count(), 8)

    def test_main_user_remove_first_post(self):
        self.request_login('main_user@test.com')
        post = Post.objects.filter(thread=self.thread.id).order_by('created_at')[0]
        self.check_ajax_error(self.client.post(reverse('forum:posts:delete', args=[post.id])), 'forum.delete_post.remove_first_post')
        self.assertEqual(Post.objects.all().count(), 8)

    # moderator
    def test_moderator_remove_post(self):
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:posts:delete', args=[self.post.id])))
        self.assertEqual(Post.objects.all().count(), 8)

        # check if edit & remove buttons has dissapeared
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-remove-post-button', 2),
                                                                                                         ('pgf-change-post-button', 2)])

    def test_moderator_remove_post_of_second_user(self):
        self.assertEqual(self.second_account, self.post4.author)
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:posts:delete', args=[self.post4.id])))
        self.assertEqual(Post.objects.all().count(), 8)

    def test_moderator_remove_first_post(self):
        self.request_login('moderator@test.com')
        post = Post.objects.filter(thread=self.thread.id).order_by('created_at')[0]
        self.check_ajax_error(self.client.post(reverse('forum:posts:delete', args=[post.id])), 'forum.delete_post.remove_first_post')
        self.assertEqual(Post.objects.all().count(), 8)

    # second user
    def test_second_user_remove_post(self):
        self.request_login('second_user@test.com')
        self.check_ajax_error(self.client.post(reverse('forum:posts:delete', args=[self.post.id])), 'forum.delete_post.no_permissions')
        self.assertEqual(Post.objects.all().count(), 8)

    def test_second_user_remove_post_of_second_user(self):
        self.assertEqual(self.second_account, self.post4.author)
        self.request_login('second_user@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:posts:delete', args=[self.post4.id])))
        self.assertEqual(Post.objects.all().count(), 8)

    def test_second_user_remove_first_post(self):
        self.request_login('second_user@test.com')
        post = Post.objects.filter(thread=self.thread3.id).order_by('created_at')[0]
        self.check_ajax_error(self.client.post(reverse('forum:posts:delete', args=[post.id])), 'forum.delete_post.remove_first_post')
        self.assertEqual(Post.objects.all().count(), 8)

    ###############################
    # post editing
    ###############################

    # button
    def test_main_user_has_edit_post_button(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-change-post-button', 3)])
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread2.id])), texts=[('pgf-change-post-button', 2)])

    def test_moderator_has_edit_post_button(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-change-post-button', 3)])
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread2.id])), texts=[('pgf-change-post-button', 3)])

    def test_second_user_has_edit_post_button(self):
        self.request_login('second_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread.id])), texts=[('pgf-change-post-button', 0)])
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread2.id])), texts=[('pgf-change-post-button', 1)])
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread3.id])), texts=[('pgf-change-post-button', 1)])

    # edit post page
    def test_edit_page_unlogined(self):
        request_url = reverse('forum:posts:edit', args=[self.post.id])
        self.assertRedirects(self.client.get(request_url), login_url(request_url), status_code=302, target_status_code=200)

    def test_edit_page_fast_account(self):
        self.request_login('main_user@test.com')

        self.main_account.is_fast = True
        self.main_account.save()

        self.check_html_ok(self.client.get(reverse('forum:posts:edit', args=[self.post.id])), texts=['forum.edit_thread.fast_account'])

    def test_edit_page_no_permissions(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:posts:edit', args=[self.post4.id])), texts=['forum.edit_thread.no_permissions'])

    def test_edit_page_moderator_access(self):
        self.request_login('moderator@test.com')
        self.check_html_ok(self.client.get(reverse('forum:posts:edit', args=[self.post.id])), texts=[('pgf-change-post-form', 4), ('post-text', 1)])

    def test_edit_page_author_access(self):
        self.request_login('main_user@test.com')
        self.check_html_ok(self.client.get(reverse('forum:posts:edit', args=[self.post.id])), texts=[('pgf-change-post-form', 4), ('post-text', 1)])

    # update post

    def test_update_post_unlogined(self):
        self.check_ajax_error(self.client.post(reverse('forum:posts:update', args=[self.post.id])), 'common.login_required')
        self.assertEqual(self.post.text, Post.objects.get(id=self.post.id).text)

    def test_update_post_fast_account(self):
        self.request_login('main_user@test.com')

        self.main_account.is_fast = True
        self.main_account.save()

        self.check_ajax_error(self.client.post(reverse('forum:posts:update', args=[self.post.id])), 'forum.update_post.fast_account')
        self.assertEqual(self.post.text, Post.objects.get(id=self.post.id).text)

    def test_update_post_no_permissions(self):
        self.request_login('main_user@test.com')
        self.check_ajax_error(self.client.post(reverse('forum:posts:update', args=[self.post4.id])), 'forum.update_post.no_permissions')
        self.assertEqual(self.post4.text, Post.objects.get(id=self.post4.id).text)

    def test_update_post_form_errors(self):
        self.request_login('moderator@test.com')
        self.check_ajax_error(self.client.post(reverse('forum:posts:update', args=[self.post.id])), 'forum.update_post.form_errors')

    def test_update_post_moderator_access(self):
        self.request_login('moderator@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:posts:update', args=[self.post.id]), {'text': 'new text'}))
        self.assertEqual(Post.objects.get(id=self.post.id).text, 'new text')

    def test_update_post_author_access(self):
        self.request_login('main_user@test.com')
        self.check_ajax_ok(self.client.post(reverse('forum:posts:update', args=[self.post.id]), {'text': 'new text'}))
        self.assertEqual(Post.objects.get(id=self.post.id).text, 'new text')
