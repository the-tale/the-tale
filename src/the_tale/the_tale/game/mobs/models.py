
import smart_imports

smart_imports.all()


class MobRecord(django_models.Model):

    MAX_UUID_LENGTH = 32
    MAX_NAME_LENGTH = 32

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    editor = django_models.ForeignKey('accounts.Account', null=True, related_name='+', on_delete=django_models.SET_NULL)

    state = rels_django.RelationIntegerField(relation=relations.MOB_RECORD_STATE, db_index=True)
    type = rels_django.RelationIntegerField(relation=tt_beings_relations.TYPE, db_index=True)

    is_mercenary = django_models.BooleanField(default=False)
    is_eatable = django_models.BooleanField(default=False)

    archetype = rels_django.RelationIntegerField(relation=game_relations.ARCHETYPE, db_index=True)

    level = django_models.IntegerField(default=0)

    uuid = django_models.CharField(max_length=MAX_UUID_LENGTH, unique=True)

    name = django_models.CharField(max_length=MAX_NAME_LENGTH, unique=True, null=False, db_index=True)

    description = django_models.TextField(null=False, default='')

    abilities = django_models.TextField(null=False)

    terrains = django_models.TextField(null=False)

    data = django_models.TextField(null=False, default='{}')

    communication_verbal = rels_django.RelationIntegerField(relation=tt_beings_relations.COMMUNICATION_VERBAL, db_index=True)
    communication_gestures = rels_django.RelationIntegerField(relation=tt_beings_relations.COMMUNICATION_GESTURES, db_index=True)
    communication_telepathic = rels_django.RelationIntegerField(relation=tt_beings_relations.COMMUNICATION_TELEPATHIC, db_index=True)

    intellect_level = rels_django.RelationIntegerField(relation=tt_beings_relations.INTELLECT_LEVEL, db_index=True)

    class Meta:
        permissions = (("create_mobrecord", "Может предлагать мобов"),
                       ("moderate_mobrecord", "Может утверждать мобов"),)
