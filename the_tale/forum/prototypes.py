# coding: utf-8
import markdown

from django.core.urlresolvers import reverse

from dext.utils.decorators import nested_commit_on_success
from dext.utils.urls import UrlBuilder

from accounts.prototypes import AccountPrototype

from common.utils import bbcode
from common.utils.pagination import Paginator

from forum.conf import forum_settings
from forum.models import Category, SubCategory, Thread, Post, MARKUP_METHOD, POST_STATE, POST_REMOVED_BY


class CategoryPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_slug(cls, slug):
        try:
            return cls(Category.objects.get(slug=slug))
        except Category.DoesNotExist:
            return None

    @property
    def id(self): return self.model.id

    @property
    def caption(self): return self.model.caption

    @property
    def slug(self): return self.model.slug

    @property
    def order(self): return self.model.order

    @classmethod
    def create(cls, caption, slug, order):

        model = Category.objects.create(caption=caption, slug=slug, order=order)

        return cls(model)


class SubCategoryPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_slug(cls, slug):
        try:
            return cls(SubCategory.objects.get(slug=slug))
        except SubCategory.DoesNotExist:
            return None

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(SubCategory.objects.get(id=id_))
        except SubCategory.DoesNotExist:
            return None

    @property
    def id(self): return self.model.id

    @property
    def created_at(self): return self.model.created_at

    @property
    def category(self):
        if not hasattr(self, '_category'):
            self._category = CategoryPrototype(self.model.category)
        return self._category

    @property
    def category_id(self): return self.model.category_id

    @property
    def slug(self): return self.model.slug

    @property
    def caption(self): return self.model.caption

    @property
    def order(self): return self.model.order

    @property
    def updated_at(self): return self.model.updated_at

    @property
    def threads_count(self): return self.model.threads_count
    def update_threads_count(self): self.model.threads_count = Thread.objects.filter(subcategory=self.model).count()

    @property
    def posts_count(self): return self.model.posts_count
    def update_posts_count(self): self.model.posts_count = sum(Thread.objects.filter(subcategory=self.model).values_list('posts_count', flat=True))

    @property
    def last_poster(self):
        if not hasattr(self, '_last_poster'):
            self._last_poster = AccountPrototype(self.model.last_poster) if self.model.last_poster else None
        return self._last_poster

    @property
    def closed(self): return self.model.closed

    def update(self, author=None, date=None):
        self.update_threads_count()
        self.update_posts_count()

        if author:
            self.model.last_poster = author.model

        if date:
            self.model.updated_at = date

        self.save()

    def save(self):
        self.model.save()

    @classmethod
    @nested_commit_on_success
    def create(cls, category, caption, slug, order, closed=False):

        model = SubCategory.objects.create(category=category.model, caption=caption, slug=slug, order=order, closed=closed)

        return cls(model)


class ThreadPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(Thread.objects.get(id=id_))
        except Thread.DoesNotExist:
            return None

    @property
    def id(self): return self.model.id

    @property
    def created_at(self): return self.model.created_at

    @property
    def subcategory(self):
        if not hasattr(self, '_subcategory'):
            self._subcategory = SubCategoryPrototype(self.model.subcategory)
        return self._subcategory

    def get_caption(self): return self.model.caption
    def set_caption(self, value): self.model.caption = value
    caption = property(get_caption, set_caption)

    @property
    def author(self):
        if not hasattr(self, '_author'):
            self._author = AccountPrototype(self.model.author) if self.model.author else None
        return self._author

    @property
    def last_poster(self):
        if not hasattr(self, '_last_poster'):
            self._last_poster = AccountPrototype(self.model.last_poster) if self.model.last_poster else None
        return self._last_poster

    @property
    def posts_count(self): return self.model.posts_count

    @property
    def updated_at(self): return self.model.updated_at

    @property
    def paginator(self):
        url_builder = UrlBuilder(reverse('forum:threads:show', args=[self.id]))
        # +1 since first post does not counted
        return Paginator(1, self.posts_count+1, forum_settings.POSTS_ON_PAGE, url_builder)

    @classmethod
    def get_threads_with_last_users_posts(cls, user, limit=None):
        from django.db import models

        threads = Thread.objects.filter(post__author=user.model).annotate(last_user_post_time=models.Max('post__updated_at')).order_by('-last_user_post_time')

        if limit:
            threads = threads[:limit]

        return [cls(thread) for thread in threads]


    @classmethod
    @nested_commit_on_success
    def create(cls, subcategory, caption, author, text, markup_method=MARKUP_METHOD.POSTMARKUP):

        if isinstance(subcategory, int):
            subcategory = SubCategoryPrototype.get_by_id(subcategory)

        thread_model = Thread.objects.create(subcategory=subcategory.model,
                                             caption=caption,
                                             author=author.model,
                                             last_poster=author.model,
                                             posts_count=0)

        post_model = Post.objects.create(thread=thread_model,
                                         author=author.model,
                                         markup_method=markup_method,
                                         text=text)

        subcategory.update(author, post_model.created_at)

        return cls(thread_model)


    @nested_commit_on_success
    def delete(self):

        subcategory = self.subcategory

        Post.objects.filter(thread=self.model).delete()
        self.model.delete()

        subcategory.update()


    @nested_commit_on_success
    def update(self, caption=None, new_subcategory_id=None, author=None, date=None):

        subcategory = self.subcategory

        if caption is not None:
            self.model.caption = caption

        if date is not None:
            self.model.updated_at = date

        if author:
            self.model.last_poster = author.model

        subcategory_changed = new_subcategory_id is not None and self.subcategory.id != new_subcategory_id

        if subcategory_changed:
            new_subcategory = SubCategoryPrototype.get_by_id(new_subcategory_id)
            self.model.subcategory = new_subcategory.model

        self.update_posts_count()

        self.save()

        if subcategory_changed:
            subcategory.update()
            new_subcategory.update()

    def update_posts_count(self): self.model.posts_count = Post.objects.filter(thread=self.model).count() - 1

    def save(self):
        self.model.save()



class PostPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(Post.objects.get(id=id_))
        except Post.DoesNotExist:
            return None

    @property
    def id(self): return self.model.id

    @property
    def thread(self):
        if not hasattr(self, '_thread'):
            self._thread = ThreadPrototype(self.model.thread)
        return self._thread

    @property
    def created_at(self): return self.model.created_at

    @property
    def updated_at(self): return self.model.updated_at

    @property
    def author(self):
        if not hasattr(self, '_author'):
            self._author = AccountPrototype(self.model.author) if self.model.author else None
        return self._author

    @property
    def text(self): return self.model.text

    @property
    def markup_method(self): return self.model.markup_method

    @property
    def state(self): return self.model.state

    @property
    def removed_by(self): return self.model.removed_by

    @property
    def remove_initiator(self): return self.model.remove_initiator

    @property
    def technical(self): return self.model.technical

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

        post = Post.objects.create(thread=thread.model, author=author.model, text=text, technical=technical)

        thread.update(author=author, date=post.created_at)

        thread.subcategory.update(author, post.created_at)

        return cls(post)


    @nested_commit_on_success
    def delete(self, initiator, thread):

        self.model.state = POST_STATE.REMOVED

        if self.author == initiator:
            self.model.removed_by = POST_REMOVED_BY.AUTHOR
        elif thread.author == initiator:
            self.model.removed_by = POST_REMOVED_BY.THREAD_OWNER
        else:
            self.model.removed_by = POST_REMOVED_BY.MODERATOR

        self.model.remove_initiator = initiator.model

        self.save()

    def update(self, text):
        self.model.text = text
        self.save()

    def save(self):
        self.model.save()
