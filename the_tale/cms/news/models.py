# coding: utf-8

import markdown

from django.db import models

from the_tale.forum.models import Thread

class News(models.Model):

    caption = models.CharField(max_length=256, blank=False, null=False)

    description = models.TextField(null=False, blank=True, default='')

    content = models.TextField(null=False, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)

    forum_thread = models.ForeignKey(Thread, null=True, on_delete=models.SET_NULL)

    @property
    def html_description(self):
        return markdown.markdown(self.description)

    @property
    def html_content(self):
        return markdown.markdown(self.content)
