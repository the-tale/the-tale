# coding: utf-8
import datetime

from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed

from dext.views import handler, validate_argument
from dext.common.utils.urls import UrlBuilder, url

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils.decorators import login_required

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.views import validate_fast_account, validate_ban_forum

from the_tale.game.heroes import logic as heroes_logic

from the_tale.forum.models import Category, SubCategory, Thread, Post
from the_tale.forum import forms
from the_tale.forum.conf import forum_settings
from the_tale.forum.read_state import ReadState
from the_tale.forum.prototypes import ( CategoryPrototype,
                               SubCategoryPrototype,
                               ThreadPrototype,
                               PostPrototype,
                               SubscriptionPrototype,
                               ThreadReadInfoPrototype,
                               SubCategoryReadInfoPrototype)


def can_delete_thread(account):
    return account.has_perm('forum.moderate_thread')

def can_change_thread(account, thread):
    return (account.id == thread.author.id and not thread.technical) or account.has_perm('forum.moderate_thread')

def can_change_thread_category(account):
    return account.has_perm('forum.moderate_thread')

def can_delete_posts(account, thread):
    return account.id == thread.author.id or account.has_perm('forum.moderate_post')

def can_create_thread(account, subcategory):
    if not subcategory.closed:
        return account.is_authenticated() and not account.is_fast

    return account.has_perm('forum.moderate_thread')

def can_change_posts(account):
    return account.has_perm('forum.moderate_post')

def is_moderator(account):
    return account._model.groups.filter(name=forum_settings.MODERATOR_GROUP_NAME).exists()


class BaseForumResource(Resource):

    @validate_argument('category', CategoryPrototype.get_by_slug, 'forum', u'категория не найдена')
    @validate_argument('subcategory', SubCategoryPrototype.get_by_id, 'forum', u'подкатегория не найдена')
    @validate_argument('thread', ThreadPrototype.get_by_id, 'forum', u'обсуждение не найдено')
    @validate_argument('post', PostPrototype.get_by_id, 'forum', u'сообщение не найдено')
    def initialize(self, category=None, subcategory=None, thread=None, post=None, *args, **kwargs):
        super(BaseForumResource, self).initialize(*args, **kwargs)

        self.post = post
        self.thread = self.post.thread if self.post and thread is None else thread
        self.subcategory = self.thread.subcategory if self.thread and subcategory is None else subcategory
        self.category = self.subcategory.category if self.subcategory and category is None else category

        # TODO: check consistency

        if self.subcategory and self.subcategory.is_restricted_for(self.account):
            return self.auto_error('forum.subcategory_access_restricted', u'Вы не можете работать с материалами из этого раздела')



class PostsResource(BaseForumResource):

    @login_required
    @validate_ban_forum()
    @validate_fast_account()
    @handler('#post', 'delete', method='post')
    def delete_post(self):

        if not (can_delete_posts(self.account, self.thread) or self.post.author == self.account):
            return self.json_error('forum.delete_post.no_permissions', u'У Вас нет прав для удаления сообщения')

        if Post.objects.filter(thread=self.thread._model, created_at__lt=self.post.created_at).count() == 0:
            return self.json_error('forum.delete_post.remove_first_post', u'Вы не можете удалить первое сообщение в теме')

        if self.post.author.id != self.account.id and is_moderator(self.post.author):
            return self.auto_error('forum.delete_post.remove_moderator_post', u'Вы не можете удалить сообщение модератора')

        self.post.delete(self.account)

        return self.json_ok()


    def get_post_url(self, post):
        thread_posts_ids = list(PostPrototype._db_filter(thread_id=post.thread_id).order_by('created_at').values_list('id', flat=True))
        page = Paginator.get_page_numbers(thread_posts_ids.index(post.id)+1, forum_settings.POSTS_ON_PAGE)
        return url('forum:threads:show', post.thread_id, page=page) + ('#m%d' % post.id)

    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#post', 'edit', method='get')
    def edit_post(self):

        if not (can_change_posts(self.account) or self.post.author == self.account):
            return self.template('error.html', {'error_message': u'У Вас нет прав для редактирования сообщения',
                                                'error_code': 'forum.edit_thread.no_permissions'})

        return self.template('forum/edit_post.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'thread': self.thread,
                              'post': self.post,
                              'post_url': self.get_post_url(self.post),
                              'new_post_form': forms.NewPostForm(initial={'text': self.post.text})} )

    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#post', 'update', method='post')
    def update_post(self):

        if not (can_change_posts(self.account) or self.post.author == self.account):
            return self.json_error('forum.update_post.no_permissions', u'У Вас нет прав для редактирования сообщения')

        edit_post_form = forms.NewPostForm(self.request.POST)

        if not edit_post_form.is_valid():
            return self.json_error('forum.update_post.form_errors', edit_post_form.errors)

        self.post.update(edit_post_form.c.text)

        return self.json_ok(data={'next_url': self.get_post_url(self.post)})


