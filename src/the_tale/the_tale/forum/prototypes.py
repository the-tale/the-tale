
import smart_imports

smart_imports.all()


class CategoryPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Category
    _readonly = ('id', 'caption', 'slug', 'order')
    _bidirectional = ()
    _get_by = ('slug', 'id')

    @classmethod
    def create(cls, caption, slug, order):
        model = models.Category.objects.create(caption=caption, slug=slug, order=order)
        return cls(model)


class SubCategoryPrototype(utils_prototypes.BasePrototype):
    _model_class = models.SubCategory
    _readonly = ('id', 'order', 'created_at', 'category_id', 'updated_at', 'threads_count', 'posts_count', 'closed', 'last_thread_created_at', 'restricted', 'description')
    _bidirectional = ('caption',)
    _get_by = ('id', 'uid')

    @utils_decorators.lazy_property
    def category(self): return CategoryPrototype(self._model.category)

    def update_counts(self):
        self._model.threads_count = models.Thread.objects.filter(subcategory=self._model).count()
        self._model.posts_count = PostPrototype._db_filter(thread__subcategory__id=self.id).count() - self.threads_count

    @utils_decorators.lazy_property
    def last_poster(self): return accounts_prototypes.AccountPrototype(self._model.last_poster) if self._model.last_poster else None

    @utils_decorators.lazy_property
    def last_thread(self): return ThreadPrototype(self._model.last_thread) if self._model.last_thread else None

    def get_last_threads(self, limit):
        return ThreadPrototype.from_query(models.Thread.objects.filter(subcategory=self._model).order_by('-updated_at')[:limit])

    def is_restricted_for(self, account):
        if not self.restricted:
            return False
        if not account.is_authenticated:
            return True
        return PermissionPrototype.get_for(account_id=account.id, subcategory_id=self.id) is None

    def update(self):
        self.update_counts()

        try:
            last_post = PostPrototype(model=PostPrototype._db_filter(thread__subcategory__id=self.id, state=relations.POST_STATE.DEFAULT).latest('created_at'))
        except PostPrototype._model_class.DoesNotExist:
            last_post = None

        if last_post is None:
            self._model.last_poster = None
            self._model.last_thread = None
            self._model.updated_at = datetime.datetime.now()
            self._model.last_thread_created_at = None

        else:
            self._model.last_poster = last_post.author._model
            self._model.last_thread = last_post._model.thread
            self._model.updated_at = last_post.updated_at
            self._model.last_thread_created_at = last_post.thread.created_at

        self.save()

    def save(self):
        self._model.save()

    @classmethod
    def create(cls, category, caption, order, closed=False, restricted=False, uid=None):

        model = models.SubCategory.objects.create(category=category._model, caption=caption, order=order, closed=closed, restricted=restricted, uid=uid)

        return cls(model=model)

    @classmethod
    def subcategories_visible_to_account_query(cls, account):
        if account:
            return cls._model_class.objects.filter(django_models.Q(restricted=False) |
                                                   (django_models.Q(restricted=True) & django_models.Q(permission__account_id=account.id)))
        else:
            return cls._model_class.objects.filter(restricted=False)

    @classmethod
    def subcategories_visible_to_account(cls, account):
        return cls.from_query(cls.subcategories_visible_to_account_query(account=account).order_by('order', 'id'))

    @django_transaction.atomic
    def delete(self):
        threads_query = ThreadPrototype._db_filter(subcategory=self._model)

        for thread in ThreadPrototype.from_query(threads_query):
            thread.delete()

        self._model.delete()


class ThreadPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Thread
    _readonly = ('id', 'created_at', 'posts_count', 'updated_at', 'technical', 'subcategory_id', 'important')
    _bidirectional = ('caption', )
    _get_by = ('id', )

    @utils_decorators.lazy_property
    def subcategory(self): return SubCategoryPrototype(self._model.subcategory)

    @utils_decorators.lazy_property
    def author(self): return accounts_prototypes.AccountPrototype(self._model.author) if self._model.author else None

    @utils_decorators.lazy_property
    def last_poster(self): return accounts_prototypes.AccountPrototype(self._model.last_poster) if self._model.last_poster else None

    @property
    def paginator(self):
        url_builder = utils_urls.UrlBuilder(django_reverse('forum:threads:show', args=[self.id]))
        # +1 since first post does not counted
        return utils_pagination.Paginator(1, self.posts_count + 1, conf.settings.POSTS_ON_PAGE, url_builder)

    @classmethod
    def threads_visible_to_account_query(cls, account):

        query = cls._model_class.objects

        if account:
            condition = (django_models.Q(subcategory__restricted=False) |
                         (django_models.Q(subcategory__restricted=True) & django_models.Q(subcategory__permission__account_id=account.id)))

            query = query.filter(condition)
        else:
            query = query.filter(subcategory__restricted=False)

        return query

    @classmethod
    def get_last_threads(cls, account, limit, exclude_subcategories=()):
        query = cls.threads_visible_to_account_query(account=account)

        if exclude_subcategories:
            query = query.exclude(subcategory__uid__in=exclude_subcategories)

        return cls.from_query(query.order_by('-updated_at')[:limit])

    def get_first_post(self):
        return PostPrototype(model=models.Post.objects.filter(thread=self._model).order_by('created_at')[0])

    def get_last_post(self):
        return PostPrototype(model=models.Post.objects.filter(thread=self._model).order_by('-created_at')[0])

    @classmethod
    def get_new_thread_delay(cls, account):
        last_thread_time = cls._db_filter(author_id=account.id).aggregate(django_models.Max('created_at')).get('created_at__max')

        if last_thread_time is None:
            last_thread_time = account.created_at

        delay_seconds = conf.settings.THREAD_DELAY - (datetime.datetime.now() - last_thread_time).total_seconds()

        if delay_seconds > 0:
            return int(delay_seconds)

        return 0

    @classmethod
    @django_transaction.atomic
    def create(cls, subcategory, caption, author, text, markup_method=relations.MARKUP_METHOD.POSTMARKUP, technical=False):

        if isinstance(subcategory, int):
            subcategory = SubCategoryPrototype.get_by_id(subcategory)

        thread_model = models.Thread.objects.create(subcategory=subcategory._model,
                                                    caption=caption,
                                                    author=author._model,
                                                    last_poster=author._model,
                                                    technical=technical,
                                                    posts_count=0)

        models.Post.objects.create(thread=thread_model,
                                   author=author._model,
                                   markup_method=markup_method,
                                   technical=technical,
                                   text=text,
                                   created_at_turn=game_turn.number(),
                                   state=relations.POST_STATE.DEFAULT)

        prototype = cls(model=thread_model)

        subcategory.update()

        post_service_prototypes.MessagePrototype.create(post_service_message_handlers.ForumThreadHandler(thread_id=prototype.id))

        return prototype

    @django_transaction.atomic
    def delete(self):

        subcategory = self.subcategory

        models.Post.objects.filter(thread=self._model).delete()
        self._model.delete()

        subcategory.update()

    @django_transaction.atomic
    def update(self, caption=None, new_subcategory_id=None, important=None):

        subcategory = self.subcategory

        if caption is not None:
            self._model.caption = caption

        if important is not None:
            self._model.important = important

        try:
            last_post = PostPrototype(model=PostPrototype._db_filter(thread__id=self.id, state=relations.POST_STATE.DEFAULT).latest('created_at'))
        except PostPrototype._model_class.DoesNotExist:
            last_post = None

        if last_post is None:
            self._model.last_poster = None
            self._model.updated_at = datetime.datetime.now()
        else:
            self._model.last_poster = last_post.author._model
            self._model.updated_at = last_post.updated_at

        subcategory_changed = new_subcategory_id is not None and self.subcategory.id != new_subcategory_id

        if subcategory_changed:
            new_subcategory = SubCategoryPrototype.get_by_id(new_subcategory_id)
            self._model.subcategory = new_subcategory._model

        self.update_posts_count()

        self.save()

        subcategory.update()

        if subcategory_changed:
            new_subcategory.update()

    def update_posts_count(self):
        self._model.posts_count = PostPrototype._db_filter(thread=self._model).count() - 1

    def save(self):
        self._model.save()


class PostPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Post
    _readonly = ('id', 'created_at', 'created_at_turn', 'updated_at', 'text', 'markup_method', 'state', 'removed_by', 'technical', 'author_id', 'thread_id')
    _bidirectional = ()
    _get_by = ('id', )

    @utils_decorators.lazy_property
    def thread(self): return ThreadPrototype(self._model.thread)

    @utils_decorators.lazy_property
    def author(self): return accounts_prototypes.AccountPrototype(self._model.author) if self._model.author else None

    @property
    def is_updated(self):
        return self.updated_at is not None and self.updated_at > self.created_at + datetime.timedelta(seconds=1)

    @property
    def html(self):
        if self.markup_method.is_POSTMARKUP:
            return bbcode_renderers.default.render(self.text)
        elif self.markup_method.is_MARKDOWN:
            return markdown.markdown(self.text)

    @property
    def safe_html(self):
        if self.markup_method.is_POSTMARKUP:
            return bbcode_renderers.safe.render(self.text)
        elif self.markup_method.is_MARKDOWN:
            return markdown.markdown(self.text)

    @property
    def is_removed(self): return self.state.is_REMOVED

    @property
    def is_removed_by_author(self): return self.removed_by.is_AUTHOR

    @property
    def is_removed_by_thread_owner(self): return self.removed_by.is_THREAD_OWNER

    @property
    def is_removed_by_moderator(self): return self.removed_by.is_MODERATOR

    @classmethod
    def get_new_post_delay(cls, account):
        last_post_time = cls._db_filter(author_id=account.id).aggregate(django_models.Max('created_at')).get('created_at__max')

        if last_post_time is None:
            last_post_time = account.created_at

        posts_number = cls._db_filter(author_id=account.id).count()

        max_post_delay = max(conf.settings.POST_DELAY, conf.settings.FIRST_POST_DELAY - posts_number * conf.settings.POST_DELAY)

        delay_seconds = max_post_delay - (datetime.datetime.now() - last_post_time).total_seconds()

        if delay_seconds < 0:
            return 0

        return int(delay_seconds)

    @classmethod
    @django_transaction.atomic
    def create(cls, thread, author, text, technical=False):
        post = models.Post.objects.create(thread=thread._model,
                                          author=author._model,
                                          text=text,
                                          technical=technical,
                                          markup_method=relations.MARKUP_METHOD.POSTMARKUP,
                                          created_at_turn=game_turn.number(),
                                          state=relations.POST_STATE.DEFAULT)

        thread.update()

        thread.subcategory.update()

        prototype = cls(post)

        post_service_prototypes.MessagePrototype.create(post_service_message_handlers.ForumPostHandler(post_id=prototype.id))

        return prototype

    @django_transaction.atomic
    def delete(self, initiator):

        self._model.text = ''

        self._model.state = relations.POST_STATE.REMOVED

        if self.author == initiator:
            self._model.removed_by = relations.POST_REMOVED_BY.AUTHOR
        elif self.thread.author == initiator:
            self._model.removed_by = relations.POST_REMOVED_BY.THREAD_OWNER
        else:
            self._model.removed_by = relations.POST_REMOVED_BY.MODERATOR

        self._model.remove_initiator = initiator._model

        self.save()

        self.thread.update()

    @django_transaction.atomic
    def update(self, text):
        self._model.text = text
        self._model.updated_at_turn = game_turn.number()
        self.save()

        self.thread.update()
        self.thread.subcategory.update()

    def save(self):
        self._model.save()


class SubscriptionPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Subscription
    _readonly = ('id', )
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def get_for(cls, account, thread=None, subcategory=None):

        if thread is not None and subcategory is not None:
            raise exceptions.ForumException('only one value (thread or subcategory) must be defined')

        try:
            return cls(cls._model_class.objects.get(account_id=account.id,
                                                    thread_id=thread.id if thread is not None else None,
                                                    subcategory_id=subcategory.id if subcategory is not None else None))
        except cls._model_class.DoesNotExist:
            return None

    @classmethod
    def has_subscription(cls, account, thread=None, subcategory=None):
        return cls.get_for(account, thread, subcategory) is not None

    @classmethod
    def get_threads_for_account(cls, account):
        threads = models.Thread.objects.filter(subscription__account_id=account.id).order_by('-updated_at')
        return [ThreadPrototype(model=thread) for thread in threads]

    @classmethod
    def get_subcategories_for_account(cls, account):
        subcategories = models.SubCategory.objects.filter(subscription__account_id=account.id).order_by('-updated_at')
        return [SubCategoryPrototype(model=subcategory) for subcategory in subcategories]

    @classmethod
    def get_accounts_for_thread(cls, thread):
        accounts = accounts_models.Account.objects.filter(subscription__thread_id=thread.id)
        return [accounts_prototypes.AccountPrototype(model=account) for account in accounts]

    @classmethod
    def get_accounts_for_subcategory(cls, subcategory):
        accounts = accounts_models.Account.objects.filter(subscription__subcategory_id=subcategory.id)
        return [accounts_prototypes.AccountPrototype(model=account) for account in accounts]

    @classmethod
    def create(cls, account, thread=None, subcategory=None):
        if (thread is not None and subcategory is not None) or (thread is None and subcategory is None):
            raise exceptions.ForumException('only one value (thread or subcategory) must be defined')

        exist_subscription = SubscriptionPrototype.get_for(account, thread=thread, subcategory=subcategory)
        if exist_subscription is not None:
            return exist_subscription

        model = cls._model_class.objects.create(account=account._model,
                                                thread=thread._model if thread is not None else None,
                                                subcategory=subcategory._model if subcategory is not None else None)
        return cls(model)

    def remove(self):
        self._model.delete()

    @classmethod
    @django_transaction.atomic
    def remove_all_in_subcategory(cls, account_id, subcategory_id):
        cls._model_class.objects.filter(account_id=account_id, subcategory_id=subcategory_id).delete()
        cls._model_class.objects.filter(account_id=account_id, thread_id__in=ThreadPrototype._model_class.objects.filter(subcategory_id=subcategory_id)).delete()


