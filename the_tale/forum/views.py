# -*- coding: utf-8 -*-
import postmarkup

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from dext.views.resources import handler
from dext.utils.decorators import nested_commit_on_success

from common.utils.resources import Resource

from forum.models import Category, SubCategory, Thread, Post
from forum.forms import NewPostForm, NewThreadForm
from forum.conf import forum_settings
from forum.logic import create_thread, create_post, delete_thread, delete_post


class ForumResource(Resource):

    def __init__(self, request, category=None, subcategory=None, thread_id=None, post_id=None, *args, **kwargs):
        super(ForumResource, self).__init__(request, *args, **kwargs)

        self.post_id = int(post_id) if post_id is not None else None
        self.thread_id = int(thread_id) if thread_id is not None else None
        self.category_slug = category
        self.subcategory_slug = subcategory

    def can_delete_thread(self, thread):
        return self.user == thread.author or self.user.has_perm('forum.delete_thread')

    def can_delete_posts(self, thread):
        return self.user == thread.author or self.user.has_perm('forum.delete_post')

    @property
    def category(self):
        if not hasattr(self, '_category'):
            if self.category_slug:
                self._category = get_object_or_404(Category, slug=self.category_slug)
            else:
                self._category = self.subcategory.category
        return self._category

    @property
    def subcategory(self):
        if not hasattr(self, '_subcategory'):
            if self.subcategory_slug:
                self._subcategory = get_object_or_404(SubCategory, slug=self.subcategory_slug)
            else:
                self._subcategory = self.thread.subcategory
        return self._subcategory

    @property
    def thread(self):
        if not hasattr(self, '_thread'):
            if self.thread_id:
                self._thread = get_object_or_404(Thread, id=self.thread_id)
            else:
                self._thread = self.post.thread
        return self._thread

    @property
    def post(self):
        if not hasattr(self, '_post'):
            self._post = get_object_or_404(Post, id=self.post_id)
        return self._post

    @handler('', method='get')
    def index(self):
        categories = list(Category.objects.all().order_by('order', 'id'))

        subcategories = list(SubCategory.objects.all().order_by('order', 'id'))

        forum_structure = []

        for category in categories:
            children = []
            for subcategory in subcategories:
                if subcategory.category_id == category.id:
                    children.append(subcategory)

            forum_structure.append({'category': category,
                                    'subcategories': children})


        return self.template('forum/index.html',
                             {'forum_structure': forum_structure} )


    @handler('#category', '#subcategory', name='subcategory', method='get')
    def get_subcategory(self):

        threads = Thread.objects.filter(subcategory=self.subcategory).order_by('-updated_at')

        return self.template('forum/subcategory.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'threads': threads} )


    @handler('#category', '#subcategory', 'new-thread', name='new_thread', method='get')
    def new_thread(self):

        if self.account is None:
            return self.template('error.html', {'msg': u'Вы должны войти на сайт, чтобы писать на форуме',
                                                'error_code': 'forum.new_thread.unlogined'})

        if self.account.is_fast:
            return self.template('error.html', {'msg': u'Вы не закончили регистрацию и не можете писать на форуме',
                                                'error_code': 'forum.new_thread.fast_account'})

        return self.template('forum/new_thread.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'new_thread_form': NewThreadForm()} )

    @handler('#category', '#subcategory', 'create-thread', name='create_thread', method='post')
    def create_thread(self):

        if self.account is None:
            return self.json_error('forum.create_thread.unlogined', u'Вы должны войти на сайт, чтобы писать на форуме')

        if self.account.is_fast:
            return self.json_error('forum.create_thread.fast_account', u'Вы не закончили регистрацию и не можете писать на форуме')

        if self.subcategory.closed:
            return self.json_error('forum.create_thread.closed_subcategory', u'Вы не можете создавать темы в данном разделе')

        new_thread_form = NewThreadForm(self.request.POST)

        if not new_thread_form.is_valid():
            return self.json_error('forum.create_thread.form_errors', new_thread_form.errors)

        thread = create_thread(self.subcategory,
                               caption=new_thread_form.c.caption,
                               author=self.account.user,
                               text=new_thread_form.c.text)

        return self.json_ok(data={'thread_id': thread.id})

    @handler('#category', '#subcategory', '#thread_id', 'delete', name='delete-thread', method='post')
    def delete_thread(self):

        if self.account is None:
            return self.json_error('forum.delete_thread.unlogined', u'Вы должны войти на сайт, чтобы удалить тему')

        if self.account.is_fast:
            return self.json_error('forum.delete_thread.fast_account', u'Вы не закончили регистрацию и не можете работать с форумом')

        if not self.can_delete_thread(self.thread):
            return self.json_error('forum.delete_thread.no_permissions', u'У Вас нет прав для удаления темы')

        delete_thread(self.subcategory, self.thread)

        return self.json_ok()

    @handler('#category', '#subcategory', '#thread_id', name='show_thread', method='get')
    def get_thread(self, page=1):

        page = int(page) - 1

        post_from = page * forum_settings.POSTS_ON_PAGE

        if post_from > self.thread.posts_count:
            last_page = self.thread.posts_count / forum_settings.POSTS_ON_PAGE + 1
            url = '%s?page=%d' % (reverse('forum:show_thread', args=[self.category.slug, self.subcategory.slug, self.thread.id]), last_page)
            return self.redirect(url, permanent=False)

        post_to = post_from + forum_settings.POSTS_ON_PAGE

        posts = Post.objects.filter(thread=self.thread).order_by('created_at')[post_from:post_to]

        pages_count = (self.thread.posts_count + 1) / forum_settings.POSTS_ON_PAGE
        if (self.thread.posts_count + 1) % forum_settings.POSTS_ON_PAGE:
            pages_count += 1

        pages_on_page_slice = posts
        if post_from == 0:
            pages_on_page_slice = pages_on_page_slice[1:]
        has_post_on_page = any([post.author == self.user for post in pages_on_page_slice])

        return self.template('forum/thread.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'thread': self.thread,
                              'new_post_form': NewPostForm(),
                              'posts': posts,
                              'pages_numbers': range(pages_count),
                              'start_posts_from': page * forum_settings.POSTS_ON_PAGE,
                              'can_delete_thread': self.can_delete_thread(self.thread),
                              'can_delete_posts': self.can_delete_posts(self.thread),
                              'has_post_on_page': has_post_on_page,
                              'current_page_number': page} )


    @handler('#category', '#subcategory', '#thread_id', 'create-post', name='create_post', method='post')
    def create_post(self):

        if self.account is None:
            return self.json_error('forum.create_post.unlogined', u'Вы должны войти на сайт, чтобы писать на форуме')

        if self.account.is_fast:
            return self.json_error('forum.create_post.fast_account', u'Вы не закончили регистрацию и не можете писать на форуме')

        new_post_form = NewPostForm(self.request.POST)

        if not new_post_form.is_valid():
            return self.json_error('forum.create_post.form_errors', new_post_form.errors)

        create_post(self.subcategory, self.thread, self.account.user, new_post_form.c.text)

        return self.json_ok()

    @handler('posts', '#post_id', 'delete', name='delete-post', method='post')
    def delete_post(self):

        if self.account is None:
            return self.json_error('forum.delete_post.unlogined', u'Вы должны войти на сайт, чтобы удалить сообщение')

        if self.account.is_fast:
            return self.json_error('forum.delete_post.fast_account', u'Вы не закончили регистрацию и не можете работать с форумом')

        if not (self.can_delete_posts(self.thread) or self.post.author == self.user):
            return self.json_error('forum.delete_post.no_permissions', u'У Вас нет прав для удаления сообщения')

        if Post.objects.filter(thread=self.thread, created_at__lt=self.post.created_at).count() == 0:
            return self.json_error('forum.delete_post.remove_first_post', u'Вы не можете удалить первое сообщение в теме')

        delete_post(self.subcategory, self.thread, self.post)

        return self.json_ok()



    @handler('preview', name='preview', method='post')
    def preview(self):
        return self.string(postmarkup.render_bbcode(self.request.POST.get('text', '')))