class ThreadsResource(BaseForumResource):

    @login_required
    @validate_fast_account()
    @handler('#thread', 'subscribe', method='post')
    def subscribe(self):
        SubscriptionPrototype.create(self.account, thread=self.thread)
        return self.json_ok()

    @login_required
    @validate_fast_account()
    @handler('#thread', 'unsubscribe', method='post')
    def unsubscribe(self):
        subscription = SubscriptionPrototype.get_for(self.account, thread=self.thread)

        if subscription:
            subscription.remove()

        return self.json_ok()


    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#thread', 'create-post', method='post')
    def create_post(self):

        new_post_delay = PostPrototype.get_new_post_delay(self.account)

        if new_post_delay > 0:
            error_message = (u'Создавать новые сообщения можно не чаще раза в %d секунд. <br/>Задержка увеличивается для игроков, только начинающих общаться на форуме.<br/> Вы сможете создать новое сообщение через %d сек.' %
                             ( forum_settings.POST_DELAY,
                               int(new_post_delay)))
            return self.json_error('forum.create_post.delay', error_message)


        new_post_form = forms.NewPostForm(self.request.POST)

        if not new_post_form.is_valid():
            return self.json_error('forum.create_post.form_errors', new_post_form.errors)

        post = PostPrototype.create(self.thread, self.account, new_post_form.c.text)

        if self.account.is_authenticated():
            ThreadReadInfoPrototype.read_thread(self.thread, self.account)

        return self.json_ok(data={'next_url': url('forum:threads:show', self.thread.id, page=self.thread.paginator.pages_count) + ('#m%d' % post.id)})


    @validate_argument('author', AccountPrototype.get_by_id, 'forum.threads.index', u'автор не найден')
    @validate_argument('participant', AccountPrototype.get_by_id, 'forum.threads.index', u'участник не найден')
    @validate_argument('page', int, 'forum.threads.index', u'неверный номер страницы')
    @handler('', method='get')
    def index(self, author=None, page=1, participant=None):

        threads_query = ThreadPrototype.threads_visible_to_account_query(self.account if self.account.is_authenticated() else None).order_by('-updated_at')

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
                              'threads': threads,
                              'read_state': ReadState(account=self.account)} )


    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#thread', 'delete', method='post')
    def delete_thread(self):

        if not can_delete_thread(self.account):
            return self.json_error('forum.delete_thread.no_permissions', u'У Вас нет прав для удаления темы')

        self.thread.delete()

        return self.json_ok()

    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#thread', 'update', method='post')
    def update_thread(self):

        if not can_change_thread(self.account, self.thread):
            return self.json_error('forum.update_thread.no_permissions', u'У Вас нет прав для редактирования темы')

        account_is_moderator = is_moderator(self.account)

        EditThreadForm = forms.EditThreadModeratorForm if account_is_moderator else forms.EditThreadForm

        edit_thread_form = EditThreadForm(subcategories=[SubCategoryPrototype(subcategory_model) for subcategory_model in SubCategory.objects.all()],
                                          data=self.request.POST )

        if not edit_thread_form.is_valid():
            return self.json_error('forum.update_thread.form_errors', edit_thread_form.errors)

        try:
            new_subcategory_id = int(edit_thread_form.c.subcategory)
        except ValueError:
            new_subcategory_id = None

        if new_subcategory_id is not None and self.thread.subcategory.id != edit_thread_form.c.subcategory:
            if not can_change_thread_category(self.account):
                return self.json_error('forum.update_thread.no_permissions_to_change_subcategory', u'У вас нет прав для переноса темы в другой раздел')

        if account_is_moderator:
            self.thread.update(caption=edit_thread_form.c.caption, new_subcategory_id=new_subcategory_id, important=edit_thread_form.c.important)
        else:
            self.thread.update(caption=edit_thread_form.c.caption, new_subcategory_id=new_subcategory_id, important=self.thread.important)

        return self.json_ok()

    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#thread', 'edit', method='get')
    def edit_thread(self):

        if not can_change_thread(self.account, self.thread):
            return self.template('error.html', {'error_message': u'Вы не можете редактировать эту тему',
                                                'error_code': 'forum.edit_thread.no_permissions'})

        account_is_moderator = is_moderator(self.account)

        if account_is_moderator:
            form = forms.EditThreadModeratorForm(subcategories=[SubCategoryPrototype(subcategory_model) for subcategory_model in SubCategory.objects.all()],
                                                 initial={'subcategory': self.subcategory.id,
                                                          'caption': self.thread.caption,
                                                          'important': self.thread.important})
        else:
            form = forms.EditThreadForm(subcategories=[SubCategoryPrototype(subcategory_model) for subcategory_model in SubCategory.objects.all()],
                                        initial={'subcategory': self.subcategory.id,
                                                 'caption': self.thread.caption})

        return self.template('forum/edit_thread.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'thread': self.thread,
                              'edit_thread_form': form,
                              'is_moderator': account_is_moderator,
                              'can_change_thread_category': can_change_thread_category(self.account)} )


    @validate_argument('page', int, 'forum.threads.show', u'неверный номер страницы')
    @handler('#thread', name='show', method='get')
    def get_thread(self, page=1):

        thread_data = ThreadPageData()

        if not thread_data.initialize(account=self.account, thread=self.thread, page=page):
            return self.redirect(thread_data.paginator.last_page_url, permanent=False)

        if self.account.is_authenticated():
            ThreadReadInfoPrototype.read_thread(self.thread, self.account)

        return self.template('forum/thread.html',
                             {'category': self.category,
                              'thread': self.thread,
                              'thread_data': thread_data} )


