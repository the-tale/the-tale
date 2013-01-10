# coding: utf-8
import datetime

from django.db import models
from django.core.urlresolvers import reverse

class Category(models.Model):

    caption = models.CharField(max_length=256, blank=False, null=False)

    slug = models.CharField(max_length=32, blank=False, null=False, db_index=True)

    order = models.IntegerField(default=0, null=False, blank=True)

    def __unicode__(self): return self.slug


class SubCategory(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    category = models.ForeignKey(Category, null=False)

    slug = models.CharField(max_length=32, blank=False, null=False, db_index=True)

    caption = models.CharField(max_length=256, blank=False, null=False)

    order = models.IntegerField(default=0, null=False, blank=True)

    updated_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    threads_count = models.IntegerField(default=0, null=False)

    last_poster = models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+')

    posts_count = models.BigIntegerField(default=0, null=False)

    closed = models.BooleanField(default=False) # if True, only staff can create themes in this subcategory

    def __unicode__(self): return self.slug


class Thread(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    subcategory = models.ForeignKey(SubCategory, null=False)

    caption = models.CharField(max_length=256, blank=False, null=False)

    author =  models.ForeignKey('accounts.Account', null=True, related_name='+')

    last_poster = models.ForeignKey('accounts.Account', null=True, related_name='+')

    posts_count = models.BigIntegerField(default=0, null=False)

    updated_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    class Meta:
        permissions = (("moderate_thread", u"Может редактировать темы на форуме"), )

    def get_absolute_url(self):
        return reverse('forum:threads:show', args=[self.id])

    def __unicode__(self): return u'%d - %s' % (self.id, self.caption)


class MARKUP_METHOD:
    POSTMARKUP = 0
    MARKDOWN = 1

MARKUP_METHOD_CHOICES = ( (MARKUP_METHOD.POSTMARKUP, 'bb-code'),
                          (MARKUP_METHOD.MARKDOWN, 'markdown') )

class POST_REMOVED_BY:
    AUTHOR = 0
    THREAD_OWNER = 1
    MODERATOR = 2

POST_REMOVED_BY_CHOICES = ( (POST_REMOVED_BY.AUTHOR, u'удалён автором'),
                            (POST_REMOVED_BY.THREAD_OWNER, u'удалён владельцем темы'),
                            (POST_REMOVED_BY.MODERATOR, u'удалён модератором') )

class POST_STATE:
    DEFAULT = 0
    REMOVED = 1

POST_STATE_CHOICES = ( (POST_STATE.DEFAULT, u'видим'),
                       (POST_STATE.REMOVED, u'удалён') )


class Post(models.Model):

    thread = models.ForeignKey(Thread, null=False)

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    updated_at = models.DateTimeField(auto_now=True, null=False, default=datetime.datetime(2000, 1, 1))

    author = models.ForeignKey('accounts.Account', null=True, related_name='+')

    text = models.TextField(null=False, blank=True, default='')

    markup_method = models.IntegerField(default=MARKUP_METHOD.POSTMARKUP, choices=MARKUP_METHOD_CHOICES, null=False)

    state = models.IntegerField(default=POST_STATE.DEFAULT, choices=POST_STATE_CHOICES)
    removed_by = models.IntegerField(default=None, null=True, choices=POST_REMOVED_BY_CHOICES)
    remove_initiator = models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+')

    technical = models.BooleanField(default=False)

    class Meta:
        permissions = (("moderate_post", u"Может редактировать сообщения пользователей"), )

    def __unicode__(self): return u'thread %d, post %d' % (self.thread_id, self.id)
