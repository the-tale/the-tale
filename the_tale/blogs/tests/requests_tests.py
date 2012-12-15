# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.permissions import sync_group
from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from game.logic import create_test_map

# from forum.models import Post

from blogs.models import Post, Vote, POST_STATE
from blogs.prototypes import PostPrototype, VotePrototype
from blogs.conf import blogs_settings


class BaseTestRequests(TestCase):

    def setUp(self):
        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

        from forum.models import Category, SubCategory

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=blogs_settings.FORUM_CATEGORY_SLUG + '-caption',
                                   slug=blogs_settings.FORUM_CATEGORY_SLUG,
                                   category=forum_category)

    def create_posts(self, number, author, caption_template, text_template):
        return [PostPrototype.create(author, caption_template % i, text_template % i) for i in xrange(number) ]

    def check_post_votes(self, post_id, votes):
        post = Post.objects.get(id=post_id)
        self.assertEqual(post.votes, votes)

    def check_vote(self, vote, voter, value, post_id):
        self.assertEqual(vote.voter, voter)
        self.assertEqual(vote.value, value)
        self.assertEqual(vote.model.post.id, post_id)



class TestIndexRequests(BaseTestRequests):

    def test_no_posts(self):
        self.check_html_ok(self.client.get(reverse('blogs:posts:')), texts=(('pgf-no-posts-message', 1),))

    def test_one_page(self):
        self.create_posts(2, self.account_1, 'caption-a1-%d', 'text-a1-%d')
        self.create_posts(3, self.account_2, 'caption-a2-%d', 'text-a2-%d')

        declined_post = PostPrototype(Post.objects.get(caption='caption-a1-0'))
        declined_post.state = POST_STATE.DECLINED
        declined_post.save()

        texts = [('pgf-no-posts-message', 0),
                 ('caption-a1-0', 0), ('text-a1-0', 0), # test decline record hidding
                 ('caption-a1-1', 1), ('text-a1-1', 0),
                 ('caption-a2-0', 1), ('text-a2-0', 0),
                 ('caption-a2-1', 1), ('text-a2-1', 0),
                 ('caption-a2-2', 1), ('text-a2-2', 0),
                 ('test_user_1', 1),
                 ('test_user_2', 3)]

        self.check_html_ok(self.client.get(reverse('blogs:posts:')), texts=texts)

    def create_two_pages(self):
        self.create_posts(blogs_settings.POSTS_ON_PAGE, self.account_1, 'caption-a1-%d', 'text-a1-%d')
        self.create_posts(3, self.account_2, 'caption-a2-%d', 'text-a2-%d')

    def test_two_pages(self):
        self.create_two_pages()

        texts = [('pgf-no-posts-message', 0),
                 ('caption-a1-0', 1), ('text-a1-0', 0),
                 ('caption-a1-1', 1), ('text-a1-1', 0),
                 ('caption-a1-2', 1), ('text-a1-2', 0),
                 ('caption-a1-3', 0), ('text-a1-3', 0),
                 ('caption-a2-0', 0), ('text-a2-0', 0),
                 ('caption-a2-2', 0), ('text-a2-2', 0),
                 ('test_user_1', 3), ('test_user_2', 0)]

        self.check_html_ok(self.client.get(reverse('blogs:posts:')+'?page=2'), texts=texts)

    def test_index_redirect_from_large_page(self):
        self.assertRedirects(self.client.get(reverse('blogs:posts:')+'?page=2'),
                             reverse('blogs:posts:')+'?page=1', status_code=302, target_status_code=200)

    def test_filter_by_user_no_posts_message(self):
        self.create_two_pages()

        result, account_id, bundle_id = register_user('test_user_4', 'test_user_4@test.com', '111111')
        account_4 = AccountPrototype.get_by_id(account_id)
        self.check_html_ok(self.client.get(reverse('blogs:posts:')+('?author_id=%d' % account_4.id)),
                           texts=[('pgf-no-posts-message', 1)])


    def test_filter_by_user(self):
        self.create_two_pages()

        account_1_texts = [('pgf-no-posts-message', 0),
                           ('caption-a1-0', 1),
                           ('caption-a1-1', 1),
                           ('caption-a1-2', 1),
                           ('caption-a1-3', 1),
                           ('caption-a2-0', 0),
                           ('caption-a2-2', 0),
                           ('test_user_1', blogs_settings.POSTS_ON_PAGE + 1), #1 for filter text
                           ('test_user_2', 0)]

        self.check_html_ok(self.client.get(reverse('blogs:posts:')+('?author_id=%d' % self.account_1.id)),
                           texts=account_1_texts)

        account_2_texts = [('pgf-no-posts-message', 0),
                           ('caption-a1-0', 0),
                           ('caption-a1-1', 0),
                           ('caption-a1-2', 0),
                           ('caption-a1-3', 0),
                           ('caption-a2-0', 1),
                           ('caption-a2-2', 1),
                           ('test_user_1', 0),
                           ('test_user_2', 3+1)] # 1 for filter text


        self.check_html_ok(self.client.get(reverse('blogs:posts:')+('?author_id=%d' % self.account_2.id)),
                           texts=account_2_texts)


