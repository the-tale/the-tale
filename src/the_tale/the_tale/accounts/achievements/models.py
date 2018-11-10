
import smart_imports

smart_imports.all()


class Achievement(django_models.Model):

    CAPTION_MAX_LENGTH = 128
    DESCRIPTION_MAX_LENGTH = 1024

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    group = rels_django.RelationIntegerField(relation=relations.ACHIEVEMENT_GROUP, db_index=True)
    type = rels_django.RelationIntegerField(relation=relations.ACHIEVEMENT_TYPE, db_index=True)

    caption = django_models.CharField(max_length=CAPTION_MAX_LENGTH)
    description = django_models.CharField(max_length=DESCRIPTION_MAX_LENGTH)

    order = django_models.IntegerField()

    approved = django_models.BooleanField(default=False)

    barrier = django_models.IntegerField()

    points = django_models.IntegerField()

    item_1 = django_models.ForeignKey('collections.Item', null=True, default=None, related_name='+', on_delete=django_models.SET_NULL)
    item_2 = django_models.ForeignKey('collections.Item', null=True, default=None, related_name='+', on_delete=django_models.SET_NULL)
    item_3 = django_models.ForeignKey('collections.Item', null=True, default=None, related_name='+', on_delete=django_models.SET_NULL)

    class Meta:
        permissions = (('edit_achievement', 'Может создавать и редактировать достижения'),)


class AccountAchievements(django_models.Model):

    account = django_models.OneToOneField('accounts.Account', on_delete=django_models.CASCADE)

    achievements = django_models.TextField(default='{}')

    points = django_models.IntegerField(default=0)


class GiveAchievementTask(django_models.Model):
    account = django_models.ForeignKey('accounts.Account', null=True, on_delete=django_models.CASCADE)
    achievement = django_models.ForeignKey(Achievement, on_delete=django_models.CASCADE)
