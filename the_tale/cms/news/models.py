# coding: utf-8

from django.db import models

from rels.django import RelationIntegerField

from the_tale.forum.models import Thread

from the_tale.cms.news import relations


class News(models.Model):

    caption = models.CharField(max_length=256, blank=False, null=False)

    description = models.TextField(null=False, blank=True, default='')

    content = models.TextField(null=False, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)

    forum_thread = models.ForeignKey(Thread, null=True, on_delete=models.SET_NULL)

    emailed = RelationIntegerField(relation=relations.EMAILED_STATE, db_index=True)

    class Meta:
        permissions = (("edit_news", u"Может создавать новости"), )
        get_latest_by = 'created_at'
