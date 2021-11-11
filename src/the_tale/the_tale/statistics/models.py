
import smart_imports

smart_imports.all()


class Record(django_models.Model):

    date = django_models.DateTimeField(null=False)
    type = rels_django.RelationIntegerField(relation=relations.RECORD_TYPE, db_index=True)

    value_int = django_models.BigIntegerField()
    value_float = django_models.FloatField()


class FullStatistics(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True)

    data = django_models.JSONField()
