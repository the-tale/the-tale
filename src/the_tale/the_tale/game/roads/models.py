
import smart_imports

smart_imports.all()


class Road(django_models.Model):

    point_1 = django_models.ForeignKey('places.Place', related_name='+', on_delete=django_models.CASCADE)
    point_2 = django_models.ForeignKey('places.Place', related_name='+', on_delete=django_models.CASCADE)

    length = django_models.FloatField(blank=True, default=0.0)

    path = django_models.TextField(null=False, default='')

    class Meta:
        unique_together = (('point_1', 'point_2'), )

    def __str__(self):
        return '%s -> %s' % (self.point_1, self.point_2)
