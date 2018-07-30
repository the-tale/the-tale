
import smart_imports

smart_imports.all()


class CompanionRecord(django_models.Model):
    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    state = rels_django.RelationIntegerField(relation=relations.STATE, db_index=True)
    dedication = rels_django.RelationIntegerField(relation=relations.DEDICATION, db_index=True)
    archetype = rels_django.RelationIntegerField(relation=game_relations.ARCHETYPE, blank=True)
    mode = rels_django.RelationIntegerField(relation=relations.MODE, blank=True)

    type = rels_django.RelationIntegerField(relation=tt_beings_relations.TYPE, db_index=True)

    communication_verbal = rels_django.RelationIntegerField(relation=tt_beings_relations.COMMUNICATION_VERBAL, db_index=True)
    communication_gestures = rels_django.RelationIntegerField(relation=tt_beings_relations.COMMUNICATION_GESTURES, db_index=True)
    communication_telepathic = rels_django.RelationIntegerField(relation=tt_beings_relations.COMMUNICATION_TELEPATHIC, db_index=True)

    intellect_level = rels_django.RelationIntegerField(relation=tt_beings_relations.INTELLECT_LEVEL, db_index=True)

    max_health = django_models.IntegerField(default=1)

    data = django_models.TextField(null=False, default='{}')

    class Meta:
        permissions = (("create_companionrecord", "Может создавать спутников"),
                       ("moderate_companionrecord", "Может утверждать спутников"),)
