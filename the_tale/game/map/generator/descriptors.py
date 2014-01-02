# coding: utf-8

import math

import rels

from the_tale.common.utils.logic import choose_from_interval, choose_nearest

from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.conf import map_settings


class WIND_DIRECTION(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    direction = rels.Column(unique=False)

    records = ( (0,  u'восточный', -math.pi*8.0/8.0),
                 (1,  u'юго-восточно-восточный', -math.pi*7.0/8.0),
                 (2,  u'юго-восточный', -math.pi*6.0/8.0),
                 (3,  u'юго-юго-восточный', -math.pi*5.0/8.0),
                 (4,  u'южный', -math.pi*4.0/8.0),
                 (5,  u'юго-юго-западный', -math.pi*3.0/8.0),
                 (6,  u'юго-западный', -math.pi*2.0/8.0),
                 (7,  u'юго-западно-западный', -math.pi*1.0/8.0),
                 (8,  u'западный', -math.pi*0.0/8.0),
                 (9,  u'западный', math.pi*0.0/8.0),
                 (10, u'северо-западно-западный', math.pi*1.0/8.0),
                 (11, u'северо-западный', math.pi*2.0/8.0),
                 (12, u'северо-северо-западный', math.pi*3.0/8.0),
                 (13, u'северный', math.pi*4.0/8.0),
                 (14, u'северо-северо-восточный', math.pi*5.0/8.0),
                 (15, u'северо-восточный', math.pi*6.0/8.0),
                 (16, u'северо-восточно-восточный', math.pi*7.0/8.0),
                 (17, u'восточный', math.pi*8.0/8.0) )


#http://ru.wikipedia.org/wiki/Ветер
class WIND_POWER(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    power = rels.Column()

    records = ((0,  u'штиль', 0.0),
                (1,  u'тихий ветер', 0.05),
                (2,  u'лёгкий ветер', 0.10),
                (3,  u'слабый ветер', 0.17),
                (4,  u'умеренный ветер', 0.25),
                (5,  u'свежий ветер', 0.43),
                (6,  u'сильный ветер', 0.55),
                (7,  u'крепкий ветер', 0.65),
                (8,  u'очень крепкий ветер', 0.75),
                (9,  u'шторм', 0.85),
                (10, u'сильный шторм', 0.88),
                (11, u'жестокий шторм', 0.92),
                (12, u'ураган', 0.96) )


class TEMPERATURE_POWER(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    temperature = rels.Column()

    records = ( (0, u'ужасно холодно', 0.00),
                 (1, u'очень холодно', 0.10),
                 (2, u'холодно', 0.25),
                 (3, u'прохладно', 0.35),
                 (4, u'умеренная температура', 0.45),
                 (5, u'тепло', 0.55),
                 (6, u'жарко', 0.70),
                 (7, u'очень жарко', 0.85),
                 (8, u'ужасно жарко', 0.95) )


class WETNESS_POWER(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    wetness = rels.Column()

    records = ( (0, u'ужасно сухо', 0.00),
                 (1, u'очень сухо', 0.05),
                 (2, u'сухо', 0.15),
                 (3, u'пониженная влажность', 0.30),
                 (4, u'умеренная влажность', 0.40),
                 (5, u'повышенная влажность', 0.60),
                 (6, u'влажно', 0.70),
                 (7, u'очень влажно', 0.85),
                 (8, u'туман', 0.90),
                 (9, u'сильный туман', 0.95) )


# GROUND_WETNESS_POWERS = [(0.00, u'истрескавшаяся пыльная земля'),
#                          (0.10, u'высохшая земля'),
#                          (0.30, u'сухая земля'),
#                          (0.60, u'влажная земля'),
#                          (0.75, u'небольшые лужи'),
#                          (0.85, u'грязь и большие лужи'),
#                          (0.90, u'грязь, лужи и ручьи'),
#                          (0.95, u'грязевое месиво') ]


def _get_wind_direction(cell):
    return choose_nearest(math.atan2(cell.atmo_wind[1], cell.atmo_wind[0]),
                          [(r.direction, r) for r in WIND_DIRECTION.records])

def _get_wind_power(cell):
    wind_power = math.hypot(*cell.atmo_wind)
    return choose_from_interval(wind_power, [(r.power, r) for r in WIND_POWER.records])

def _get_temperature(cell):
    return choose_from_interval(cell.mid_temperature, [(r.temperature, r) for r in TEMPERATURE_POWER.records])

def _get_wetness(cell):
    return choose_from_interval(cell.mid_wetness,  [(r.wetness, r) for r in WETNESS_POWER.records])



class UICell(object):

    def __init__(self, world_cell=None):
        if world_cell:
            self.wind_direction = _get_wind_direction(world_cell)
            self.wind_power = _get_wind_power(world_cell)
            self.temperature = _get_temperature(world_cell)
            self.wetness = _get_wetness(world_cell)

    def serialize(self):
        return (self.wind_direction.value,
                self.wind_power.value,
                self.temperature.value,
                self.wetness.value)

    @classmethod
    def deserialize(cls, data):
        cell = cls()

        cell.wind_direction = WIND_DIRECTION.index_value[data[0]]
        cell.wind_power = WIND_POWER.index_value[data[1]]
        cell.temperature = TEMPERATURE_POWER.index_value[data[2]]
        cell.wetness = WETNESS_POWER.index_value[data[3]]

        return cell


class UICells(object):

    def __init__(self, generator=None): # pylint: disable=W0613
        self.cells = ()

    def get_cell(self, x, y):
        return self.cells[y][x]

    def serialize(self):
        data = []

        for row in self.cells:
            serialized_row = [cell.serialize() for cell in row]
            data.append(serialized_row)

        return data

    @classmethod
    def create(cls, generator):
        obj = cls()

        cells = []

        for y in xrange(0, generator.h):
            row = []

            for x in xrange(0, generator.w):
                cell = generator.cell_info(x, y)
                randomized_cell = cell.randomize(seed=(x+y)*TimePrototype.get_current_time().game_time.day, fraction=map_settings.CELL_RANDOMIZE_FRACTION)
                row.append(UICell(randomized_cell))

            cells.append(tuple(row))

        obj.cells = tuple(cells)

        return obj


    @classmethod
    def deserialize(cls, data):
        obj = cls()

        cells = []

        for row in data:
            cells_row = [UICell.deserialize(cell_data) for cell_data in row ]
            cells.append(tuple(cells_row))

        obj.cells = tuple(cells)

        return obj