class ThreadPageData(object):

    def __init__(self):
        pass

    def initialize(self, account, thread, page, inline=False):

        self.account = account
        self.thread = thread

        url_builder = UrlBuilder(reverse('forum:threads:show', args=[self.thread.id]),
                                 arguments={'page': page})

        page -= 1

        self.paginator = Paginator(page, thread.posts_count+1, forum_settings.POSTS_ON_PAGE, url_builder)

        if self.paginator.wrong_page_number:
            return False

        post_from, post_to = self.paginator.page_borders(page)
        self.post_from = post_from

        self.posts = [PostPrototype(post_model) for post_model in Post.objects.filter(thread=self.thread._model).order_by('created_at')[post_from:post_to]]

        self.authors = {author.id:author for author in  AccountPrototype.get_list_by_id([post.author_id for post in self.posts])}

        self.game_objects = {game_object.account_id:game_object
                             for game_object in  heroes_logic.load_heroes_by_account_ids([post.author_id for post in self.posts])}

        pages_on_page_slice = self.posts
        if post_from == 0:
            pages_on_page_slice = pages_on_page_slice[1:]

        self.has_post_on_page = any([post.author.id == self.account.id for post in pages_on_page_slice])
        self.new_post_form = forms.NewPostForm()
        self.start_posts_from = page * forum_settings.POSTS_ON_PAGE

        self.inline = inline

        self.can_delete_posts = can_delete_posts(self.account, self.thread)
        self.can_change_posts = can_change_posts(self.account)
        self.can_delete_thread = not self.inline and can_delete_thread(self.account)
        self.can_change_thread = not self.inline and can_change_thread(self.account, self.thread)

        self.ignore_first_post = (self.inline and self.paginator.current_page_number==0)
        self.can_post = self.account.is_authenticated() and not self.account.is_fast

        self.no_posts = (len(self.posts) == 0) or (self.ignore_first_post and len(self.posts) == 1)
        self.can_subscribe = self.account.is_authenticated() and not self.account.is_fast

        self.has_subscription = SubscriptionPrototype.has_subscription(self.account, self.thread)

        return True

