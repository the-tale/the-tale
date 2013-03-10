# coding: utf-8

from django.core.urlresolvers import reverse
from django.conf import settings as project_settings

from dext.utils.decorators import nested_commit_on_success

from common.utils import bbcode

from accounts.prototypes import AccountPrototype

from blogs.models import Post, Vote, POST_STATE

from forum.prototypes import ThreadPrototype as ForumThreadPrototype
from forum.prototypes import SubCategoryPrototype as ForumSubCategoryPrototype
from forum.models import MARKUP_METHOD

from blogs.conf import blogs_settings

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

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = POST_STATE(self.model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self.model.state = self.state.value
    state = property(get_state, set_state)

    @property
    def forum_thread_id(self): return self.model.forum_thread_id

    @property
    def forum_thread(self):
        if not hasattr(self, '_forum_thread'):
            self._forum_thread = ForumThreadPrototype.get_by_id(self.forum_thread_id)
        return self._forum_thread

    def get_votes(self): return self.model.votes
    def set_votes(self, value): self.model.votes = value
    votes = property(get_votes, set_votes)

    def get_moderator_id(self): return self.model.moderator_id
    def set_moderator_id(self, value): return self.model.moderator_id
    moderator_id = property(get_moderator_id, set_moderator_id)

    def get_caption(self): return self.model.caption
    def set_caption(self, value): self.model.caption = value
    caption = property(get_caption, set_caption)

    def get_text(self): return self.model.text
    def set_text(self, value): self.model.text = value
    text = property(get_text, set_text)

    @property
    def text_html(self): return bbcode.render(self.text)

    @property
    def author(self):
        if not hasattr(self, '_author'):
            self._author = AccountPrototype(self.model.author)
        return self._author

    @property
    def created_at(self): return self.model.created_at

    @property
    def updated_at(self): return self.model.updated_at

    def recalculate_votes(self):
        self.votes = Vote.objects.filter(post=self.model, value=True).count() - Vote.objects.filter(post=self.model, value=False).count()

    @classmethod
    @nested_commit_on_success
    def create(cls, author, caption, text):

        model = Post.objects.create(author=author.model,
                                    caption=caption,
                                    text=text,
                                    votes=1)

        thread = ForumThreadPrototype.create(ForumSubCategoryPrototype.get_by_slug(blogs_settings.FORUM_CATEGORY_SLUG),
                                             caption=caption,
                                             author=author,
                                             text=u'обсуждение [url="%s%s"]произведения[/url]' % (project_settings.SITE_URL,
                                                                                                  reverse('blogs:posts:show', args=[model.id])),
                                             markup_method=MARKUP_METHOD.POSTMARKUP)

        model.forum_thread = thread.model
        model.save()

        post = cls(model)

        VotePrototype.create(post, author, True)

        return post

    def save(self):
        self.model.save()


class VotePrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(Vote.objects.get(id=id_))
        except Vote.DoesNotExist:
            return None

    @classmethod
    def get_for(cls, voter, post):
        try:
            return cls(Vote.objects.get(voter_id=voter.id, post_id=post.id))
        except Vote.DoesNotExist:
            return None

    @property
    def voter(self):
        if not hasattr(self, '_voter'):
            self._voter = AccountPrototype(self.model.voter)
        return self._voter

    def get_value(self): return self.model.value
    def set_value(self, value): self.model.value = value
    value = property(get_value, set_value)

    @classmethod
    def create(cls, post, voter, value):
        model = Vote.objects.create(post=post.model,
                                    voter=voter.model,
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
        self.model.save()
