# coding: utf-8

import markdown

from django.db import models

from cms.conf import cms_settings


SECTIONS_CHOICES = [(section.id, section.caption) for section in cms_settings.SECTIONS]

SECTIONS_DICT = dict([(section.id, section) for section in cms_settings.SECTIONS])


class Page(models.Model):

    section = models.CharField(max_length=16, default=None, choices=SECTIONS_CHOICES, db_index=True)

    slug = models.CharField(max_length=256, default='', blank=True, db_index=True)

    caption = models.CharField(max_length=256, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, null=False, db_index=True)

    author = models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=models.SET_NULL)
    editor = models.ForeignKey('accounts.Account', null=True, default=None, related_name='+', on_delete=models.SET_NULL)

    description = models.TextField(null=False, blank=False, default='')

    content = models.TextField(null=False, blank=False, default='')

    order = models.IntegerField(default=None, blank=True, db_index=True)

    active = models.BooleanField(default=False)

    class Meta:
        unique_together = (('section', 'slug'), ('section', 'order'))

    def get_section(self):
        return SECTIONS_DICT[self.section]

    @property
    def html_content(self):
        return markdown.markdown(self.content)
