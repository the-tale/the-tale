# coding: utf-8
import datetime

import markdown

from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction, models

from dext.utils.urls import UrlBuilder

from the_tale.accounts.models import Account
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.common.utils import bbcode
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.forum.conf import forum_settings
from the_tale.forum.models import Category, SubCategory, Thread, Post, Subscription, ThreadReadInfo, SubCategoryReadInfo, Permission
from the_tale.forum.exceptions import ForumException
from the_tale.forum.relations import MARKUP_METHOD, POST_REMOVED_BY, POST_STATE


class CategoryPrototype(BasePrototype):
    _model_class = Category
    _readonly = ('id', 'caption', 'slug', 'order')
    _bidirectional = ()
    _get_by = ('slug', 'id')

    @classmethod
    def create(cls, caption, slug, order):
        model = Category.objects.create(caption=caption, slug=slug, order=order)
        return cls(model)


class SubCategoryPrototype(BasePrototype):
    _model_class = SubCategory
    _readonly = ('id', 'order', 'created_at', 'category_id', 'updated_at', 'threads_count', 'posts_count', 'closed', 'last_thread_created_at', 'restricted')
    _bidirectional = ('caption',)
    _get_by = ('id', 'uid')

    @lazy_property
    def category(self): return CategoryPrototype(self._model.category)

    def update_threads_count(self): self._model.threads_count = Thread.objects.filter(subcategory=self._model).count()

    def update_posts_count(self): self._model.posts_count = sum(Thread.objects.filter(subcategory=self._model).values_list('posts_count', flat=True))

    @lazy_property
    def last_poster(self): return AccountPrototype(self._model.last_poster) if self._model.last_poster else None

    def is_restricted_for(self, account):
        if not self.restricted:
            return False
        if not account.is_authenticated():
            return True
        return PermissionPrototype.get_for(account_id=account.id, subcategory_id=self.id) is None

    def update(self, author=None, date=None, last_thread_created_at=None):
        self.update_threads_count()
        self.update_posts_count()

        if author:
            self._model.last_poster = author._model

        if date:
            self._model.updated_at = date

        if last_thread_created_at:
            self._model.last_thread_created_at = last_thread_created_at

        self.save()

    def save(self):
        self._model.save()

    @classmethod
    @transaction.atomic
    def create(cls, category, caption, order, closed=False, restricted=False, uid=None):

        model = SubCategory.objects.create(category=category._model, caption=caption, order=order, closed=closed, restricted=restricted, uid=uid)

        return cls(model=model)


class ThreadPrototype(BasePrototype):
    _model_class = Thread
    _readonly = ('id', 'created_at', 'posts_count', 'updated_at', 'technical', 'subcategory_id')
    _bidirectional = ('caption', )
    _get_by = ('id', )

    @lazy_property
    def subcategory(self): return SubCategoryPrototype(self._model.subcategory)

    @lazy_property
    def author(self): return AccountPrototype(self._model.author) if self._model.author else None

    @lazy_property
    def last_poster(self): return AccountPrototype(self._model.last_poster) if self._model.last_poster else None

    @property
    def paginator(self):
        url_builder = UrlBuilder(reverse('forum:threads:show', args=[self.id]))
        # +1 since first post does not counted
        return Paginator(1, self.posts_count+1, forum_settings.POSTS_ON_PAGE, url_builder)

    @classmethod
    def threads_visible_to_account_query(cls, account):
        if account:
            return cls._model_class.objects.filter(models.Q(subcategory__restricted=False) |
                                                   (models.Q(subcategory__restricted=True) & models.Q(subcategory__permission__account_id=account.id)) )
        else:
            return cls._model_class.objects.filter(subcategory__restricted=False)

    @classmethod
    def get_last_threads(cls, account, limit):
        return cls.from_query(cls.threads_visible_to_account_query(account=account).order_by('-updated_at')[:limit])


    def get_first_post(self):
        return PostPrototype(model=Post.objects.filter(thread=self._model).order_by('created_at')[0])

    @classmethod
    @transaction.atomic
    def create(cls, subcategory, caption, author, text, markup_method=MARKUP_METHOD.POSTMARKUP, technical=False):

        from the_tale.post_service.prototypes import MessagePrototype
        from the_tale.post_service.message_handlers import ForumThreadHandler

        if isinstance(subcategory, int):
            subcategory = SubCategoryPrototype.get_by_id(subcategory)

        thread_model = Thread.objects.create(subcategory=subcategory._model,
                                             caption=caption,
                                             author=author._model,
                                             last_poster=author._model,
                                             technical=technical,
                                             posts_count=0)

        post_model = Post.objects.create(thread=thread_model,
                                         author=author._model,
                                         markup_method=markup_method,
                                         technical=technical,
                                         text=text,
                                         state=POST_STATE.DEFAULT)

        prototype = cls(model=thread_model)

        subcategory.update(author, post_model.created_at, last_thread_created_at=prototype.created_at)

        MessagePrototype.create(ForumThreadHandler(thread_id=prototype.id))

        return prototype


    @transaction.atomic
    def delete(self):

        subcategory = self.subcategory

        Post.objects.filter(thread=self._model).delete()
        self._model.delete()

        subcategory.update()


    @transaction.atomic
    def update(self, caption=None, new_subcategory_id=None, author=None, date=None):

        subcategory = self.subcategory

        if caption is not None:
            self._model.caption = caption

        if date is not None:
            self._model.updated_at = date

        if author:
            self._model.last_poster = author._model

        subcategory_changed = new_subcategory_id is not None and self.subcategory.id != new_subcategory_id

        if subcategory_changed:
            new_subcategory = SubCategoryPrototype.get_by_id(new_subcategory_id)
            self._model.subcategory = new_subcategory._model

        self.update_posts_count()

        self.save()

        if subcategory_changed:
            subcategory.update()
            new_subcategory.update()

    def update_posts_count(self): self._model.posts_count = Post.objects.filter(thread=self._model).count() - 1

    def save(self):
        self._model.save()



