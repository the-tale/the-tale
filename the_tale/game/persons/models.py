# coding: utf-8

from django.db import models


class PERSON_TYPE:
    BLACKSMITH = 0 
    FISHERMAN = 1
    TAILOR = 2
    CARPENTER = 3
    HUNTER = 4
    WARDEN = 5
    MERCHANT = 6
    INNKEEPER = 7

PERSON_CHOICES = ( (PERSON_TYPE.BLACKSMITH, u'кузнец'),
                   (PERSON_TYPE.FISHERMAN, u'рыбак'),
                   (PERSON_TYPE.TAILOR, u'портной'),
                   (PERSON_TYPE.CARPENTER, u'плотник'),
                   (PERSON_TYPE.HUNTER, u'охотник'),
                   (PERSON_TYPE.WARDEN, u'стражник'),
                   (PERSON_TYPE.MERCHANT, u'торговец'),
                   (PERSON_TYPE.INNKEEPER, u'трактирщик') )

PERSON_DICT = dict(PERSON_CHOICES)


class Person(models.Model):

    place = models.ForeignKey('places.Place', related_name='persons')

    name = models.CharField(max_length=256)

    type = models.IntegerField(max_length=256, choices=PERSON_CHOICES)

    power = models.IntegerField(default=0)
