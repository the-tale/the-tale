
import smart_imports

smart_imports.all()


class WorldInfo(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True)

    data = django_models.TextField(null=False, default='', blank=True)


class MapInfo(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, null=False)

    turn_number = django_models.BigIntegerField(null=False, db_index=True)

    width = django_models.IntegerField(null=False)
    height = django_models.IntegerField(null=False)

    terrain = django_models.TextField(null=False, default='[]')

    cells = django_models.TextField(null=False, default='')

    world = django_models.ForeignKey(WorldInfo, null=False, related_name='+', on_delete=django_models.CASCADE)

    statistics = django_models.TextField(null=False, default='{}')


class MapRegion(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True, db_index=True)

    turn_number = django_models.BigIntegerField(null=False, unique=True)

    data = django_postgres_fields.JSONField()

    class Meta:
        index_together = (('turn_number', 'created_at'),)