class PostPrototype(BasePrototype):
    _model_class = Post
    _readonly = ('id', 'created_at', 'updated_at', 'text', 'markup_method', 'state', 'removed_by', 'technical')
    _bidirectional = ()
    _get_by = ('id', )

    @lazy_property
    def thread(self): return ThreadPrototype(self._model.thread)

    @lazy_property
    def author(self): return AccountPrototype(self._model.author) if self._model.author else None

    @property
    def html(self):
        if self.markup_method.is_POSTMARKUP:
            return bbcode.render(self.text)
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
    @transaction.atomic
    def create(cls, thread, author, text, technical=False):

        from the_tale.post_service.prototypes import MessagePrototype
        from the_tale.post_service.message_handlers import ForumPostHandler

        post = Post.objects.create(thread=thread._model,
                                   author=author._model,
                                   text=text,
                                   technical=technical,
                                   markup_method=MARKUP_METHOD.POSTMARKUP,
                                   state=POST_STATE.DEFAULT)

        thread.update(author=author, date=post.created_at)

        thread.subcategory.update(author, post.created_at)

        prototype = cls(post)

        MessagePrototype.create(ForumPostHandler(post_id=prototype.id))

        return prototype


    @transaction.atomic
    def delete(self, initiator, thread):

        self._model.state = POST_STATE.REMOVED

        if self.author == initiator:
            self._model.removed_by = POST_REMOVED_BY.AUTHOR
        elif thread.author == initiator:
            self._model.removed_by = POST_REMOVED_BY.THREAD_OWNER
        else:
            self._model.removed_by = POST_REMOVED_BY.MODERATOR

        self._model.remove_initiator = initiator._model

        self.save()

    def update(self, text):
        self._model.text = text
        self.save()

    def save(self):
        self._model.save()


class SubscriptionPrototype(BasePrototype):
    _model_class = Subscription
    _readonly = ('id', )
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def get_for(cls, account, thread=None, subcategory=None):

        if thread is not None and subcategory is not None:
            raise ForumException('only one value (thread or subcategory) must be defined')

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
        threads = Thread.objects.filter(subscription__account_id=account.id).order_by('-updated_at')
        return [ThreadPrototype(model=thread) for thread in threads]

    @classmethod
    def get_subcategories_for_account(cls, account):
        subcategories = SubCategory.objects.filter(subscription__account_id=account.id).order_by('-updated_at')
        return [SubCategoryPrototype(model=subcategory) for subcategory in subcategories]

    @classmethod
    def get_accounts_for_thread(cls, thread):
        accounts = Account.objects.filter(subscription__thread_id=thread.id)
        return [AccountPrototype(model=account) for account in accounts]

    @classmethod
    def get_accounts_for_subcategory(cls, subcategory):
        accounts = Account.objects.filter(subscription__subcategory_id=subcategory.id)
        return [AccountPrototype(model=account) for account in accounts]

    @classmethod
    def create(cls, account, thread=None, subcategory=None):
        if (thread is not None and subcategory is not None) or (thread is None and subcategory is None):
            raise ForumException('only one value (thread or subcategory) must be defined')

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
    @transaction.atomic
    def remove_all_in_subcategory(cls, account_id, subcategory_id):
        cls._model_class.objects.filter(account_id=account_id, subcategory_id=subcategory_id).delete()
        cls._model_class.objects.filter(account_id=account_id, thread_id__in=ThreadPrototype._model_class.objects.filter(subcategory_id=subcategory_id)).delete()


class ThreadReadInfoPrototype(BasePrototype):
    _model_class = ThreadReadInfo
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
    def get_threads_info(cls, threads_ids, account_id):
        return dict(cls._model_class.objects.filter(account_id=account_id, thread_id__in=threads_ids).values_list('thread_id', 'read_at'))

    @classmethod
    def remove_old_infos(cls):
        cls._model_class.objects.filter(read_at__lt=datetime.datetime.now() - datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME)).delete()

    @classmethod
    def create(cls, thread, account):
        try:
            model = cls._model_class.objects.create(thread_id=thread.id,
                                                    account_id=account.id)
            return cls(model=model)
        except IntegrityError:
            return cls._get_for(thread_id=thread.id, account_id=account.id)

    @classmethod
    def read_thread(cls, thread, account):

        info = cls.get_for(thread.id, account.id)

        if info:
            info.save()
            return info

        return cls.create(thread, account)

    def save(self):
        self._model.save()


class SubCategoryReadInfoPrototype(BasePrototype):
    _model_class = SubCategoryReadInfo
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
    def remove_old_infos(cls):
        cls._model_class.objects.filter(read_at__lt=datetime.datetime.now() - datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME)).delete()

    @classmethod
    def create(cls, subcategory, account, all_read_at=None):
        if all_read_at is None:
            all_read_at = datetime.datetime.fromtimestamp(0)

        try:
            model = cls._model_class.objects.create(subcategory_id=subcategory.id,
                                                    account_id=account.id,
                                                    all_read_at=all_read_at)
            return cls(model=model)
        except IntegrityError:
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


class PermissionPrototype(BasePrototype):
    _model_class = Permission
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
