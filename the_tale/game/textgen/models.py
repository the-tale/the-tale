# coding: utf-8

from django.db import models

class PROPERTIES:
    CASES = (u'им', u'рд', u'дт', u'вн', u'тв', u'пр')
    ANIMACYTIES = (u'од', u'но')
    NUMBERS = (u'ед', u'мн')
    GENDERS = (u'жр', u'ср', u'мр')
    TIMES = (u'нст', u'прш', u'буд')


class WORD_TYPE:
    NOUN = 1

WORD_TYPE_CHOICES = ( (WORD_TYPE.NOUN, u'существительное'), )


class Word(models.Model):

    normalized = models.CharField(max_length=32, unique=True, db_index=True)

    type = models.IntegerField(choices=WORD_TYPE_CHOICES)

    forms = models.TextField()

    properties = models.CharField(max_length=16)
