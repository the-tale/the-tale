
import smart_imports

smart_imports.all()


class History(django_models.Model):

    MAX_NAME_LENGHT = 64

    created_at = django_models.DateTimeField(auto_now_add=True)
    updated_at = django_models.DateTimeField(auto_now=True)

    started_at = django_models.DateTimeField(null=True)
    finished_at = django_models.DateTimeField(null=True)

    state = rels_django.RelationIntegerField(relation=relations.STATE, relation_column='value')
    result = rels_django.RelationIntegerField(relation=relations.RESULT, relation_column='value', null=True)

    name = django_models.CharField(max_length=MAX_NAME_LENGHT)

    data = django_models.JSONField()

    class Meta:
        index_together = (('name', 'state'),)
