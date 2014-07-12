# coding: utf-8

from django.core.urlresolvers import reverse
from django.conf import settings as project_settings
from django.db import transaction

from the_tale.common.utils import bbcode
from the_tale.common.utils.decorators import lazy_property
from the_tale.common.utils.prototypes import BasePrototype

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import get_system_user

from the_tale.forum.prototypes import ThreadPrototype as ForumThreadPrototype, PostPrototype as ForumPostPrototype
from the_tale.forum.prototypes import SubCategoryPrototype as ForumSubCategoryPrototype
from the_tale.forum.models import MARKUP_METHOD

from the_tale.blogs.models import Post, Vote
from the_tale.blogs.conf import blogs_settings
from the_tale.blogs.relations import POST_STATE


class PostPrototype(BasePrototype):
    _model_class = Post
    _readonly = ('id', 'forum_thread_id', 'created_at', 'updated_at')
    _bidirectional = ('votes', 'moderator_id', 'caption', 'text', 'state')
    _get_by = ('id', )

    @lazy_property
    def forum_thread(self): return ForumThreadPrototype.get_by_id(self.forum_thread_id)

    @property
    def text_html(self): return bbcode.render(self.text)

    @lazy_property
    def author(self):
        if self._model.author:
            return AccountPrototype(self._model.author)
        return None

    def recalculate_votes(self):
        self.votes = Vote.objects.filter(post=self._model).count()

    @classmethod
    @transaction.atomic
    def create(cls, author, caption, text):

        model = Post.objects.create(author=author._model,
                                    caption=caption,
                                    text=text,
                                    state=POST_STATE.ACCEPTED,
                                    votes=1)

        thread = ForumThreadPrototype.create(ForumSubCategoryPrototype.get_by_uid(blogs_settings.FORUM_CATEGORY_UID),
                                             caption=caption,
                                             author=get_system_user(),
                                             text=u'обсуждение [url="%s%s"]произведения[/url]' % (project_settings.SITE_URL,
                                                                                                  reverse('blogs:posts:show', args=[model.id])),
                                             markup_method=MARKUP_METHOD.POSTMARKUP)

        model.forum_thread = thread._model
        model.save()

        post = cls(model)

        VotePrototype.create(post, author)

        return post

    @transaction.atomic
    def accept(self, moderator):
        self.state = POST_STATE.ACCEPTED
        self.moderator_id = moderator.id
        self.save()

    @transaction.atomic
    def decline(self, moderator):
        self.state = POST_STATE.DECLINED
        self.moderator_id = moderator.id
        self.save()

        thread = ForumThreadPrototype(self._model.forum_thread)
        thread.caption = thread.caption + u' [удалён]'
        thread.save()

        ForumPostPrototype.create(thread,
                                  get_system_user(),
                                  u'Произведение было удалено',
                                  technical=True)


    def save(self):
        self._model.save()


class VotePrototype(BasePrototype):
    _model_class = Vote
    _readonly = ('id', )
    _bidirectional = ()
    _get_by = ('id', )

    @classmethod
    def get_for(cls, voter, post):
        try:
            return cls(Vote.objects.get(voter_id=voter.id, post_id=post.id))
        except Vote.DoesNotExist:
            return None

    @lazy_property
    def voter(self): return AccountPrototype(self._model.voter)

    @classmethod
    def create(cls, post, voter):
        model = Vote.objects.create(post=post._model,
                                    voter=voter._model)
        return cls(model)

    @classmethod
    def remove_if_exists(cls, post, voter):
        vote = cls.get_for(voter, post)

        if vote:
            vote.remove()

        return None

    @classmethod
    def create_if_not_exists(cls, post, voter):
        vote = cls.get_for(voter, post)

        if vote:
            return vote

        return cls.create(post, voter)

    def save(self):
        self._model.save()

    def remove(self):
        self._model.delete()
