# coding: utf-8
import markdown

from django.core.urlresolvers import reverse

from dext.utils.decorators import nested_commit_on_success
from dext.utils.urls import UrlBuilder

from accounts.models import Account
from accounts.prototypes import AccountPrototype

from common.utils import bbcode
from common.utils.pagination import Paginator
from common.utils.prototypes import BasePrototype
from common.utils.decorators import lazy_property

from forum.conf import forum_settings
from forum.models import Category, SubCategory, Thread, Post, Subscription, MARKUP_METHOD, POST_STATE, POST_REMOVED_BY


class CategoryPrototype(BasePrototype):
    _model_class = Category
    _readonly = ('id', 'caption', 'slug', 'order')
    _bidirectional = ()
    _get_by = ('slug', )

    @classmethod
    def create(cls, caption, slug, order):
        model = Category.objects.create(caption=caption, slug=slug, order=order)
        return cls(model)


class SubCategoryPrototype(BasePrototype):
    _model_class = SubCategory
    _readonly = ('id', 'caption', 'slug', 'order', 'created_at', 'category_id', 'updated_at', 'threads_count', 'posts_count', 'closed')
    _bidirectional = ()
    _get_by = ('slug', 'id')

    @lazy_property
    def category(self): return CategoryPrototype(self._model.category)

    def update_threads_count(self): self._model.threads_count = Thread.objects.filter(subcategory=self._model).count()

    def update_posts_count(self): self._model.posts_count = sum(Thread.objects.filter(subcategory=self._model).values_list('posts_count', flat=True))

    @lazy_property
    def last_poster(self): return AccountPrototype(self._model.last_poster) if self._model.last_poster else None

    def update(self, author=None, date=None):
        self.update_threads_count()
        self.update_posts_count()

        if author:
            self._model.last_poster = author._model

        if date:
            self._model.updated_at = date

        self.save()

    def save(self):
        self._model.save()

    @classmethod
    @nested_commit_on_success
    def create(cls, category, caption, slug, order, closed=False):

        model = SubCategory.objects.create(category=category._model, caption=caption, slug=slug, order=order, closed=closed)

        return cls(model=model)


class ThreadPrototype(BasePrototype):
    _model_class = Thread
    _readonly = ('id', 'created_at', 'posts_count', 'updated_at', 'technical')
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
    def get_threads_with_last_users_posts(cls, account, limit=None):
        from django.db import models

        threads = Thread.objects.filter(post__author=account._model).annotate(last_user_post_time=models.Max('post__updated_at')).order_by('-last_user_post_time')

        if limit:
            threads = threads[:limit]

        return [cls(thread) for thread in threads]


    @classmethod
    @nested_commit_on_success
    def create(cls, subcategory, caption, author, text, markup_method=MARKUP_METHOD.POSTMARKUP, technical=False):

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
                                         text=text)

        subcategory.update(author, post_model.created_at)

        return cls(thread_model)


    @nested_commit_on_success
    def delete(self):

        subcategory = self.subcategory

        Post.objects.filter(thread=self._model).delete()
        self._model.delete()

        subcategory.update()


    @nested_commit_on_success
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
        if self.markup_method == MARKUP_METHOD.POSTMARKUP:
            return bbcode.render(self.text)
        elif self.markup_method == MARKUP_METHOD.MARKDOWN:
            return markdown.markdown(self.text)

    @property
    def is_removed(self): return self.state == POST_STATE.REMOVED

    @property
    def is_removed_by_author(self): return self.removed_by == POST_REMOVED_BY.AUTHOR

    @property
    def is_removed_by_thread_owner(self): return self.removed_by == POST_REMOVED_BY.THREAD_OWNER

    @property
    def is_removed_by_moderator(self): return self.removed_by == POST_REMOVED_BY.MODERATOR

    @classmethod
    @nested_commit_on_success
    def create(cls, thread, author, text, technical=False):

        from post_service.prototypes import MessagePrototype
        from post_service.message_handlers import ForumPostHandler

        post = Post.objects.create(thread=thread._model, author=author._model, text=text, technical=technical)

        thread.update(author=author, date=post.created_at)

        thread.subcategory.update(author, post.created_at)

        prototype = cls(post)

        MessagePrototype.create(ForumPostHandler(post_id=prototype.id))

        return prototype


    @nested_commit_on_success
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
    _readonly = ()
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def get_for(cls, account, thread):
        try:
            return cls(cls._model_class.objects.get(account_id=account.id, thread_id=thread.id))
        except cls._model_class.DoesNotExist:
            return None

    @classmethod
    def get_threads_for_account(cls, account):
        threads = Thread.objects.filter(subscription__account_id=account.id).order_by('updated_at')
        return [ThreadPrototype(model=thread) for thread in threads]

    @classmethod
    def get_accounts_for_thread(cls, thread):
        accounts = Account.objects.filter(subscription__thread_id=thread.id)
        return [AccountPrototype(model=account) for account in accounts]

    @classmethod
    def create(cls, account, thread):
        model = cls._model_class.objects.create(account=account._model, thread=thread._model)
        return cls(model)

    @classmethod
    def has_subscription(cls, account, thread):
        return cls._model_class.objects.filter(account_id=account.id, thread_id=thread.id).exists()

    def remove(self):
        self._model.delete()
