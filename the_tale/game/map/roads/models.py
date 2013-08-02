# coding: utf-8

from django.db import models

class Road(models.Model):

    point_1 = models.ForeignKey('places.Place', related_name='+', on_delete=models.CASCADE)
    point_2 = models.ForeignKey('places.Place', related_name='+', on_delete=models.CASCADE)

    length = models.FloatField(blank=True, default=0.0)

    exists = models.BooleanField(default=True)

    path = models.TextField(null=False, default='')

    class Meta:
        unique_together = (('point_1', 'point_2'), )

    def __unicode__(self):
        return u'%s -> %s' % (self.point_1, self.point_2)


class Waymark(models.Model):

    point_from = models.ForeignKey('places.Place', related_name='+', on_delete=models.CASCADE)
    point_to = models.ForeignKey('places.Place', related_name='+', on_delete=models.CASCADE)

    road = models.ForeignKey(Road, null=True, related_name='+', on_delete=models.SET_NULL)

    length = models.FloatField(blank=True, default=0.0)

    class Meta:
        unique_together = (('point_from', 'point_to', 'road'), )
