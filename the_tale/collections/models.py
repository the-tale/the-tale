# coding: utf-8


from django.db import models


class Collection(models.Model):

    CAPTION_MAX_LENGTH = 100
    DESCRIPTION_MAX_LENGTH = 1000

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    approved = models.BooleanField(blank=True, default=False)

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)

    description = models.TextField(max_length=DESCRIPTION_MAX_LENGTH)

    class Meta:
        permissions = (('edit_collection', u'Может создавать и редактировать коллекции'),
                       ('moderate_collection', u'Может утверждать коллекции'),)

    def __unicode__(self): return self.caption


class Kit(models.Model):
    CAPTION_MAX_LENGTH = 100
    DESCRIPTION_MAX_LENGTH = 1000

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    approved = models.BooleanField(blank=True, default=False)

    collection = models.ForeignKey(Collection, null=False, on_delete=models.PROTECT)

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)

    description = models.TextField(max_length=DESCRIPTION_MAX_LENGTH)

    class Meta:
        permissions = (('edit_kit', u'Может создавать и редактировать наборы'),
                       ('moderate_kit', u'Может утверждать наборы'),)

    def __unicode__(self): return self.caption


class Item(models.Model):
    CAPTION_MAX_LENGTH = 100

    approved = models.BooleanField(blank=True, default=False)

    kit = models.ForeignKey(Kit, null=False, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    caption = models.CharField(max_length=CAPTION_MAX_LENGTH)

    text = models.TextField()

    class Meta:
        permissions = (('edit_item', u'Может создавать и редактировать предметы'),
                       ('moderate_item', u'Может утверждать предметы'),)

    def __unicode__(self): return self.caption



class AccountItems(models.Model):

    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, unique=True)

    items = models.TextField(default='{}')


class GiveItemTask(models.Model):
    account = models.ForeignKey('accounts.Account', null=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
