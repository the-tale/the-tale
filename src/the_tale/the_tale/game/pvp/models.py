
import smart_imports

smart_imports.all()


class Battle1x1Result(django_models.Model):
    created_at = django_models.DateTimeField(auto_now_add=True, null=False)

    participant_1 = django_models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=django_models.CASCADE)
    participant_2 = django_models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=django_models.CASCADE)

    result = rels_django.RelationIntegerField(relation=relations.BATTLE_1X1_RESULT, relation_column='value', db_index=True)
