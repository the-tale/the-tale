from django.db import models

class Road(models.Model):

    point_1 = models.ForeignKey('places.Place', related_name='+') 
    point_2 = models.ForeignKey('places.Place', related_name='+') 
    
    length = models.FloatField()

    class Meta:
        unique_together = (('point_1', 'point_2'), )
