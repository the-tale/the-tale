# coding: utf-8


from django.db import models


class Section(models.Model):

    CAPTION_MAX_LENGTH = 100
    DESCRIPTION_MAX_LENGTH = 1000

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    approved = models.BooleanField(blank=True, default=False)

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)

    description = models.TextField(max_length=DESCRIPTION_MAX_LENGTH)

    class Meta:
        permissions = (('edit_section', u'Может создавать и редактировать разделы'),
                       ('moderate_section', u'Может утверждать разделы'),)


class Kit(models.Model):
    CAPTION_MAX_LENGTH = 100
    DESCRIPTION_MAX_LENGTH = 1000

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    approved = models.BooleanField(blank=True, default=False)

    section = models.ForeignKey(Section, null=False, on_delete=models.PROTECT)

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)

    description = models.TextField(max_length=DESCRIPTION_MAX_LENGTH)

    class Meta:
        permissions = (('edit_kit', u'Может создавать и редактировать наборы'),
                       ('moderate_kit', u'Может утверждать наборы'),)


class Reward(models.Model):
    CAPTION_MAX_LENGTH = 100

    approved = models.BooleanField(blank=True, default=False)

    kit = models.ForeignKey(Kit, null=False, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)

    text = models.TextField()

    class Meta:
        permissions = (('edit_reward', u'Может создавать и редактировать награды'),
                       ('moderate_reward', u'Может утверждать награды'),)