class TestNewRequests(BaseTestRequests):

    def setUp(self):
        super(TestNewRequests, self).setUp()
        self.request_login('test_user_1@test.com')

    def test_unlogined(self):
        self.request_logout()
        url = reverse('blogs:posts:new')
        self.check_redirect(url, login_url(url))

    def test_is_fast(self):
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.client.get(reverse('blogs:posts:new')), texts=(('blogs.posts.fast_account', 1),))

    def test_success(self):
        self.check_html_ok(self.client.get(reverse('blogs:posts:new')))


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super(TestShowRequests, self).setUp()
        self.create_posts(1, self.account_1, 'caption-a2-%d', 'text-a2-%d')
        self.post = Post.objects.all()[0]

    def test_unexsists(self):
        self.check_html_ok(self.client.get(reverse('blogs:posts:show', args=[666])), status_code=404)

    def test_show(self):

        texts = [('caption-a2-0', 3 + 1), # 1 from social sharing
                 ('text-a2-0', 1 + 1) ] # 1 from social sharing

        self.check_html_ok(self.client.get(reverse('blogs:posts:show', args=[self.post.id])), texts=texts)

    def test_wrong_state(self):
        self.post.state = POST_STATE.DECLINED
        self.post.save()
        self.check_html_ok(self.client.get(reverse('blogs:posts:show', args=[self.post.id])), texts=(('blogs.posts.post_declined', 1),))



class TestCreateRequests(BaseTestRequests):

    def setUp(self):
        super(TestCreateRequests, self).setUp()
        self.request_login('test_user_1@test.com')

    def get_post_data(self):
        return {'caption': 'post-caption',
                'text': 'post-text'}

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('blogs:posts:create'), self.get_post_data()), 'common.login_required')

    def test_is_fast(self):
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_ajax_error(self.client.post(reverse('blogs:posts:create'), self.get_post_data()), 'blogs.posts.fast_account')

    def test_success(self):
        response = self.client.post(reverse('blogs:posts:create'), self.get_post_data())

        post = PostPrototype(Post.objects.all()[0])
        self.assertEqual(post.caption, 'post-caption')
        self.assertEqual(post.text, 'post-text')
        self.assertEqual(post.votes, 1)

        vote = VotePrototype(Vote.objects.all()[0])
        self.check_vote(vote, self.account_1, True, post.id)

        self.check_ajax_ok(response, data={'next_url': reverse('blogs:posts:show', args=[post.id])})

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('blogs:posts:create'), {}), 'blogs.posts.create.form_errors')


