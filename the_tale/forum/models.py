# coding: utf-8
import datetime

from django.db import models
from django.core.urlresolvers import reverse

from rels.django import RelationIntegerField

from the_tale.forum.relations import MARKUP_METHOD, POST_REMOVED_BY, POST_STATE


class Category(models.Model):

    caption = models.CharField(max_length=256, blank=False, null=False)

    slug = models.CharField(max_length=32, blank=False, null=False, db_index=True)

    order = models.IntegerField(default=0, null=False, blank=True)

    def __unicode__(self): return self.slug


class SubCategory(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime.fromtimestamp(0))

    category = models.ForeignKey(Category, null=False, on_delete=models.PROTECT)

    caption = models.CharField(max_length=256, blank=False, null=False)

    order = models.IntegerField(default=0, null=False, blank=True)

    uid = models.CharField(max_length=16, blank=True, null=True, default=None, db_index=True)

    updated_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime.fromtimestamp(0))
    last_thread_created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime.fromtimestamp(0))

    threads_count = models.IntegerField(default=0, null=False)

    last_poster = models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    posts_count = models.BigIntegerField(default=0, null=False)

    closed = models.BooleanField(default=False) # if True, only staff can create themes in this subcategory
    restricted = models.BooleanField(default=False, db_index=True) # if True, permissions required to work with this subcategory

    def __unicode__(self): return self.caption


class Thread(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime.fromtimestamp(0))

    subcategory = models.ForeignKey(SubCategory, null=False, on_delete=models.PROTECT)

    caption = models.CharField(max_length=256, blank=False, null=False)

    author =  models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)

    last_poster = models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)

    posts_count = models.BigIntegerField(default=0, null=False)

    updated_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime.fromtimestamp(0))

    technical = models.BooleanField(default=False)

    important = models.BooleanField(default=False, db_index=True)

    class Meta:
        permissions = (("moderate_thread", u"Может редактировать темы на форуме"), )

    def get_absolute_url(self):
        return reverse('forum:threads:show', args=[self.id])

    def __unicode__(self): return u'%d - %s' % (self.id, self.caption)


class Subscription(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, null=True, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('account', 'thread'),
                           ('account', 'subcategory'),)

class Post(models.Model):

    thread = models.ForeignKey(Thread, null=False, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    updated_at = models.DateTimeField(auto_now=True, null=False, default=datetime.datetime.fromtimestamp(0))

    author = models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)

    text = models.TextField(null=False, blank=True, default='')

    markup_method = RelationIntegerField(relation=MARKUP_METHOD, relation_column='value')

    state = RelationIntegerField(relation=POST_STATE, relation_column='value', db_index=True)
    removed_by = RelationIntegerField(relation=POST_REMOVED_BY, relation_column='value', null=True, default=None)
    remove_initiator = models.ForeignKey('accounts.Account', null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    technical = models.BooleanField(default=False)

    class Meta:
        permissions = (("moderate_post", u"Может редактировать сообщения пользователей"), )

    def __unicode__(self): return u'thread %d, post %d' % (self.thread_id, self.id)



class ThreadReadInfo(models.Model):

    thread = models.ForeignKey(Thread, db_index=True, on_delete=models.CASCADE)

    account = models.ForeignKey('accounts.Account', related_name='+', db_index=True, on_delete=models.CASCADE)

    read_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = (('thread', 'account'),)


class SubCategoryReadInfo(models.Model):

    subcategory = models.ForeignKey(SubCategory, db_index=True, on_delete=models.CASCADE)

    account = models.ForeignKey('accounts.Account', related_name='+', db_index=True, on_delete=models.CASCADE)

    all_read_at = models.DateTimeField()
    read_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('subcategory', 'account'),)



class Permission(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    account = models.ForeignKey('accounts.Account', related_name='+', on_delete=models.CASCADE)

    class Meta:
        unique_together = (('subcategory', 'account'),)
