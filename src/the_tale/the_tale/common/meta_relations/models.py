
import smart_imports

smart_imports.all()


class Relation(django_models.Model):
    relation = django_models.IntegerField(db_index=True)

    from_type = django_models.IntegerField()
    from_object = django_models.BigIntegerField()

    to_type = django_models.IntegerField()
    to_object = django_models.BigIntegerField()

    class Meta:
        index_together = (('from_type', 'from_object'),
                          ('to_type', 'to_object'))
