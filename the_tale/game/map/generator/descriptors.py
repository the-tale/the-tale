# coding: utf-8

import math

from common.utils.logic import choose_from_interval

WIND_DIRECTIONS = [(-math.pi*8.0/8.0, u'восточный'),
                   (-math.pi*7.0/8.0, u'юго-восточно-восточный'),
                   (-math.pi*6.0/8.0, u'юго-восточный'),
                   (-math.pi*5.0/8.0, u'юго-юго-восточный'),
                   (-math.pi*4.0/8.0, u'южный'),
                   (-math.pi*3.0/8.0, u'юго-юго-западный'),
                   (-math.pi*2.0/8.0, u'юго-западный'),
                   (-math.pi*1.0/8.0, u'юго-западно-западный'),
                   (-math.pi*0.0/8.0, u'западный'),
                   ( math.pi*0.0/8.0, u'западный'),
                   ( math.pi*1.0/8.0, u'северо-западно-западный'),
                   ( math.pi*2.0/8.0, u'северо-западный'),
                   ( math.pi*3.0/8.0, u'северо-северо-западный'),
                   ( math.pi*4.0/8.0, u'северный'),
                   ( math.pi*5.0/8.0, u'северо-северо-восточный'),
                   ( math.pi*6.0/8.0, u'северо-восточный'),
                   ( math.pi*7.0/8.0, u'северо-восточно-восточный'),
                   ( math.pi*8.0/8.0, u'восточный') ]

#http://ru.wikipedia.org/wiki/Ветер
WIND_POWERS = [(0.0, u'штиль'),
               (0.05, u'тихий ветер'),
               (0.10, u'лёгкий ветер'),
               (0.17, u'слабый ветер'),
               (0.25, u'умеренный ветер'),
               (0.43, u'свежий ветер'),
               (0.55, u'сильный ветер'),
               (0.65, u'крепкий ветер'),
               (0.75, u'очень-крепкий ветер'),
               (0.85, u'шторм'),
               (0.88, u'сильный шторм'),
               (0.92, u'жестокий шторм'),
               (0.96, u'ураган') ]

TEMPERATURE_POWERS = [(0.00, u'ужасно холодно'),
                      (0.10, u'очень холодно'),
                      (0.25, u'холодно'),
                      (0.35, u'прохладно'),
                      (0.45, u'умеренная температура'),
                      (0.55, u'тепло'),
                      (0.70, u'жарко'),
                      (0.85, u'очень жарко'),
                      (0.95, u'ужасно жарко')]

WETNESS_POWERS = [(0.00, u'ужасно сухо'),
                  (0.05, u'очень сухо'),
                  (0.15, u'сухо'),
                  (0.30, u'пониженная влажность'),
                  (0.40, u'умеренная влажность'),
                  (0.60, u'повышенная влажность'),
                  (0.70, u'влажно'),
                  (0.85, u'очень влажно'),
                  (0.90, u'туман'),
                  (0.95, u'сильный туман') ]


# GROUND_WETNESS_POWERS = [(0.00, u'истрескавшаяся пыльная земля'),
#                          (0.10, u'высохшая земля'),
#                          (0.30, u'сухая земля'),
#                          (0.60, u'влажная земля'),
#                          (0.75, u'небольшые лужи'),
#                          (0.85, u'грязь и большие лужи'),
#                          (0.90, u'грязь, лужи и ручьи'),
#                          (0.95, u'грязевое месиво') ]


def wind(cell):

    wind_angle = math.atan2(cell.atmo_wind[1], cell.atmo_wind[0])
    wind_power = math.hypot(*cell.atmo_wind)

    angle_verbose = None
    min_angle_delta = 999999
    for direction, text in WIND_DIRECTIONS:
        angle_delta = math.fabs(direction - wind_angle)
        if angle_delta < min_angle_delta:
            min_angle_delta = angle_delta
            angle_verbose = text

    power_verbose = choose_from_interval(wind_power, WIND_POWERS)

    return u'%s %s' % (angle_verbose, power_verbose)

def temperature(cell):
    return choose_from_interval(cell.atmo_temperature, TEMPERATURE_POWERS)

def wetness(cell):
    return choose_from_interval(cell.atmo_wetness, WETNESS_POWERS)
