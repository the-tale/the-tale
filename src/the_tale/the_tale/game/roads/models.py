
import smart_imports

smart_imports.all()


class Road(django_models.Model):

    point_1 = django_models.ForeignKey('places.Place', related_name='+', on_delete=django_models.CASCADE)
    point_2 = django_models.ForeignKey('places.Place', related_name='+', on_delete=django_models.CASCADE)

    length = django_models.FloatField(blank=True, default=0.0)

    exists = django_models.BooleanField(default=True)

    path = django_models.TextField(null=False, default='')

    class Meta:
        unique_together = (('point_1', 'point_2'), )

    def __str__(self):
        return '%s -> %s' % (self.point_1, self.point_2)


class Waymark(django_models.Model):

    point_from = django_models.ForeignKey('places.Place', related_name='+', on_delete=django_models.CASCADE)
    point_to = django_models.ForeignKey('places.Place', related_name='+', on_delete=django_models.CASCADE)

    road = django_models.ForeignKey(Road, null=True, related_name='+', on_delete=django_models.SET_NULL)

    length = django_models.FloatField(blank=True, default=0.0)

    class Meta:
        unique_together = (('point_from', 'point_to', 'road'), )
