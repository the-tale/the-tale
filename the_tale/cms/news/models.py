# coding: utf-8

import markdown

from django.db import models

from forum.models import Thread

class News(models.Model):

    caption = models.CharField(max_length=256, blank=False, null=False)

    description = models.TextField(null=False, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    forum_thread = models.ForeignKey(Thread, null=True)
    
    @property
    def html_description(self):
        return markdown.markdown(self.description)
