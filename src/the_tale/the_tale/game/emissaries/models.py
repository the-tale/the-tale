
import smart_imports

smart_imports.all()


class Emissary(django_models.Model):
    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    clan = django_models.ForeignKey('clans.Clan', related_name='+', on_delete=django_models.PROTECT)

    place = django_models.ForeignKey('places.Place', related_name='+', on_delete=django_models.PROTECT)

    state = rels_django.RelationIntegerField(relation=relations.STATE, db_index=True)

    data = django_models.JSONField()


class Event(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    emissary = django_models.ForeignKey(Emissary, related_name='+', on_delete=django_models.PROTECT)

    state = rels_django.RelationIntegerField(relation=relations.EVENT_STATE, db_index=True)

    data = django_models.JSONField()

    stop_reason = rels_django.RelationIntegerField(relation=relations.EVENT_STOP_REASON, db_index=True)