class ThreadReadInfoPrototype(utils_prototypes.BasePrototype):
    _model_class = models.ThreadReadInfo
    _readonly = ('id', 'read_at', 'thread_id', 'account_id')
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def get_for(cls, thread_id, account_id):
        try:
            return cls(model=cls._model_class.objects.get(thread_id=thread_id, account_id=account_id))
        except cls._model_class.DoesNotExist:
            return None

    @classmethod
    def get_threads_info(cls, account_id):
        return {read_info.thread_id: read_info for read_info in cls.from_query(cls._db_filter(account_id=account_id))}

    @classmethod
    def remove_old_infos(cls):
        cls._model_class.objects.filter(read_at__lt=datetime.datetime.now() - datetime.timedelta(seconds=conf.settings.UNREAD_STATE_EXPIRE_TIME)).delete()

    @classmethod
    def create(cls, thread, account):
        try:
            model = cls._model_class.objects.create(thread_id=thread.id,
                                                    account_id=account.id)
            return cls(model=model)
        except django_db.IntegrityError:
            return cls.get_for(thread_id=thread.id, account_id=account.id)

    @classmethod
    def read_thread(cls, thread, account):

        info = cls.get_for(thread.id, account.id)

        if info:
            info.save()
            return info

        return cls.create(thread, account)

    def save(self):
        self._model.save()


class SubCategoryReadInfoPrototype(utils_prototypes.BasePrototype):
    _model_class = models.SubCategoryReadInfo
    _readonly = ('id', 'read_at', 'all_read_at', 'subcategory_id', 'account_id')
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def get_for(cls, subcategory_id, account_id):
        try:
            return cls(model=cls._model_class.objects.get(subcategory_id=subcategory_id, account_id=account_id))
        except cls._model_class.DoesNotExist:
            return None

    @classmethod
    def get_subcategories_info(cls, account_id):
        return {read_info.subcategory_id: read_info for read_info in cls.from_query(cls._db_filter(account_id=account_id))}

    @classmethod
    def remove_old_infos(cls):
        cls._model_class.objects.filter(read_at__lt=datetime.datetime.now() - datetime.timedelta(seconds=conf.settings.UNREAD_STATE_EXPIRE_TIME)).delete()

    @classmethod
    def create(cls, subcategory, account, all_read_at=None):
        if all_read_at is None:
            all_read_at = datetime.datetime.fromtimestamp(0)

        try:
            model = cls._model_class.objects.create(subcategory_id=subcategory.id,
                                                    account_id=account.id,
                                                    all_read_at=all_read_at)
            return cls(model=model)
        except django_db.IntegrityError:
            prototype = cls.get_for(subcategory_id=subcategory.id, account_id=account.id)
            prototype._model.all_read_at = all_read_at
            prototype.save()
            return prototype

    @classmethod
    def read_subcategory(cls, subcategory, account):

        info = cls.get_for(subcategory.id, account.id)

        if info:
            info.save()
            return info

        return cls.create(subcategory, account)

    @classmethod
    def read_all_in_subcategory(cls, subcategory, account):

        info = cls.get_for(subcategory.id, account.id)

        if info:
            info._model.all_read_at = datetime.datetime.now()
            info.save()
            return info

        return cls.create(subcategory, account, all_read_at=datetime.datetime.now())

    def save(self):
        self._model.save()


class PermissionPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Permission
    _readonly = ('id', 'account_id', 'subcategory_id')
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def get_for(cls, account_id, subcategory_id):
        try:
            return cls(model=cls._model_class.objects.get(account_id=account_id, subcategory_id=subcategory_id))
        except cls._model_class.DoesNotExist:
            return None

    @classmethod
    def create(cls, account, subcategory):
        model = cls._model_class.objects.create(account=account._model,
                                                subcategory=subcategory._model)
        return cls(model=model)

    def remove(self):
        SubscriptionPrototype.remove_all_in_subcategory(account_id=self.account_id, subcategory_id=self.subcategory_id)
        self._model.delete()
