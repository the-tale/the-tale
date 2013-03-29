# coding: utf-8

from django.core.urlresolvers import reverse
from django.conf import settings as project_settings

from dext.utils.decorators import nested_commit_on_success

from common.utils import bbcode
from common.utils.decorators import lazy_property
from common.utils.prototypes import BasePrototype

from accounts.prototypes import AccountPrototype

from forum.prototypes import ThreadPrototype as ForumThreadPrototype
from forum.prototypes import SubCategoryPrototype as ForumSubCategoryPrototype
from forum.models import MARKUP_METHOD

from blogs.models import Post, Vote, POST_STATE
from blogs.conf import blogs_settings


class PostPrototype(BasePrototype):
    _model_class = Post
    _readonly = ('id', 'forum_thread_id', 'created_at', 'updated_at')
    _bidirectional = ('votes', 'moderator_id', 'caption', 'text')
    _get_by = ('id', )

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = POST_STATE(self._model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self._model.state = self.state.value
    state = property(get_state, set_state)

    @lazy_property
    def forum_thread(self): return ForumThreadPrototype.get_by_id(self.forum_thread_id)

    @property
    def text_html(self): return bbcode.render(self.text)

    @lazy_property
    def author(self): return AccountPrototype(self._model.author)

    def recalculate_votes(self):
        self.votes = Vote.objects.filter(post=self._model, value=True).count() - Vote.objects.filter(post=self._model, value=False).count()

    @classmethod
    @nested_commit_on_success
    def create(cls, author, caption, text):

        model = Post.objects.create(author=author._model,
                                    caption=caption,
                                    text=text,
                                    votes=1)

        thread = ForumThreadPrototype.create(ForumSubCategoryPrototype.get_by_slug(blogs_settings.FORUM_CATEGORY_SLUG),
                                             caption=caption,
                                             author=author,
                                             text=u'обсуждение [url="%s%s"]произведения[/url]' % (project_settings.SITE_URL,
                                                                                                  reverse('blogs:posts:show', args=[model.id])),
                                             markup_method=MARKUP_METHOD.POSTMARKUP)

        model.forum_thread = thread._model
        model.save()

        post = cls(model)

        VotePrototype.create(post, author, True)

        return post

    def save(self):
        self._model.save()


class VotePrototype(BasePrototype):
    _model_class = Vote
    _readonly = ('id', )
    _bidirectional = ('value',)
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
    def create(cls, post, voter, value):
        model = Vote.objects.create(post=post._model,
                                    voter=voter._model,
                                    value=value)
        return cls(model)

    @classmethod
    def create_or_update(cls, post, voter, value):
        vote = cls.get_for(voter, post)

        if vote:
            vote.value = value
            vote.save()
            return vote

        return cls.create(post, voter, value)

    def save(self):
        self._model.save()
