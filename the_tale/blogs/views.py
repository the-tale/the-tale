# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views.resources import handler, validator
from dext.utils.decorators import nested_commit_on_success
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.decorators import login_required
from common.utils.enum import create_enum

from accounts.prototypes import AccountPrototype

from blogs.prototypes import PostPrototype, VotePrototype
from blogs.models import Post, Vote, POST_STATE
from blogs.conf import blogs_settings
from blogs.forms import PostForm


ORDER_BY = create_enum('ORDER_BY', (('ALPHABET', 'alphabet', u'по алфавиту'),
                                    ('CREATED_AT', 'created_at', u'по дате создания'),
                                    ('RATING', 'rating', u'по рейтингу'),))

class PostResource(Resource):

    def initialize(self, post_id=None, *args, **kwargs):
        super(PostResource, self).initialize(*args, **kwargs)

        if post_id is not None:
            self.post_id = int(post_id)
            self.post = PostPrototype.get_by_id(self.post_id)
            if self.post is None:
                return self.auto_error('blogs.posts.wrong_post_id', u'Запись не найдена', status_code=404)
        else:
            self.post_id = None
            self.post = None

        self.can_moderate_post = self.user.has_perm('blogs.moderate_post')

    @validator(code='blogs.posts.fast_account', message=u'Для выполнения этого действия необходимо завершить регистрацию')
    def validate_fast_account_restrictions(self, *args, **kwargs): return not self.account.is_fast

    @validator(code='blogs.posts.no_edit_rights', message=u'Вы не можете редактировать это произведение')
    def validate_edit_rights(self, *args, **kwargs): return self.account.id == self.post.author.id or self.can_moderate_post

    @validator(code='blogs.posts.moderator_rights_required', message=u'Вы не являетесь модератором')
    def validate_moderator_rights(self, *args, **kwargs): return self.can_moderate_post

    @validator(code='blogs.posts.post_declined', message=u'Произведение не прошло проверку модератора и отклонено')
    def validate_declined_state(self, *args, **kwargs): return not self.post.state.is_declined


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

        if self.account:
            votes = dict( (vote.post_id, VotePrototype(vote)) for vote in Vote.objects.filter(post_id__in=[post.id for post in posts], voter=self.account.model) )

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
    @validate_fast_account_restrictions()
    @handler('new', method='get')
    def new(self):
        return self.template('blogs/new.html', {'form': PostForm()})

    @login_required
    @validate_fast_account_restrictions()
    @handler('create', method='post')
    def create(self):

        form = PostForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('blogs.posts.create.form_errors', form.errors)

        post = PostPrototype.create(author=self.account, caption=form.c.caption, text=form.c.text)
        return self.json_ok(data={'next_url': reverse('blogs:posts:show', args=[post.id])})

    @validate_declined_state()
    @handler('#post_id', name='show', method='get')
    def show(self):
        return self.template('blogs/show.html', {'post': self.post,
                                                 'vote': None if not self.account else VotePrototype.get_for(self.account, self.post)})

    @login_required
    @validate_fast_account_restrictions()
    @validate_edit_rights()
    @validate_declined_state()
    @handler('#post_id', 'edit', method='get')
    def edit(self):
        form = PostForm(initial={'caption': self.post.caption,
                                 'text': self.post.text})
        return self.template('blogs/edit.html', {'post': self.post,
                                                 'form': form} )

    @login_required
    @validate_fast_account_restrictions()
    @validate_edit_rights()
    @validate_declined_state()
    @nested_commit_on_success
    @handler('#post_id', 'update', method='post')
    def update(self):
        form = PostForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('blogs.posts.update.form_errors', form.errors)

        self.post.caption = form.c.caption
        self.post.text = form.c.text
        self.post.state = POST_STATE.NOT_MODERATED

        if self.can_moderate_post:
            self.post.moderator_id = self.account.id

        self.post.save()

        self.post.forum_thread.caption = form.c.caption
        self.post.forum_thread.save()

        return self.json_ok()

    @login_required
    @validate_fast_account_restrictions()
    @validate_moderator_rights()
    @handler('#post_id', 'accept', method='post')
    def accept(self):
        self.post.state = POST_STATE.ACCEPTED
        self.post.moderator_id = self.account.id
        self.post.save()

        return self.json_ok()

    @login_required
    @validate_fast_account_restrictions()
    @validate_moderator_rights()
    @handler('#post_id', 'decline', method='post')
    def decline(self):
        self.post.state = POST_STATE.DECLINED
        self.post.moderator_id = self.account.id
        self.post.save()

        return self.json_ok()

    @login_required
    @validate_fast_account_restrictions()
    @nested_commit_on_success
    @handler('#post_id', 'vote', method='post')
    def vote(self, value):

        value = {'for': True, 'against': False}.get(value)

        if value is None:
            return self.json_error('blogs.posts.vote.wrong_value', u'Неверно указан тип голоса')

        VotePrototype.create_or_update(self.post, self.account, value)

        self.post.recalculate_votes()
        self.post.save()

        return self.json_ok()
