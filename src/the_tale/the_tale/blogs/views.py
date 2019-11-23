
import smart_imports

smart_imports.all()


ORDER_BY = utils_enum.create_enum('ORDER_BY', (('ALPHABET', 'alphabet', 'по алфавиту'),
                                               ('CREATED_AT', 'created_at', 'по дате создания'),
                                               ('RATING', 'rating', 'по голосам'),
                                               ('MIGHT', 'might', 'по рейтингу'),))


@dext_old_views.validator(code='blogs.posts.fast_account', message='Для выполнения этого действия необходимо завершить регистрацию')
def validate_fast_account_restrictions(resource, *args, **kwargs):
    return resource.account.is_authenticated and not resource.account.is_fast


@dext_old_views.validator(code='blogs.posts.no_edit_rights', message='Вы не можете редактировать это произведение')
def validate_edit_rights(resource, *args, **kwargs): return resource.account.id == resource.post.author.id or resource.can_moderate_post


@dext_old_views.validator(code='blogs.posts.moderator_rights_required', message='Вы не являетесь модератором')
def validate_moderator_rights(resource, *args, **kwargs): return resource.can_moderate_post


@dext_old_views.validator(code='blogs.posts.post_declined', message='Произведение не прошло проверку модератора и отклонено')
def validate_declined_state(resource, *args, **kwargs): return not resource.post.state.is_DECLINED


