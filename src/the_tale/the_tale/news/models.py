
import smart_imports

smart_imports.all()


class News(django_models.Model):

    caption = django_models.CharField(max_length=256, blank=False, null=False)

    description = django_models.TextField(null=False, blank=True, default='')

    content = django_models.TextField(null=False, blank=True, default='')

    created_at = django_models.DateTimeField(auto_now_add=True, null=False, db_index=True)

    forum_thread = django_models.ForeignKey(forum_models.Thread, null=True, on_delete=django_models.SET_NULL)

    emailed = rels_django.RelationIntegerField(relation=relations.EMAILED_STATE, db_index=True)

    class Meta:
        permissions = (("edit_news", "Может создавать новости"), )
        get_latest_by = 'created_at'