class SubscriptionsResource(Resource):

    @login_required
    @validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(SubscriptionsResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def subscriptions(self):
        return self.template('forum/subscriptions.html',
                             {'threads': SubscriptionPrototype.get_threads_for_account(self.account),
                              'subcategories': SubscriptionPrototype.get_subcategories_for_account(self.account)} )




class SubCategoryResource(BaseForumResource):

    @login_required
    @validate_fast_account()
    @handler('#subcategory', 'subscribe', method='post')
    def subscribe(self):
        SubscriptionPrototype.create(self.account, subcategory=self.subcategory)
        return self.json_ok()

    @login_required
    @validate_fast_account()
    @handler('#subcategory', 'unsubscribe', method='post')
    def unsubscribe(self):
        subscription = SubscriptionPrototype.get_for(self.account, subcategory=self.subcategory)

        if subscription:
            subscription.remove()

        return self.json_ok()

    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#subcategory', 'new-thread', method='get')
    def new_thread(self):

        if not can_create_thread(self.account, self.subcategory):
            return self.template('error.html', {'error_message': u'Вы не можете создавать темы в данном разделе',
                                                'error_code': 'forum.new_thread.no_permissions'})

        return self.template('forum/new_thread.html',
                             {'category': self.subcategory.category,
                              'subcategory': self.subcategory,
                              'new_thread_form': forms.NewThreadForm()} )

    @login_required
    @validate_fast_account()
    @validate_ban_forum()
    @handler('#subcategory', 'create-thread', method='post')
    def create_thread(self):

        if not can_create_thread(self.account, self.subcategory):
            return self.json_error('forum.create_thread.no_permissions', u'Вы не можете создавать темы в данном разделе')

        new_thread_delay = ThreadPrototype.get_new_thread_delay(self.account)
        if new_thread_delay > 0:
            error_message = (u'Создавать новые обсуждения можно не чаще раза в %d минут.<br/> Вы сможете создать новое обсуждение через %d сек.' %
                             ( int(forum_settings.THREAD_DELAY / 60),
                               int(new_thread_delay)))
            return self.json_error('forum.create_thread.delay', error_message)

        new_thread_form = forms.NewThreadForm(self.request.POST)

        if not new_thread_form.is_valid():
            return self.json_error('forum.create_thread.form_errors', new_thread_form.errors)

        thread = ThreadPrototype.create(self.subcategory,
                                        caption=new_thread_form.c.caption,
                                        author=self.account,
                                        text=new_thread_form.c.text)

        return self.json_ok(data={'thread_url': reverse('forum:threads:show', args=[thread.id]),
                                  'thread_id': thread.id})

    @validate_argument('page', int, 'forum.subcategories.show', u'неверный номер страницы')
    @handler('#subcategory', name='show', method='get')
    def get_subcategory(self, page=1):

        threads_query = Thread.objects.filter(subcategory=self.subcategory._model)

        url_builder = UrlBuilder(reverse('forum:subcategories:show', args=[self.subcategory.id]), arguments={'page': page})

        page -= 1

        paginator = Paginator(page, threads_query.count(), forum_settings.THREADS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        thread_from, thread_to = paginator.page_borders(page)

        threads = ThreadPrototype.from_query(threads_query.select_related().order_by('-important', '-updated_at')[thread_from:thread_to])

        important_threads = sorted(filter(lambda t: t.important, threads), key=lambda t: t.caption)
        threads = filter(lambda t: not t.important, threads)

        read_state = ReadState(account=self.account)

        if self.account.is_authenticated():
            SubCategoryReadInfoPrototype.read_subcategory(subcategory=self.subcategory, account=self.account)

        return self.template('forum/subcategory.html',
                             {'category': self.category,
                              'subcategory': self.subcategory,
                              'can_create_thread': can_create_thread(self.account, self.subcategory),
                              'paginator': paginator,
                              'can_subscribe': self.account.is_authenticated() and not self.account.is_fast,
                              'has_subscription': SubscriptionPrototype.has_subscription(self.account, subcategory=self.subcategory),
                              'threads': threads,
                              'important_threads': important_threads,
                              'read_state': read_state } )


class ForumResource(BaseForumResource):

    @handler('', method='get')
    def index(self):
        categories = list(CategoryPrototype(category_model) for category_model in Category.objects.all().order_by('order', 'id'))

        subcategories = SubCategoryPrototype.subcategories_visible_to_account(account=self.account if self.account.is_authenticated() else None)

        forum_structure = []

        read_states = {subcategory.id: ReadState(account=self.account)
                       for subcategory in subcategories}

        for category in categories:
            children = []
            for subcategory in subcategories:
                if subcategory.category_id == category.id:
                    children.append(subcategory)

            forum_structure.append({'category': category,
                                    'subcategories': children})


        return self.template('forum/index.html',
                             {'forum_structure': forum_structure,
                              'read_states': read_states} )

    @login_required
    @handler('categories', '#subcategory', 'read-all-in-subcategory', name='read-all-in-subcategory', method='post')
    def read_all__one(self):
        SubCategoryReadInfoPrototype.read_all_in_subcategory(subcategory=self.subcategory, account=self.account)
        return self.json_ok()

    @login_required
    @handler('categories', 'read-all', name='read-all', method='post')
    def read_all__all(self):
        for subcategory in SubCategoryPrototype.subcategories_visible_to_account(account=self.account):
            SubCategoryReadInfoPrototype.read_all_in_subcategory(subcategory=subcategory, account=self.account)
        return self.json_ok()

    @handler('feed', method='get')
    def feed(self):
        feed = Atom1Feed(u'Сказка: Форум',
                         self.request.build_absolute_uri('/'),
                         u'Новые темы на форуме мморпг «Сказка»',
                         language=u'ru',
                         feed_url=self.request.build_absolute_uri(reverse('forum:feed')))

        threads = [ThreadPrototype(model=thread) for thread in Thread.objects.filter(subcategory__restricted=False).order_by('-created_at')[:forum_settings.FEED_ITEMS_NUMBER]]

        for thread in threads:

            if datetime.datetime.now() - thread.created_at < datetime.timedelta(seconds=forum_settings.FEED_ITEMS_DELAY):
                continue

            post = PostPrototype(model=Post.objects.filter(thread_id=thread.id).order_by('created_at')[0])

            url = self.request.build_absolute_uri(reverse('forum:threads:show', args=[thread.id]))

            feed.add_item(title=thread.caption,
                          link=url,
                          description=post.safe_html,
                          pubdate=thread.created_at,
                          unique_id=url)

        return self.atom(feed.writeString('utf-8'))
