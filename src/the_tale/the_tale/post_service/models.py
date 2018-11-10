
import smart_imports

smart_imports.all()


class Message(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    processed_at = django_models.DateTimeField(null=True, blank=True)

    state = rels_django.RelationIntegerField(relation=relations.MESSAGE_STATE, relation_column='value', db_index=True)

    handler = django_models.TextField(default='')
