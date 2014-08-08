# coding: utf-8

from django.core.urlresolvers import reverse
from django.db import transaction

from dext.views import handler, validator, validate_argument
from dext.common.utils.urls import UrlBuilder

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils.decorators import login_required
from the_tale.common.utils.enum import create_enum

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.views import validate_ban_forum

from the_tale.blogs.prototypes import PostPrototype, VotePrototype
from the_tale.blogs.models import Post, Vote
from the_tale.blogs.conf import blogs_settings
from the_tale.blogs.forms import PostForm
from the_tale.blogs.relations import POST_STATE


ORDER_BY = create_enum('ORDER_BY', (('ALPHABET', 'alphabet', u'по алфавиту'),
                                    ('CREATED_AT', 'created_at', u'по дате создания'),
                                    ('RATING', 'rating', u'по рейтингу'),))

class PostResource(Resource):

    @validate_argument('post', PostPrototype.get_by_id, 'blogs.posts', u'Запись не найдена')
    def initialize(self, post=None, *args, **kwargs):
        super(PostResource, self).initialize(*args, **kwargs)
        self.post = post
        self.can_moderate_post = self.account.has_perm('blogs.moderate_post')

    @validator(code='blogs.posts.fast_account', message=u'Для выполнения этого действия необходимо завершить регистрацию')
    def validate_fast_account_restrictions(self, *args, **kwargs):
        return self.account.is_authenticated() and not self.account.is_fast

    @validator(code='blogs.posts.no_edit_rights', message=u'Вы не можете редактировать это произведение')
    def validate_edit_rights(self, *args, **kwargs): return self.account.id == self.post.author.id or self.can_moderate_post

    @validator(code='blogs.posts.moderator_rights_required', message=u'Вы не являетесь модератором')
    def validate_moderator_rights(self, *args, **kwargs): return self.can_moderate_post

    @validator(code='blogs.posts.post_declined', message=u'Произведение не прошло проверку модератора и отклонено')
    def validate_declined_state(self, *args, **kwargs): return not self.post.state.is_DECLINED


    @handler('', method='get')
    def index(self, page=1, author_id=None, order_by=ORDER_BY.CREATED_AT):

        posts_query = Post.objects.filter(state__in=[POST_STATE.NOT_MODERATED, POST_STATE.ACCEPTED])

        is_filtering = False

        author_account = None

        if author_id is not None:
            author_id = int(author_id)
            author_account = AccountPrototype.get_by_id(author_id)
            if author_account:
                posts_query = posts_query.filter(author_id=author_account.id)
                is_filtering = True
            else:
                posts_query = Post.objects.none()

        if order_by is not None:
            if order_by == ORDER_BY.ALPHABET:
                posts_query = posts_query.order_by('caption')
            elif order_by == ORDER_BY.CREATED_AT:
                posts_query = posts_query.order_by('-created_at')
            elif order_by == ORDER_BY.RATING:
                posts_query = posts_query.order_by('-votes')
            else:
                order_by = ORDER_BY.CREATED_AT
                posts_query = posts_query.order_by('-created_at')

        url_builder = UrlBuilder(reverse('blogs:posts:'), arguments={'author_id': author_id,
                                                                     'order_by': order_by})

        posts_count = posts_query.count()

        page = int(page) - 1

        paginator = Paginator(page, posts_count, blogs_settings.POSTS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        post_from, post_to = paginator.page_borders(page)

        posts = [ PostPrototype(post) for post in posts_query.select_related()[post_from:post_to]]

        votes = {}

        if self.account.is_authenticated():
            votes = dict( (vote.post_id, VotePrototype(vote)) for vote in Vote.objects.filter(post_id__in=[post.id for post in posts], voter=self.account._model) )

        return self.template('blogs/index.html',
                             {'posts': posts,
                              'votes': votes,
                              'order_by': order_by,
                              'ORDER_BY': ORDER_BY,
                              'is_filtering': is_filtering,
                              'current_page_number': page,
                              'author_account': author_account,
                              'paginator': paginator,
                              'url_builder': url_builder} )

    @login_required
    @validate_ban_forum()
    @validate_fast_account_restrictions()
    @handler('new', method='get')
    def new(self):
        return self.template('blogs/new.html', {'form': PostForm()})

    @login_required
    @validate_ban_forum()
    @validate_fast_account_restrictions()
    @handler('create', method='post')
    def create(self):

        form = PostForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('blogs.posts.create.form_errors', form.errors)

        post = PostPrototype.create(author=self.account, caption=form.c.caption, text=form.c.text)
        return self.json_ok(data={'next_url': reverse('blogs:posts:show', args=[post.id])})

    @validate_declined_state()
    @handler('#post', name='show', method='get')
    def show(self):
        from the_tale.forum.views import ThreadPageData

        thread_data = ThreadPageData()
        thread_data.initialize(account=self.account, thread=self.post.forum_thread, page=1, inline=True)

        return self.template('blogs/show.html', {'post': self.post,
                                                 'thread_data': thread_data,
                                                 'vote': None if not self.account.is_authenticated() else VotePrototype.get_for(self.account, self.post)})

    @login_required
    @validate_ban_forum()
    @validate_fast_account_restrictions()
    @validate_edit_rights()
    @validate_declined_state()
    @handler('#post', 'edit', method='get')
    def edit(self):
        form = PostForm(initial={'caption': self.post.caption,
                                 'text': self.post.text})
        return self.template('blogs/edit.html', {'post': self.post,
                                                 'form': form} )

    @login_required
    @validate_ban_forum()
    @validate_fast_account_restrictions()
    @validate_edit_rights()
    @validate_declined_state()
    @transaction.atomic
    @handler('#post', 'update', method='post')
    def update(self):
        form = PostForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('blogs.posts.update.form_errors', form.errors)

        self.post.caption = form.c.caption
        self.post.text = form.c.text
        # self.post.state = POST_STATE.NOT_MODERATED

        if self.can_moderate_post:
            self.post.moderator_id = self.account.id

        self.post.save()

        self.post.forum_thread.caption = form.c.caption
        self.post.forum_thread.save()

        return self.json_ok()

    @login_required
    @validate_fast_account_restrictions()
    @validate_moderator_rights()
    @handler('#post', 'accept', method='post')
    def accept(self):
        self.post.accept(self.account)
        return self.json_ok()

    @login_required
    @validate_fast_account_restrictions()
    @validate_moderator_rights()
    @handler('#post', 'decline', method='post')
    def decline(self):
        self.post.decline(self.account)
        return self.json_ok()

    @login_required
    @validate_fast_account_restrictions()
    @transaction.atomic
    @handler('#post', 'vote', method='post')
    def vote(self):

        VotePrototype.create_if_not_exists(self.post, self.account)

        self.post.recalculate_votes()
        self.post.save()

        return self.json_ok()

    @login_required
    @validate_fast_account_restrictions()
    @transaction.atomic
    @handler('#post', 'unvote', method='post')
    def unvote(self):

        VotePrototype.remove_if_exists(self.post, self.account)

        self.post.recalculate_votes()
        self.post.save()

        return self.json_ok()
