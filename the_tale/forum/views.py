# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from dext.views.resources import handler
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.decorators import login_required

from forum.models import Category, SubCategory, Thread, Post
from forum.forms import NewPostForm, NewThreadForm, EditThreadForm
from forum.conf import forum_settings
from forum.prototypes import CategoryPrototype, SubCategoryPrototype, ThreadPrototype, PostPrototype

class BaseForumResource(Resource):

    def initialize(self, category=None, subcategory=None, thread_id=None, post_id=None, *args, **kwargs):
        super(BaseForumResource, self).initialize(*args, **kwargs)

        self.post_id = int(post_id) if post_id is not None else None
        self.thread_id = int(thread_id) if thread_id is not None else None
        self.category_slug = category
        self.subcategory_slug = subcategory

    def can_delete_thread(self, thread):
        return self.account == thread.author or self.user.has_perm('forum.moderate_thread')

    def can_change_thread(self, thread):
        return self.account == thread.author or self.user.has_perm('forum.moderate_thread')

    def can_change_thread_category(self):
        return self.user.has_perm('forum.moderate_thread')

    def can_delete_posts(self, thread):
        return self.account == thread.author or self.user.has_perm('forum.moderate_post')

    def can_create_thread(self, subcategory):
        if not subcategory.closed:
            return self.account and not self.account.is_fast

        return self.user.has_perm('forum.moderate_thread')

    def can_change_posts(self):
        return self.user.has_perm('forum.moderate_post')

    @property
    def category(self):
        if not hasattr(self, '_category'):
            if self.category_slug:
                self._category = CategoryPrototype.get_by_slug(self.category_slug)
            else:
                self._category = self.subcategory.category
        return self._category

    @property
    def subcategory(self):
        if not hasattr(self, '_subcategory'):
            if self.subcategory_slug:
                self._subcategory = SubCategoryPrototype.get_by_slug(self.subcategory_slug)
            else:
                self._subcategory = self.thread.subcategory
        return self._subcategory

    @property
    def thread(self):
        if not hasattr(self, '_thread'):
            if self.thread_id:
                self._thread = ThreadPrototype.get_by_id(self.thread_id)
            else:
                self._thread = self.post.thread
        return self._thread

    @property
    def post(self):
        if not hasattr(self, '_post'):
            self._post = PostPrototype.get_by_id(self.post_id)
        return self._post

class PostsResource(BaseForumResource):

    @login_required
    @handler('create', method='post')
    def create_post(self, thread_id):

        thread = ThreadPrototype.get_by_id(thread_id)

        if self.account.is_fast:
            return self.json_error('forum.create_post.fast_account', u'Вы не закончили регистрацию и не можете писать на форуме')

        new_post_form = NewPostForm(self.request.POST)

        if not new_post_form.is_valid():
            return self.json_error('forum.create_post.form_errors', new_post_form.errors)

        PostPrototype.create(thread, self.account, new_post_form.c.text)

        return self.json_ok(data={'thread_url': reverse('forum:threads:show', args=[thread.id]) + ('?page=%d' % thread.paginator.pages_count)})

    @login_required
    @handler('#post_id', 'delete', method='post')
    def delete_post(self):

        if self.account.is_fast:
            return self.json_error('forum.delete_post.fast_account', u'Вы не закончили регистрацию и не можете работать с форумом')

        if not (self.can_delete_posts(self.thread) or self.post.author == self.account):
            return self.json_error('forum.delete_post.no_permissions', u'У Вас нет прав для удаления сообщения')

        if Post.objects.filter(thread=self.thread.model, created_at__lt=self.post.created_at).count() == 0:
            return self.json_error('forum.delete_post.remove_first_post', u'Вы не можете удалить первое сообщение в теме')

        self.post.delete(self.account, self.thread)

        return self.json_ok()

    @login_required
    @handler('#post_id', 'edit', method='get')
    def edit_post(self):

        if self.account.is_fast:
            return self.template('error.html', {'msg': u'Вы не закончили регистрацию, чтобы редактировать сообщения',
                                                'error_code': 'forum.edit_thread.fast_account'})

        if not (self.can_change_posts() or self.post.author == self.account):
            return self.template('error.html', {'msg': u'У Вас нет прав для редактирования сообщения',
                                                'error_code': 'forum.edit_thread.no_permissions'})

        return self.template('forum/edit_post.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'thread': self.thread,
                              'post': self.post,
                              'new_post_form': NewPostForm(initial={'text': self.post.text})} )

    @login_required
    @handler('#post_id', 'update', method='post')
    def update_post(self):

        if self.account.is_fast:
            return self.json_error('forum.update_post.fast_account', u'Вы не закончили регистрацию и не можете работать с форумом')

        if not (self.can_change_posts() or self.post.author == self.account):
            return self.json_error('forum.update_post.no_permissions', u'У Вас нет прав для редактирования сообщения')

        edit_post_form = NewPostForm(self.request.POST)

        if not edit_post_form.is_valid():
            return self.json_error('forum.update_post.form_errors', edit_post_form.errors)

        self.post.update(edit_post_form.c.text)

        return self.json_ok()


