# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

from game.game_info import RACE, GENDER


PERSON_TYPE = create_enum('PERSON_TYPE', ( ('BLACKSMITH', 0, u'кузнец'),
                                           ('FISHERMAN', 1, u'рыбак'),
                                           ('TAILOR', 2, u'портной'),
                                           ('CARPENTER', 3, u'плотник'),
                                           ('HUNTER', 4, u'охотник'),
                                           ('WARDEN', 5, u'стражник'),
                                           ('MERCHANT', 6, u'торговец'),
                                           ('INNKEEPER', 7, u'трактирщик'),
                                           ('ROGUE', 8, u'вор'),
                                           ('FARMER', 9, u'фермер'),
                                           ('MINER', 10, u'шахтёр'),
                                           ('PRIEST', 11, u'священник'),
                                           ('PHYSICIAN', 12, u'лекарь'),
                                           ('ALCHEMIST', 13, u'алхимик'),
                                           ('EXECUTIONER', 14, u'палач'),
                                           ('MAGICIAN', 15, u'волшебник'),
                                           ('MAYOR', 16, u'мэр'),
                                           ('BUREAUCRAT', 17, u'бюрократ'),
                                           ('ARISTOCRAT', 18, u'аристократ'), ))

PERSON_STATE = create_enum('PERSON_STATE', ( ('IN_GAME', 0,  u'в игре'),
                                             ('OUT_GAME', 1, u'вне игры') ))


class Person(models.Model):

    place = models.ForeignKey('places.Place', related_name='persons')

    state = models.IntegerField(default=PERSON_STATE.IN_GAME, choices=PERSON_STATE._CHOICES)

    name = models.CharField(max_length=256)

    gender = models.IntegerField(null=False, default=GENDER.MASCULINE, choices=GENDER._CHOICES)

    race = models.IntegerField(choices=RACE._CHOICES, default=RACE.HUMAN)

    type = models.IntegerField(choices=PERSON_TYPE._CHOICES)

    friends_number = models.IntegerField(default=0)

    enemies_number = models.IntegerField(default=0)

    data = models.TextField(null=False, default=u'{}')
