
import smart_imports

smart_imports.all()


class SupervisorTask(django_models.Model):
    type = rels_django.RelationIntegerField(relation=relations.SUPERVISOR_TASK_TYPE)
    state = rels_django.RelationIntegerField(relation=relations.SUPERVISOR_TASK_STATE)
    created_at = django_models.DateTimeField(auto_now_add=True, null=False)


class SupervisorTaskMember(django_models.Model):
    task = django_models.ForeignKey(SupervisorTask, null=False, related_name='+', on_delete=django_models.CASCADE)
    account = django_models.ForeignKey('accounts.Account', null=False, related_name='+', on_delete=django_models.PROTECT)