class ThreadsResource(BaseForumResource):

    @handler('', method='get')
    def index(self, author_id=None, page=1, participant_id=None):
        from accounts.prototypes import AccountPrototype

        threads_query = Thread.objects.all().order_by('-updated_at')

        is_filtering = False
        author_account = None
        participant_account = None

        if author_id is not None:
            author_id = int(author_id)
            author_account = AccountPrototype.get_by_id(author_id)
            if author_account:
                threads_query = threads_query.filter(author_id=author_account.id)
                is_filtering = True
            else:
                threads_query = Thread.objects.none()

        if participant_id is not None:
            participant_id = int(participant_id)
            participant_account = AccountPrototype.get_by_id(participant_id)
            if participant_account:
                threads_query = threads_query.filter(post__author__id=participant_account.id).distinct()
                is_filtering = True
            else:
                threads_query = Thread.objects.none()

        url_builder = UrlBuilder(reverse('forum:threads:'), arguments={'author_id': author_id,
                                                                       'participant_id': participant_id,
                                                                       'page': page})

        page = int(page) - 1

        paginator = Paginator(page, threads_query.count(), forum_settings.THREADS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        thread_from, thread_to = paginator.page_borders(page)

        threads = list(ThreadPrototype(thread_model) for thread_model in threads_query.select_related().order_by('-updated_at')[thread_from:thread_to])

        return self.template('forum/threads_list.html',
                             {'is_filtering': is_filtering,
                              'pages_count': range(paginator.pages_count),
                              'current_page_number': page,
                              'author_account': author_account,
                              'participant_account': participant_account,
                              'paginator': paginator,
                              'threads': threads} )


    @login_required
    @handler('new', method='get')
    def new_thread(self, subcategory_id):

        subcategory = SubCategoryPrototype.get_by_id(subcategory_id)

        if subcategory is None:
            return self.auto_error('forum.threads.new.wrong_category_id', u'Категория не найдена', status_code=404)

        if self.account.is_fast:
            return self.template('error.html', {'msg': u'Вы не закончили регистрацию и не можете писать на форуме',
                                                'error_code': 'forum.new_thread.fast_account'})

        if not self.can_create_thread(subcategory):
            return self.template('error.html', {'msg': u'Вы не можете создавать темы в данном разделе',
                                                'error_code': 'forum.new_thread.no_permissions'})

        return self.template('forum/new_thread.html',
                             {'category': subcategory.category,
                              'subcategory': subcategory,
                              'new_thread_form': NewThreadForm()} )

    @login_required
    @handler('create', method='post')
    def create_thread(self, subcategory_id):

        subcategory = SubCategoryPrototype.get_by_id(subcategory_id)

        if subcategory is None:
            return self.auto_error('forum.threads.create.wrong_category_id', u'Категория не найдена', status_code=404)

        if self.account.is_fast:
            return self.json_error('forum.create_thread.fast_account', u'Вы не закончили регистрацию и не можете писать на форуме')

        if not self.can_create_thread(subcategory):
            return self.json_error('forum.create_thread.no_permissions', u'Вы не можете создавать темы в данном разделе')

        new_thread_form = NewThreadForm(self.request.POST)

        if not new_thread_form.is_valid():
            return self.json_error('forum.create_thread.form_errors', new_thread_form.errors)

        thread = ThreadPrototype.create(subcategory,
                                        caption=new_thread_form.c.caption,
                                        author=self.account,
                                        text=new_thread_form.c.text)

        return self.json_ok(data={'thread_url': reverse('forum:threads:show', args=[thread.id]),
                                  'thread_id': thread.id})

    @login_required
    @handler('#thread_id', 'delete', method='post')
    def delete_thread(self):

        if self.account.is_fast:
            return self.json_error('forum.delete_thread.fast_account', u'Вы не закончили регистрацию и не можете работать с форумом')

        if not self.can_delete_thread(self.thread):
            return self.json_error('forum.delete_thread.no_permissions', u'У Вас нет прав для удаления темы')

        self.thread.delete()

        return self.json_ok()

    @login_required
    @handler('#thread_id', 'update', method='post')
    def update_thread(self):

        if self.account.is_fast:
            return self.json_error('forum.update_thread.fast_account', u'Вы не закончили регистрацию и не можете работать с форумом')

        if not self.can_change_thread(self.thread):
            return self.json_error('forum.update_thread.no_permissions', u'У Вас нет прав для редактирования темы')

        edit_thread_form = EditThreadForm(subcategories=[SubCategoryPrototype(subcategory_model) for subcategory_model in SubCategory.objects.all()],
                                          data=self.request.POST )

        if not edit_thread_form.is_valid():
            return self.json_error('forum.update_thread.form_errors', edit_thread_form.errors)

        try:
            new_subcategory_id = int(edit_thread_form.c.subcategory)
        except ValueError:
            new_subcategory_id = None

        if new_subcategory_id is not None and self.thread.subcategory.id != edit_thread_form.c.subcategory:
            if not self.can_change_thread_category():
                return self.json_error('forum.update_thread.no_permissions_to_change_subcategory', u'У вас нет прав для переноса темы в другой раздел')

        self.thread.update(caption=edit_thread_form.c.caption, new_subcategory_id=new_subcategory_id)

        return self.json_ok()

    @login_required
    @handler('#thread_id', 'edit', method='get')
    def edit_thread(self):

        if self.account.is_fast:
            return self.template('error.html', {'msg': u'Вы не закончили регистрацию и не можете работать с форумом',
                                                'error_code': 'forum.edit_thread.fast_account'})

        if not self.can_change_thread(self.thread):
            return self.template('error.html', {'msg': u'Вы не можете редактировать эту тему',
                                                'error_code': 'forum.edit_thread.no_permissions'})

        return self.template('forum/edit_thread.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'thread': self.thread,
                              'edit_thread_form': EditThreadForm(subcategories=[SubCategoryPrototype(subcategory_model) for subcategory_model in SubCategory.objects.all()],
                                                                 initial={'subcategory': self.subcategory.id,
                                                                          'caption': self.thread.caption}),
                              'can_change_thread_category': self.can_change_thread_category()} )


    @handler('#thread_id', name='show', method='get')
    def get_thread(self, page=1):

        url_builder = UrlBuilder(reverse('forum:threads:show', args=[self.thread.id]),
                                 arguments={'page': page})

        page = int(page) - 1

        paginator = Paginator(page, self.thread.posts_count, forum_settings.POSTS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        post_from, post_to = paginator.page_borders(page)

        posts = [PostPrototype(post_model) for post_model in Post.objects.filter(thread=self.thread.model).order_by('created_at')[post_from:post_to]]

        pages_on_page_slice = posts
        if post_from == 0:
            pages_on_page_slice = pages_on_page_slice[1:]
        has_post_on_page = any([post.author == self.account for post in pages_on_page_slice])

        return self.template('forum/thread.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'thread': self.thread,
                              'new_post_form': NewPostForm(),
                              'posts': posts,
                              'paginator': paginator,
                              'start_posts_from': page * forum_settings.POSTS_ON_PAGE,
                              'can_delete_thread': self.can_delete_thread(self.thread),
                              'can_change_thread': self.can_change_thread(self.thread),
                              'can_delete_posts': self.can_delete_posts(self.thread),
                              'can_change_posts': self.can_change_posts(),
                              'has_post_on_page': has_post_on_page,
                              'current_page_number': page} )



class ForumResource(BaseForumResource):

    @handler('', method='get')
    def index(self):
        categories = list(CategoryPrototype(category_model) for category_model in Category.objects.all().order_by('order', 'id'))

        subcategories=[SubCategoryPrototype(subcategory_model) for subcategory_model in SubCategory.objects.all().order_by('order', 'id')]

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


    @handler('categories', '#subcategory', name='subcategory', method='get')
    def get_subcategory(self, page=1):

        threads_query = Thread.objects.filter(subcategory=self.subcategory.model)

        url_builder = UrlBuilder(reverse('forum:subcategory', args=[self.subcategory.slug]), arguments={'page': page})

        page = int(page) - 1

        paginator = Paginator(page, threads_query.count(), forum_settings.THREADS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        thread_from, thread_to = paginator.page_borders(page)

        threads = list(ThreadPrototype(thread_model) for thread_model in threads_query.select_related().order_by('-updated_at')[thread_from:thread_to])

        return self.template('forum/subcategory.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'can_create_thread': self.can_create_thread(self.subcategory),
                              'paginator': paginator,
                              'threads': threads} )