class PostResource(utils_resources.Resource):

    @dext_old_views.validate_argument('post', prototypes.PostPrototype.get_by_id, 'blogs.posts', 'Запись не найдена')
    def initialize(self, post=None, *args, **kwargs):
        super(PostResource, self).initialize(*args, **kwargs)
        self.post = post
        self.can_moderate_post = self.account.has_perm('blogs.moderate_post')

    @dext_old_views.handler('', method='get')
    def index(self, page=1, author_id=None, order_by=ORDER_BY.CREATED_AT, tag_id=None):

        posts_query = models.Post.objects.filter(state__in=[relations.POST_STATE.NOT_MODERATED, relations.POST_STATE.ACCEPTED])

        is_filtering = False

        author_account = None

        if author_id is not None:

            try:
                author_id = int(author_id)
            except ValueError:
                return self.redirect(django_reverse('blogs:posts:'), permanent=False)

            author_account = accounts_prototypes.AccountPrototype.get_by_id(author_id)
            if author_account:
                posts_query = posts_query.filter(author_id=author_account.id)
                is_filtering = True
            else:
                posts_query = models.Post.objects.none()

        if tag_id is not None:
            posts_query = posts_query.filter(id__in=models.Tagged.objects.filter(tag_id=tag_id).values_list('post_id', flat=True))

        if order_by is not None:
            if order_by == ORDER_BY.ALPHABET:
                posts_query = posts_query.order_by('caption')
            elif order_by == ORDER_BY.CREATED_AT:
                posts_query = posts_query.order_by('-created_at')
            elif order_by == ORDER_BY.RATING:
                posts_query = posts_query.order_by('-votes')
            elif order_by == ORDER_BY.MIGHT:
                posts_query = posts_query.order_by('-rating')
            else:
                order_by = ORDER_BY.CREATED_AT
                posts_query = posts_query.order_by('-created_at')

        url_builder = dext_urls.UrlBuilder(django_reverse('blogs:posts:'), arguments={'author_id': author_id,
                                                                                      'order_by': order_by,
                                                                                      'tag_id': tag_id})

        posts_count = posts_query.count()

        page = int(page) - 1

        paginator = utils_pagination.Paginator(page, posts_count, conf.settings.POSTS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        post_from, post_to = paginator.page_borders(page)

        posts = [prototypes.PostPrototype(post) for post in posts_query.select_related()[post_from:post_to]]

        votes = {}

        if self.account.is_authenticated:
            votes = dict((vote.post_id, prototypes.VotePrototype(vote))
                         for vote in models.Vote.objects.filter(post_id__in=[post.id for post in posts], voter=self.account._model))

        return self.template('blogs/index.html',
                             {'posts': posts,
                              'page_type': 'index',
                              'votes': votes,
                              'FORUM_TAGS_THREAD': conf.settings.FORUM_TAGS_THREAD,
                              'order_by': order_by,
                              'current_tag': models.Tag.objects.get(id=tag_id) if tag_id is not None else None,
                              'ORDER_BY': ORDER_BY,
                              'is_filtering': is_filtering,
                              'current_page_number': page,
                              'author_account': author_account,
                              'paginator': paginator,
                              'url_builder': url_builder})

    @utils_decorators.login_required
    @accounts_views.validate_ban_forum()
    @validate_fast_account_restrictions()
    @dext_old_views.handler('new', method='get')
    def new(self):
        return self.template('blogs/new.html', {'form': forms.PostForm(),
                                                'page_type': 'new', })

    @utils_decorators.login_required
    @accounts_views.validate_ban_forum()
    @validate_fast_account_restrictions()
    @django_transaction.atomic
    @dext_old_views.handler('create', method='post')
    def create(self):

        form = forms.PostForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('blogs.posts.create.form_errors', form.errors)

        post = prototypes.PostPrototype.create(author=self.account,
                                               caption=form.c.caption,
                                               text=form.c.text)

        meta_relations_logic.create_relations_for_objects(meta_relations.IsAbout,
                                                          meta_relations.Post.create_from_object(post),
                                                          form.c.meta_objects)

        logic.sync_technical_tags(post.id)

        return self.json_ok(data={'next_url': django_reverse('blogs:posts:show', args=[post.id])})

    @validate_declined_state()
    @dext_old_views.handler('#post', name='show', method='get')
    def show(self):
        thread_data = forum_views.ThreadPageData()
        thread_data.initialize(account=self.account, thread=self.post.forum_thread, page=1, inline=True)

        is_about_objects = logic.get_objects_post_about(self.post.id)

        is_about_objects.sort(key=lambda obj: (obj.TYPE_CAPTION, obj.caption))

        return self.template('blogs/show.html', {'post': self.post,
                                                 'page_type': 'show',
                                                 'post_meta_object': meta_relations.Post.create_from_object(self.post),
                                                 'is_about_objects': is_about_objects,
                                                 'thread_data': thread_data,
                                                 'tags': logic.get_post_tags(self.post.id),
                                                 'vote': None if not self.account.is_authenticated else prototypes.VotePrototype.get_for(self.account, self.post)})

    @utils_decorators.login_required
    @accounts_views.validate_ban_forum()
    @validate_fast_account_restrictions()
    @validate_edit_rights()
    @validate_declined_state()
    @dext_old_views.handler('#post', 'edit', method='get')
    def edit(self):
        meta_post = meta_relations.Post.create_from_object(self.post)

        meta_uids = meta_relations_logic.get_uids_related_from(relation=meta_relations.IsAbout,
                                                               meta_object=meta_post)

        form = forms.PostForm(initial={'caption': self.post.caption,
                                       'text': self.post.text,
                                       'meta_objects': ' '.join(sorted(meta_uids))})
        return self.template('blogs/edit.html', {'post': self.post,
                                                 'page_type': 'edit',
                                                 'form': form})

    @utils_decorators.login_required
    @accounts_views.validate_ban_forum()
    @validate_fast_account_restrictions()
    @validate_edit_rights()
    @validate_declined_state()
    @django_transaction.atomic
    @dext_old_views.handler('#post', 'update', method='post')
    def update(self):
        form = forms.PostForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('blogs.posts.update.form_errors', form.errors)

        self.post.caption = form.c.caption
        self.post.text = form.c.text

        if self.can_moderate_post:
            self.post.moderator_id = self.account.id

        self.post.save()

        self.post.forum_thread.caption = form.c.caption
        self.post.forum_thread.save()

        meta_relations_logic.remove_relations_from_object(meta_relations.IsAbout,
                                                          meta_relations.Post.create_from_object(self.post))

        meta_relations_logic.create_relations_for_objects(meta_relations.IsAbout,
                                                          meta_relations.Post.create_from_object(self.post),
                                                          form.c.meta_objects)

        logic.sync_technical_tags(self.post.id)

        return self.json_ok()

    @utils_decorators.login_required
    @validate_fast_account_restrictions()
    @validate_moderator_rights()
    @dext_old_views.handler('#post', 'accept', method='post')
    def accept(self):
        self.post.accept(self.account)
        return self.json_ok()

    @utils_decorators.login_required
    @validate_fast_account_restrictions()
    @validate_moderator_rights()
    @dext_old_views.handler('#post', 'decline', method='post')
    def decline(self):
        self.post.decline(self.account)
        return self.json_ok()

    @utils_decorators.login_required
    @validate_fast_account_restrictions()
    @django_transaction.atomic
    @dext_old_views.handler('#post', 'vote', method='post')
    def vote(self):

        prototypes.VotePrototype.create_if_not_exists(self.post, self.account)

        self.post.recalculate_votes()
        self.post.save()

        return self.json_ok()

    @utils_decorators.login_required
    @validate_fast_account_restrictions()
    @django_transaction.atomic
    @dext_old_views.handler('#post', 'unvote', method='post')
    def unvote(self):

        prototypes.VotePrototype.remove_if_exists(self.post, self.account)

        self.post.recalculate_votes()
        self.post.save()

        return self.json_ok()

    @utils_decorators.login_required
    @validate_fast_account_restrictions()
    @validate_moderator_rights()
    @dext_old_views.handler('#post', 'edit-tags', method='get')
    def edit_tags(self):

        tags = logic.get_post_tags(self.post.id)

        return self.template('blogs/edit_tags.html', {'post': self.post,
                                                      'form': forms.TagsForm(initial={'tags': [tag.id for tag in tags]}),
                                                      'page_type': 'edit'})

    @utils_decorators.login_required
    @validate_fast_account_restrictions()
    @validate_moderator_rights()
    @django_transaction.atomic
    @dext_old_views.handler('#post', 'update-tags', method='post')
    def update_tags(self):
        form = forms.TagsForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('blogs.posts.update_tags.form_errors', form.errors)

        logic.sync_tags(self.post.id,
                        expected_tags_ids=form.c.tags,
                        work_tags_ids={tag.id for tag in logic.get_manual_tags()})

        logic.sync_technical_tags(self.post.id)

        return self.json_ok()
