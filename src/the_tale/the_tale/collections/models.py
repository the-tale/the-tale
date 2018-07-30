
import smart_imports

smart_imports.all()


class Collection(django_models.Model):

    CAPTION_MAX_LENGTH = 100
    DESCRIPTION_MAX_LENGTH = 1000

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    approved = django_models.BooleanField(blank=True, default=False)

    caption = django_models.CharField(max_length=CAPTION_MAX_LENGTH)

    description = django_models.TextField(max_length=DESCRIPTION_MAX_LENGTH)

    class Meta:
        permissions = (('edit_collection', 'Может создавать и редактировать коллекции'),
                       ('moderate_collection', 'Может утверждать коллекции'),)

    def __str__(self): return self.caption


class Kit(django_models.Model):
    CAPTION_MAX_LENGTH = 100
    DESCRIPTION_MAX_LENGTH = 1000

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    approved = django_models.BooleanField(blank=True, default=False)

    collection = django_models.ForeignKey(Collection, null=False, on_delete=django_models.PROTECT)

    caption = django_models.CharField(max_length=CAPTION_MAX_LENGTH)

    description = django_models.TextField(max_length=DESCRIPTION_MAX_LENGTH)

    class Meta:
        permissions = (('edit_kit', 'Может создавать и редактировать наборы'),
                       ('moderate_kit', 'Может утверждать наборы'),)

    def __str__(self): return self.caption


class Item(django_models.Model):
    CAPTION_MAX_LENGTH = 100

    approved = django_models.BooleanField(blank=True, default=False)

    kit = django_models.ForeignKey(Kit, null=False, on_delete=django_models.PROTECT)

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    caption = django_models.CharField(max_length=CAPTION_MAX_LENGTH)

    text = django_models.TextField()

    class Meta:
        permissions = (('edit_item', 'Может создавать и редактировать предметы'),
                       ('moderate_item', 'Может утверждать предметы'),)

    def __str__(self): return self.caption


class AccountItems(django_models.Model):

    account = django_models.OneToOneField('accounts.Account', on_delete=django_models.CASCADE)

    items = django_models.TextField(default='{}')


class GiveItemTask(django_models.Model):
    account = django_models.ForeignKey('accounts.Account', null=True, on_delete=django_models.CASCADE)
    item = django_models.ForeignKey(Item, on_delete=django_models.CASCADE)
