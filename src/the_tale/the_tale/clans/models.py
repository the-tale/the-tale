
import smart_imports

smart_imports.all()


class Clan(django_models.Model):

    MAX_NAME_LENGTH = 128
    MIN_NAME_LENGTH = 5
    MAX_ABBR_LENGTH = 5
    MIN_ABBR_LENGTH = 2
    MAX_MOTTO_LENGTH = 256
    MAX_DESCRIPTION_LENGTH = 2024

    created_at = django_models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = django_models.DateTimeField(auto_now=True, db_index=True)

    state = rels_django.RelationIntegerField(relation=relations.STATE,
                                             relation_column='value',
                                             default=relations.STATE.ACTIVE.value)

    name = django_models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    abbr = django_models.CharField(max_length=MAX_ABBR_LENGTH, unique=True)

    motto = django_models.CharField(max_length=MAX_MOTTO_LENGTH)
    description = django_models.TextField(max_length=MAX_DESCRIPTION_LENGTH)

    members_number = django_models.IntegerField()
    active_members_number = django_models.IntegerField(default=0)
    premium_members_number = django_models.IntegerField(default=0)

    might = django_models.FloatField(default=0.0)

    forum_subcategory = django_models.ForeignKey('forum.SubCategory', null=True, on_delete=django_models.SET_NULL)

    statistics_refreshed_at = django_models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '[%s] %s' % (self.abbr, self.name)

    class Meta:
        permissions = (("moderate_clan", "Может редактировать кланы и т.п."), )


class Membership(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True)
    updated_at = django_models.DateTimeField(auto_now=True)

    clan = django_models.ForeignKey(Clan, on_delete=django_models.PROTECT)
    account = django_models.OneToOneField('accounts.Account', on_delete=django_models.PROTECT)

    role = rels_django.RelationIntegerField(relation=relations.MEMBER_ROLE, relation_column='value')


class MembershipRequest(django_models.Model):

    MAX_TEXT_LENGTH = 1024

    created_at = django_models.DateTimeField(auto_now_add=True)
    updated_at = django_models.DateTimeField(auto_now=True)

    clan = django_models.ForeignKey(Clan, on_delete=django_models.CASCADE)
    account = django_models.ForeignKey('accounts.Account', related_name='+', on_delete=django_models.CASCADE)

    initiator = django_models.ForeignKey('accounts.Account', related_name='+', on_delete=django_models.CASCADE)

    type = rels_django.RelationIntegerField(relation=relations.MEMBERSHIP_REQUEST_TYPE, relation_column='value')

    text = django_models.TextField(max_length=MAX_TEXT_LENGTH)

    class Meta:
        unique_together = (('clan', 'account'), )
