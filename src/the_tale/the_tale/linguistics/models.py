
import smart_imports

smart_imports.all()


class Word(django_models.Model):
    MAX_FORM_LENGTH = 64

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now_add=True, null=False)

    author = django_models.ForeignKey(django_settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=django_models.SET_NULL)
    parent = django_models.OneToOneField('linguistics.Word', null=True, blank=True, on_delete=django_models.SET_NULL)

    normal_form = django_models.CharField(max_length=MAX_FORM_LENGTH)
    forms = django_models.TextField(db_index=True)

    state = rels_django.RelationIntegerField(relation=relations.WORD_STATE, db_index=True)
    type = rels_django.RelationIntegerField(relation=utg_relations.WORD_TYPE, db_index=True, choices=[(record, record.text) for record in utg_relations.WORD_TYPE.records])

    used_in_ingame_templates = django_models.IntegerField(default=0)
    used_in_onreview_templates = django_models.IntegerField(default=0)
    used_in_status = rels_django.RelationIntegerField(relation=relations.WORD_USED_IN_STATUS, db_index=True)

    class Meta:
        unique_together = (('normal_form', 'type', 'state'),)
        permissions = (("moderate_word", "Может модерировать слова"), )


class Template(django_models.Model):
    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now_add=True, null=False)

    author = django_models.ForeignKey(django_settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=django_models.SET_NULL)
    parent = django_models.OneToOneField('linguistics.Template', null=True, blank=True, on_delete=django_models.SET_NULL)

    raw_template = django_models.TextField(db_index=True)
    data = django_models.TextField()

    state = rels_django.RelationIntegerField(relation=relations.TEMPLATE_STATE, db_index=True)
    key = rels_django.RelationIntegerField(relation=lexicon_keys.LEXICON_KEY, db_index=True)

    errors_status = rels_django.RelationIntegerField(relation=relations.TEMPLATE_ERRORS_STATUS, default=0, db_index=True)

    class Meta:
        permissions = (("moderate_template", "Может модерировать шаблоны фраз"),
                       ("edit_template", "Может редактировать шаблоны фраз"), )


class Contribution(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False, db_index=True)
    account = django_models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=django_models.CASCADE)

    state = rels_django.RelationIntegerField(relation=relations.CONTRIBUTION_STATE, db_index=True)
    type = rels_django.RelationIntegerField(relation=relations.CONTRIBUTION_TYPE, db_index=True)
    source = rels_django.RelationIntegerField(relation=relations.CONTRIBUTION_SOURCE, db_index=True)

    # if entity_id < 0 it is id of old phrase_candidate entity
    entity_id = django_models.BigIntegerField(db_index=True)

    reward_given = django_models.BooleanField(default=False)

    class Meta:
        unique_together = (('type', 'account', 'entity_id'),)


class Restriction(django_models.Model):
    MAX_NAME_LENGTH = 128

    created_at = django_models.DateTimeField(auto_now_add=True, null=False, db_index=True)

    name = django_models.CharField(max_length=MAX_NAME_LENGTH)

    group = rels_django.RelationIntegerField(relation=restrictions.GROUP, db_index=True)
    external_id = django_models.BigIntegerField(db_index=True)

    class Meta:
        unique_together = (('group', 'external_id'),)


class TemplateRestriction(django_models.Model):

    restriction = django_models.ForeignKey(Restriction, on_delete=django_models.CASCADE)
    template = django_models.ForeignKey(Template, on_delete=django_models.CASCADE)
    variable = django_models.CharField(max_length=32, db_index=True)

    class Meta:
        unique_together = (('restriction', 'template', 'variable'),)