class TestVoteRequests(BaseTestRequests):

    def setUp(self):
        super(TestVoteRequests, self).setUp()

        self.request_login('test_user_1@test.com')
        self.client.post(reverse('blogs:posts:create'), {'caption': 'post-caption',
                                                         'text': 'post-text'})
        self.post = PostPrototype(Post.objects.all()[0])

        self.request_logout()
        self.request_login('test_user_2@test.com')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('blogs:posts:vote', args=[self.post.id]) + '?value=for', {}), 'common.login_required')

    def test_is_fast(self):
        self.account_2.is_fast = True
        self.account_2.save()
        self.check_ajax_error(self.client.post(reverse('blogs:posts:vote', args=[self.post.id]) + '?value=for', {}), 'blogs.posts.fast_account')
        self.check_post_votes(self.post.id, 1)

    def test_post_not_exists(self):
        self.check_ajax_error(self.client.post(reverse('blogs:posts:vote', args=[666]) + '?value=for', {}), 'blogs.posts.wrong_post_id')

    def test_wrong_value(self):
        self.check_ajax_error(self.client.post(reverse('blogs:posts:vote', args=[self.post.id]) + '?value=xxx', {}), 'blogs.posts.vote.wrong_value')
        self.check_post_votes(self.post.id, 1)

    def test_success_for(self):
        self.check_ajax_ok(self.client.post(reverse('blogs:posts:vote', args=[self.post.id]) + '?value=for', {}))
        vote = VotePrototype(Vote.objects.all()[1])
        self.check_vote(vote, self.account_2, True, self.post.id)
        self.check_post_votes(self.post.id, 2)

    def test_success_agains(self):
        self.check_ajax_ok(self.client.post(reverse('blogs:posts:vote', args=[self.post.id]) + '?value=against', {}))
        vote = VotePrototype(Vote.objects.all()[1])
        self.check_vote(vote, self.account_2, False, self.post.id)
        self.check_post_votes(self.post.id, 0)

    def test_already_exists(self):
        self.check_ajax_ok(self.client.post(reverse('blogs:posts:vote', args=[self.post.id]) + '?value=for', {}))
        self.check_ajax_ok(self.client.post(reverse('blogs:posts:vote', args=[self.post.id]) + '?value=against', {}))
        self.check_post_votes(self.post.id, 0)


