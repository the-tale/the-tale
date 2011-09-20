from django.db import models

from game.angels.models import Angel

class Hero(models.Model):

    angel = models.ForeignKey(Angel, related_name='heroes', default=None, null=True, blank=True)

    alive = models.BooleanField(default=True)

    #base
    first = models.BooleanField()

    name = models.CharField(max_length=150, null=False)


    wisdom = models.IntegerField()

    health = models.FloatField(null=False, default=0.0)

    money = models.BigIntegerField(null=False, default=0)

    equipment = models.TextField(null=False, default='{}')
    bag = models.TextField(null=False, default='{}')

    #primary
    intellect = models.IntegerField()
    constitution = models.IntegerField()
    reflexes = models.IntegerField()
    charisma = models.IntegerField(default=3)
    chaoticity = models.IntegerField()

    #position
    pos_place = models.ForeignKey('places.Place', related_name='+', null=True, default=None, blank=True)
    pos_road = models.ForeignKey('roads.Road', related_name='+', null=True, default=None, blank=True)
    pos_percents = models.FloatField(null=True, default=None, blank=True)
    pos_invert_direction = models.NullBooleanField(default=False, null=True, blank=True)

    @classmethod
    def get_related_query(cls):
        return cls.objects.select_related('pos_place', 'pos_road')

    def __unicode__(self):
        return u'hero[%d] - %s' % (self.id, self.name)
