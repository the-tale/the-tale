
import smart_imports

smart_imports.all()


class AccessToken(django_models.Model):
    APPLICATION_NAME_MAX_LENGTH = 100
    APPLICATION_INFO_MAX_LENGTH = 100

    created_at = django_models.DateTimeField(auto_now_add=True)
    updated_at = django_models.DateTimeField(auto_now=True)

    account = django_models.ForeignKey('accounts.Account', null=True, default=None, on_delete=django_models.CASCADE)

    uid = utils_models.UUIDField(unique=True, db_index=True)

    application_name = django_models.CharField(max_length=APPLICATION_NAME_MAX_LENGTH)

    application_info = django_models.CharField(max_length=APPLICATION_INFO_MAX_LENGTH)

    application_description = django_models.TextField()

    state = rels_django.RelationIntegerField(relation=relations.ACCESS_TOKEN_STATE)