class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super(TestEditRequests, self).setUp()

        self.request_login('test_user_1@test.com')

        self.client.post(reverse('blogs:posts:create'), {'caption': 'post-X-caption',
                                                         'text': 'post-X-text'})
        self.post = PostPrototype(Post.objects.all()[0])

    def test_unlogined(self):
        self.request_logout()
        url = reverse('blogs:posts:edit', args=[self.post.id])
        self.check_redirect(url, login_url(url))

    def test_is_fast(self):
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.client.get(reverse('blogs:posts:edit', args=[self.post.id])), texts=(('blogs.posts.fast_account', 1),))

    def test_unexsists(self):
        self.check_html_ok(self.client.get(reverse('blogs:posts:edit', args=[666])), status_code=404)

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.client.get(reverse('blogs:posts:edit', args=[self.post.id])), texts=(('blogs.posts.no_edit_rights', 1),))

    def test_moderator(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        group = sync_group('folclor moderation group', ['blogs.moderate_post'])
        group.user_set.add(self.account_2.user)
        self.check_html_ok(self.client.get(reverse('blogs:posts:edit', args=[self.post.id])), texts=((self.post.caption, 1),
                                                                                                     (self.post.text, 1)))

    def test_wrong_state(self):
        self.post.state = POST_STATE.DECLINED
        self.post.save()
        self.check_html_ok(self.client.get(reverse('blogs:posts:edit', args=[self.post.id])), texts=(('blogs.posts.post_declined', 1),))

    def test_success(self):
        self.check_html_ok(self.client.get(reverse('blogs:posts:edit', args=[self.post.id])), texts=((self.post.caption, 1),
                                                                                                     (self.post.text, 1)))


class TestUpdateRequests(BaseTestRequests):

    def setUp(self):
        super(TestUpdateRequests, self).setUp()
        self.request_login('test_user_1@test.com')
        self.client.post(reverse('blogs:posts:create'), {'caption': 'post-X-caption',
                                                         'text': 'post-X-text'})
        self.post = PostPrototype(Post.objects.all()[0])

    def get_post_data(self):
        return {'caption': 'new-X-caption',
                'text': 'new-X-text'}

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('blogs:posts:update', args=[self.post.id]), self.get_post_data()), 'common.login_required')

    def test_is_fast(self):
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_ajax_error(self.client.post(reverse('blogs:posts:update', args=[self.post.id]), self.get_post_data()), 'blogs.posts.fast_account')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error(self.client.post(reverse('blogs:posts:update', args=[self.post.id]), self.get_post_data()), 'blogs.posts.no_edit_rights')

    def test_moderator(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        group = sync_group('folclor moderation group', ['blogs.moderate_post'])
        group.user_set.add(self.account_2.user)
        self.check_ajax_ok(self.client.post(reverse('blogs:posts:update', args=[self.post.id]), self.get_post_data()))

    def test_wrong_state(self):
        self.post.state = POST_STATE.DECLINED
        self.post.save()
        self.check_ajax_error(self.client.post(reverse('blogs:posts:update', args=[self.post.id]), self.get_post_data()), 'blogs.posts.post_declined')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('blogs:posts:update', args=[self.post.id]), {}), 'blogs.posts.update.form_errors')

    def test_update_success(self):
        old_updated_at = self.post.updated_at

        self.assertEqual(Post.objects.all().count(), 1)

        self.check_ajax_ok(self.client.post(reverse('blogs:posts:update', args=[self.post.id]), self.get_post_data()))

        self.post = PostPrototype.get_by_id(self.post.id)
        self.assertTrue(old_updated_at < self.post.updated_at)

        self.assertEqual(self.post.caption, 'new-X-caption')
        self.assertEqual(self.post.text, 'new-X-text')

        self.assertEqual(Post.objects.all().count(), 1)


class TestModerateRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerateRequests, self).setUp()

        self.request_login('test_user_1@test.com')

        self.client.post(reverse('blogs:posts:create'), {'caption': 'post-caption',
                                                         'text': 'post-text'})
        self.post = PostPrototype(Post.objects.all()[0])

        self.request_logout()
        self.request_login('test_user_2@test.com')

        group = sync_group('folclor moderation group', ['blogs.moderate_post'])
        group.user_set.add(self.account_2.user)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('blogs:posts:accept', args=[self.post.id]), {}), 'common.login_required')
        self.check_ajax_error(self.client.post(reverse('blogs:posts:decline', args=[self.post.id]), {}), 'common.login_required')

    def test_is_fast(self):
        self.account_2.is_fast = True
        self.account_2.save()
        self.check_ajax_error(self.client.post(reverse('blogs:posts:accept', args=[self.post.id]), {}), 'blogs.posts.fast_account')
        self.check_ajax_error(self.client.post(reverse('blogs:posts:decline', args=[self.post.id]), {}), 'blogs.posts.fast_account')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(reverse('blogs:posts:accept', args=[666]), {}), 'blogs.posts.wrong_post_id')
        self.check_ajax_error(self.client.post(reverse('blogs:posts:decline', args=[666]), {}), 'blogs.posts.wrong_post_id')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.client.post(reverse('blogs:posts:accept', args=[self.post.id]), {}), 'blogs.posts.moderator_rights_required')
        self.check_ajax_error(self.client.post(reverse('blogs:posts:decline', args=[self.post.id]), {}), 'blogs.posts.moderator_rights_required')

    def test_delete_success(self):
        self.check_ajax_ok(self.client.post(reverse('blogs:posts:accept', args=[self.post.id]), {}))
        self.assertTrue(PostPrototype.get_by_id(self.post.id).state.is_accepted)

        self.check_ajax_ok(self.client.post(reverse('blogs:posts:decline', args=[self.post.id]), {}))
        self.assertTrue(PostPrototype.get_by_id(self.post.id).state.is_declined)
