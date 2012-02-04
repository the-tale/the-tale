# coding: utf-8
import datetime
import postmarkup

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Category(models.Model):

    caption = models.CharField(max_length=256, blank=False, null=False)

    slug = models.CharField(max_length=32, blank=False, null=False, db_index=True)

    order = models.IntegerField(default=0, null=False, blank=True)

    def __unicode__(self): return self.slug


class SubCategory(models.Model):
    
    category = models.ForeignKey(Category, null=False)

    slug = models.CharField(max_length=32, blank=False, null=False, db_index=True)

    caption = models.CharField(max_length=256, blank=False, null=False)

    order = models.IntegerField(default=0, null=False, blank=True)

    updated_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))    

    threads_count = models.IntegerField(default=0, null=False)

    posts_count = models.BigIntegerField(default=0, null=False)

    closed = models.BooleanField(default=False) # if True, only staff can create themes in this subcategory

    def __unicode__(self): return self.slug


class Thread(models.Model):
    
    subcategory = models.ForeignKey(SubCategory, null=False)

    caption = models.CharField(max_length=256, blank=False, null=False)

    author =  models.ForeignKey(User, null=True)

    posts_count = models.BigIntegerField(default=0, null=False)

    updated_at = models.DateTimeField(auto_now_add=True, null=False, default=datetime.datetime(2000, 1, 1))

    def get_absolute_url(self):
        return reverse('forum:show_thread', args=[self.subcategory.category.slug,
                                                  self.subcategory.slug, 
                                                  self.id])        


class Post(models.Model):

    thread = models.ForeignKey(Thread, null=False)

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    author = models.ForeignKey(User, null=True)

    text = models.TextField(null=False, blank=True, default='')

    @property
    def html(self):
        return postmarkup.render_bbcode(self.text)
