# coding: utf-8

from django.db import models

from the_tale.blogs.relations import POST_STATE

from rels.django import RelationIntegerField


class Post(models.Model):

    CAPTION_MIN_LENGTH = 10
    CAPTION_MAX_LENGTH = 256

    author = models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    created_at_turn = models.BigIntegerField()

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)
    text = models.TextField(null=False, blank=True, default='')

    state = RelationIntegerField(relation=POST_STATE, relation_column='value', db_index=True)

    moderator = models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    votes = models.IntegerField(default=0)

    rating = models.IntegerField(default=0)

    # we should not remove post when ocasionally remove forum thread
    forum_thread = models.ForeignKey('forum.Thread', null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    class Meta(object):
        permissions = (("moderate_post", u"Может редактировать сообщения пользователей"), )

    def __unicode__(self): return self.caption


class Vote(models.Model):

    voter = models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=False, related_name='+', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta(object):
        unique_together = (('voter', 'post'),)


class Tag(models.Model):
    NAME_MAX_LENGTH = 32

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField()

    def __unicode__(self): return self.name


class Tagged(models.Model):

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __unicode__(self): return u'<%s - %s>' % (self.tag.name, self.post.caption)
