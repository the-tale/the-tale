# coding: utf-8

from django.db import models

class PROPERTIES:
    CASES = (u'им', u'рд', u'дт', u'вн', u'тв', u'пр')
    ANIMACYTIES = (u'од', u'но')
    NUMBERS = (u'ед', u'мн')
    GENDERS = (u'мр', u'жр', u'ср')
    TIMES = (u'нст', u'прш', u'буд')
    PERSONS = (u'1л', u'2л', u'3л')


class WORD_TYPE:
    NOUN = 1
    ADJECTIVE = 2
    VERB = 3
    NUMERAL = 4

WORD_TYPE_CHOICES = ( (WORD_TYPE.NOUN, u'существительное'),
                      (WORD_TYPE.ADJECTIVE, u'прилагательное'),
                      (WORD_TYPE.VERB, u'глагол'),
                      (WORD_TYPE.NUMERAL, u'числительное') )


class Word(models.Model):

    normalized = models.CharField(max_length=32, unique=True, db_index=True)

    type = models.IntegerField(choices=WORD_TYPE_CHOICES)

    forms = models.TextField()

    properties = models.CharField(max_length=16)
