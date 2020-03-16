
import smart_imports

smart_imports.all()


class LockRequest(django_models.Model):

    MAX_NAME_LENGTH = 64

    created_at = django_models.DateTimeField(auto_now_add=True)
    updated_at = django_models.DateTimeField(auto_now=True)

    state = rels_django.RelationIntegerField(relation=relations.STATE, relation_column='value')

    name = django_models.CharField(max_length=MAX_NAME_LENGTH, db_index=True)

    data = django_postgres_fields.JSONField()
