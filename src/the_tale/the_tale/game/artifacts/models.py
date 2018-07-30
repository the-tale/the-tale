
import smart_imports

smart_imports.all()


class ArtifactRecord(django_models.Model):

    MAX_UUID_LENGTH = 32
    MAX_NAME_LENGTH = 32

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    editor = django_models.ForeignKey('accounts.Account', null=True, related_name='+', blank=True, on_delete=django_models.SET_NULL)

    type = rels_django.RelationIntegerField(relation=relations.ARTIFACT_TYPE, relation_column='value')
    power_type = rels_django.RelationIntegerField(relation=relations.ARTIFACT_POWER_TYPE, relation_column='value')
    state = rels_django.RelationIntegerField(relation=relations.ARTIFACT_RECORD_STATE, relation_column='value')

    rare_effect = rels_django.RelationIntegerField(relation=relations.ARTIFACT_EFFECT, relation_column='value')
    epic_effect = rels_django.RelationIntegerField(relation=relations.ARTIFACT_EFFECT, relation_column='value')

    special_effect = rels_django.RelationIntegerField(relation=relations.ARTIFACT_EFFECT, relation_column='value', default=relations.ARTIFACT_EFFECT.NO_EFFECT.value)

    level = django_models.IntegerField(default=0)

    uuid = django_models.CharField(max_length=MAX_UUID_LENGTH, unique=True)

    name = django_models.CharField(max_length=MAX_NAME_LENGTH, unique=True, null=False, db_index=True)

    description = django_models.TextField(null=False, default='', blank=True)

    mob = django_models.ForeignKey('mobs.MobRecord', null=True, related_name='+', blank=True, on_delete=django_models.SET_NULL)

    data = django_models.TextField(null=False, default='{}')

    class Meta:
        permissions = (("create_artifactrecord", "Может предлагать артефакты"),
                       ("moderate_artifactrecord", "Может утверждать артефакты"),)
