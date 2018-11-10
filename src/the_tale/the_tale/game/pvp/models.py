
import smart_imports

smart_imports.all()


class Battle1x1(django_models.Model):

    account = django_models.OneToOneField('accounts.Account', null=False, related_name='+', on_delete=django_models.PROTECT)
    enemy = django_models.OneToOneField('accounts.Account', null=True, related_name='+', on_delete=django_models.PROTECT)

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)
    updated_at = django_models.DateTimeField(auto_now=True, null=False)

    state = rels_django.RelationIntegerField(relation=relations.BATTLE_1X1_STATE, relation_column='value', db_index=True)

    calculate_rating = django_models.BooleanField(default=False, db_index=True)


class Battle1x1Result(django_models.Model):
    created_at = django_models.DateTimeField(auto_now_add=True, null=False)

    participant_1 = django_models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=django_models.CASCADE)
    participant_2 = django_models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=django_models.CASCADE)

    result = rels_django.RelationIntegerField(relation=relations.BATTLE_1X1_RESULT, relation_column='value', db_index=True)
