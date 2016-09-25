# coding: utf-8

from django.db import models


class Friendship(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    friend_1 = models.ForeignKey('accounts.Account', related_name='+', on_delete=models.CASCADE)
    friend_2 = models.ForeignKey('accounts.Account', related_name='+', on_delete=models.CASCADE)

    text = models.TextField(default=u'Давайте дружить')

    is_confirmed = models.BooleanField(default=False, db_index=True)
