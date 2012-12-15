# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

POST_STATE = create_enum('POST_STATE', (('NOT_MODERATED', 0, u'не проверен'),
                                        ('ACCEPTED', 1, u'принят'),
                                        ('DECLINED', 2, u'отклонён'),))

class Post(models.Model):

    CAPTION_MIN_LENGTH = 10
    CAPTION_MAX_LENGTH = 256

    author = models.ForeignKey('accounts.Account', null=False, related_name='+')

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)
    text = models.TextField(null=False, blank=True, default='')

    state = models.IntegerField(default=POST_STATE.NOT_MODERATED, choices=POST_STATE.CHOICES)

    moderator = models.ForeignKey('accounts.Account', null=True, related_name='+')

    votes = models.IntegerField(default=0)

    class Meta:
        permissions = (("moderate_post", u"Может редактировать сообщения пользователей"), )


class Vote(models.Model):

    voter = models.ForeignKey('accounts.Account', null=False, related_name='+')
    post = models.ForeignKey(Post, null=False, related_name='+')

    created_at = models.DateTimeField(auto_now_add=True, null=False)

    value = models.BooleanField()

    class Meta:
        unique_together = (('voter', 'post'),)
