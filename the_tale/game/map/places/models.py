from django.db import models

class Place(models.Model):

    x = models.BigIntegerField(null=False)
    y = models.BigIntegerField(null=False)

    name = models.CharField(max_length=150, null=False)

    type = models.CharField(max_length=50, 
                            choices=( ('UNDEFINED', 'undefined'), ), 
                            null=False) # city, dungeong, special-place (specify where to search)

    subtype = models.CharField(max_length=50, 
                               choices=( ('UNDEFINED', 'undefined'), ), 
                               null=False) # orc city, goblin dungeon (specify how to display)

    size = models.IntegerField(null=False) # specify size of the place



class HeroPosition(models.Model):

    place = models.ForeignKey(Place, related_name='positions', null=True, default=None, blank=True)

    road = models.ForeignKey('roads.road', related_name='positions', null=True, default=None, blank=True)
    percents = models.FloatField(null=True, default=None, blank=True)
    invert_direction = models.NullBooleanField(default=False, null=True, blank=True)

    hero = models.OneToOneField('heroes.Hero', related_name='position')
