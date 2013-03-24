# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.decorators import login_required

from accounts.prototypes import AccountPrototype

from forum.models import Category, SubCategory, Thread, Post
from forum.forms import NewPostForm, NewThreadForm, EditThreadForm
from forum.conf import forum_settings
from forum.prototypes import CategoryPrototype, SubCategoryPrototype, ThreadPrototype, PostPrototype

class BaseForumResource(Resource):

    @validate_argument('category', CategoryPrototype.get_by_slug, 'forum', u'категория не найдена')
    @validate_argument('subcategory', SubCategoryPrototype.get_by_slug, 'forum', u'подкатегория не найдена')
    @validate_argument('thread', ThreadPrototype.get_by_id, 'forum', u'обсуждение не найдено')
    @validate_argument('post', PostPrototype.get_by_id, 'forum', u'сообщение не найдено')
    def initialize(self, category=None, subcategory=None, thread=None, post=None, *args, **kwargs):
        super(BaseForumResource, self).initialize(*args, **kwargs)

        self.post = post
        self.thread = self.post.thread if self.post and thread is None else thread
        self.subcategory = self.thread.subcategory if self.thread and subcategory is None else subcategory
        self.category = self.subcategory.category if self.subcategory and category is None else category

        # TODO: check consistency


    def can_delete_thread(self, thread):
        return (self.account == thread.author and not thread.subcategory.closed) or self.user.has_perm('forum.moderate_thread')

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

    def is_moderator(self, account):
        return account.user.groups.filter(name=forum_settings.MODERATOR_GROUP_NAME).exists()


class PostsResource(BaseForumResource):

    @login_required
    @validate_argument('thread', ThreadPrototype.get_by_id, 'forum.posts.create', u'обсуждение не найдено')
    @handler('create', method='post')
    def create_post(self, thread):

        if self.account.is_fast:
            return self.json_error('forum.create_post.fast_account', u'Вы не закончили регистрацию и не можете писать на форуме')

        new_post_form = NewPostForm(self.request.POST)

        if not new_post_form.is_valid():
            return self.json_error('forum.create_post.form_errors', new_post_form.errors)

        PostPrototype.create(thread, self.account, new_post_form.c.text)

        return self.json_ok(data={'thread_url': reverse('forum:threads:show', args=[thread.id]) + ('?page=%d' % thread.paginator.pages_count)})

    @login_required
    @handler('#post', 'delete', method='post')
    def delete_post(self):

        if self.account.is_fast:
            return self.json_error('forum.delete_post.fast_account', u'Вы не закончили регистрацию и не можете работать с форумом')

        if not (self.can_delete_posts(self.thread) or self.post.author == self.account):
            return self.json_error('forum.delete_post.no_permissions', u'У Вас нет прав для удаления сообщения')

        if Post.objects.filter(thread=self.thread.model, created_at__lt=self.post.created_at).count() == 0:
            return self.json_error('forum.delete_post.remove_first_post', u'Вы не можете удалить первое сообщение в теме')

        if self.post.author.id != self.account.id and self.is_moderator(self.post.author):
            return self.auto_error('forum.delete_post.remove_moderator_post', u'Вы не можете удалить сообщение модератора')

        self.post.delete(self.account, self.thread)

        return self.json_ok()

    @login_required
    @handler('#post', 'edit', method='get')
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
    @handler('#post', 'update', method='post')
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

    @validate_argument('author', AccountPrototype.get_by_id, 'forum.threads.index', u'автор не найден')
    @validate_argument('participant', AccountPrototype.get_by_id, 'forum.threads.index', u'участник не найден')
    @validate_argument('page', int, 'forum.threads.index', u'неверный номер страницы')
    @handler('', method='get')
    def index(self, author=None, page=1, participant=None):

        threads_query = Thread.objects.all().order_by('-updated_at')

        is_filtering = False

        if author is not None:
            threads_query = threads_query.filter(author_id=author.id)
            is_filtering = True

        if participant is not None:
            threads_query = threads_query.filter(post__author__id=participant.id).distinct()
            is_filtering = True

        url_builder = UrlBuilder(reverse('forum:threads:'), arguments={'author': author.id if author else None,
                                                                       'participant': participant.id if participant else None,
                                                                       'page': page})

        page -= 1

        paginator = Paginator(page, threads_query.count(), forum_settings.THREADS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        thread_from, thread_to = paginator.page_borders(page)

        threads = list(ThreadPrototype(thread_model) for thread_model in threads_query.select_related().order_by('-updated_at')[thread_from:thread_to])

        return self.template('forum/threads_list.html',
                             {'is_filtering': is_filtering,
                              'pages_count': range(paginator.pages_count),
                              'current_page_number': page,
                              'author_account': author,
                              'participant_account': participant,
                              'paginator': paginator,
                              'threads': threads} )


    @login_required
    @validate_argument('subcategory', SubCategoryPrototype.get_by_slug, 'forum', u'подкатегория не найдена')
    @handler('new', method='get')
    def new_thread(self, subcategory):

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
    @validate_argument('subcategory', SubCategoryPrototype.get_by_slug, 'forum', u'подкатегория не найдена')
    @handler('create', method='post')
    def create_thread(self, subcategory):

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
    @handler('#thread', 'delete', method='post')
    def delete_thread(self):

        if self.account.is_fast:
            return self.json_error('forum.delete_thread.fast_account', u'Вы не закончили регистрацию и не можете работать с форумом')

        if not self.can_delete_thread(self.thread):
            return self.json_error('forum.delete_thread.no_permissions', u'У Вас нет прав для удаления темы')

        self.thread.delete()

        return self.json_ok()

    @login_required
    @handler('#thread', 'update', method='post')
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
    @handler('#thread', 'edit', method='get')
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


    @validate_argument('page', int, 'forum.threads.show', u'неверный номер страницы')
    @handler('#thread', name='show', method='get')
    def get_thread(self, page=1):

        url_builder = UrlBuilder(reverse('forum:threads:show', args=[self.thread.id]),
                                 arguments={'page': page})

        page -= 1

        paginator = Paginator(page, self.thread.posts_count+1, forum_settings.POSTS_ON_PAGE, url_builder)

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


    @validate_argument('page', int, 'forum.subcategory.show', u'неверный номер страницы')
    @handler('categories', '#subcategory', name='subcategory', method='get')
    def get_subcategory(self, page=1):

        threads_query = Thread.objects.filter(subcategory=self.subcategory.model)

        url_builder = UrlBuilder(reverse('forum:subcategory', args=[self.subcategory.slug]), arguments={'page': page})

        page -= 1

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
