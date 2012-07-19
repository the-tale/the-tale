# coding: utf-8

from django.db import models

from game.game_info import RACE, RACE_CHOICES, GENDER, GENDER_CHOICES


class PERSON_TYPE:
    BLACKSMITH = 0
    FISHERMAN = 1
    TAILOR = 2
    CARPENTER = 3
    HUNTER = 4
    WARDEN = 5
    MERCHANT = 6
    INNKEEPER = 7

PERSON_TYPE_CHOICES = ( (PERSON_TYPE.BLACKSMITH, u'кузнец'),
                        (PERSON_TYPE.FISHERMAN, u'рыбак'),
                        (PERSON_TYPE.TAILOR, u'портной'),
                        (PERSON_TYPE.CARPENTER, u'плотник'),
                        (PERSON_TYPE.HUNTER, u'охотник'),
                        (PERSON_TYPE.WARDEN, u'стражник'),
                        (PERSON_TYPE.MERCHANT, u'торговец'),
                        (PERSON_TYPE.INNKEEPER, u'трактирщик') )

PERSON_TYPE_DICT = dict(PERSON_TYPE_CHOICES)


class PERSON_STATE:
    IN_GAME = 0
    OUT_GAME = 1

PERSON_STATE_CHOICES = ( (PERSON_STATE.IN_GAME, u'в игре'),
                         (PERSON_STATE.OUT_GAME, u'вне игры'))


class Person(models.Model):

    place = models.ForeignKey('places.Place', related_name='persons')

    state = models.IntegerField(default=PERSON_STATE.IN_GAME, choices=PERSON_STATE_CHOICES)

    name = models.CharField(max_length=256)

    gender = models.IntegerField(null=False, default=GENDER.MASCULINE, choices=GENDER_CHOICES)

    race = models.IntegerField(choices=RACE_CHOICES, default=RACE.HUMAN)

    type = models.IntegerField(choices=PERSON_TYPE_CHOICES)

    power = models.IntegerField(default=0)
