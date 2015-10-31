# coding: utf-8

import math

import rels

from the_tale.common.utils.logic import choose_from_interval, choose_nearest

from the_tale.game.prototypes import TimePrototype
from the_tale.game.balance import constants as c

from the_tale.game.map.conf import map_settings


class WIND_DIRECTION(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    direction = rels.Column(unique=False)

    records = ( (0,  u'восточный', -math.pi*8.0/8.0),
                 (1,  u'востоко-юго-восточный', -math.pi*7.0/8.0),
                 (2,  u'юго-восточный', -math.pi*6.0/8.0),
                 (3,  u'юго-юго-восточный', -math.pi*5.0/8.0),
                 (4,  u'южный', -math.pi*4.0/8.0),
                 (5,  u'юго-юго-западный', -math.pi*3.0/8.0),
                 (6,  u'юго-западный', -math.pi*2.0/8.0),
                 (7,  u'западо-юго-западный', -math.pi*1.0/8.0),
                 (8,  u'западный', -math.pi*0.0/8.0),
                 (9,  u'западный', math.pi*0.0/8.0),
                 (10, u'западо-северо-западный', math.pi*1.0/8.0),
                 (11, u'северо-западный', math.pi*2.0/8.0),
                 (12, u'северо-северо-западный', math.pi*3.0/8.0),
                 (13, u'северный', math.pi*4.0/8.0),
                 (14, u'северо-северо-восточный', math.pi*5.0/8.0),
                 (15, u'северо-восточный', math.pi*6.0/8.0),
                 (16, u'востоко-северо-восточный', math.pi*7.0/8.0),
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


class SAFETY(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    safety = rels.Column()

    records = ( (1, u'ни один вменяемый герой никогда не сунется в это пропащее место', 0.000),
                (2, u'здесь есть только душераздирающие вопли, дикая магия, опаснейшие монстры и страх, пробирающий до костей', 0.101),
                (3, u'в округе нет ни одного безопасного места, за каждым поворотом, каждым камнем путника ждёт бой не на жизнь на на смерть', 0.201),
                (4, u'ужасные крики то и дело пролетают по окрестностям, опасные твари ходят в открытую, далеко не каждый герой отважится зайти в это гиблое место', 0.301),
                (5, u'хищные взгляды множества голодных тварей не дадут расслабиться ни одному смельчаку, рискнувшему забраться в эту глушь', 0.401),
                (6, u'разбросанные тут и там кости и остатки походного скарба не предвещают ничего хорошего путникам', 0.501),
                (7, u'пейзаж выглядит устрашающе, присмотревшись, можно увидеть свежие следы хищных тварей', 0.601),
                (8, u'местность выглядит настораживающе, расслабляться не стоит — опасность рядом', 0.701),
                (9, u'окрестности выглядят безопаснее обычного, видимо, здесь часто ходят опытные герои', 0.801),
                (10, u'местность очень безопасная и ухоженная', 0.901) )


class ROAD_TRANSPORT(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    transport = rels.Column()

    records = ( (0, u'среди сплошного бездорожья нет и намёка на дорогу', 0.0),
                (1, u'среди бездорожья иногда проглядывают остатки заваленной буреломом да разбитыми телегами дороги', 0.5),
                (2, u'небольшая тропка петляет по округе, иногда переходя в широкие участки, как будто вспоминая о былых временах', 0.6),
                (3, u'старая неухоженная дорога то и дело пропадает из виду, скрываемая недавними изменениями ландшафта', 0.7),
                (4, u'колдобины на пару с остатками укатанного полотна пытаются сойти за дорогу', 0.8),
                (5, u'слегка потрёпанная грунтовая дорога периодически оборачивается колдобинами в местах с ослабевшей магической защитой', 0.9),
                (6, u'грунтовая дорога петляет, обходя наиболее изменчивые места ландшафта', 1.0),
                (7, u'надёжная ухоженная грунтовая дорога так и приглашает ходоков быстрее двигаться к своей цели', 1.1),
                (8, u'спрямлённая грунтовая дорога весело уходит вдаль, защищаемая от изменений редкими магическими башнями', 1.2),
                (9, u'прямая мощёная дорога то и дело прерывается грунтовыми участками в самых изменчивых своих местах', 1.3),
                (10, u'добротный мощёный тракт петляет, отгородившись магическими башнями от самых «диких» участков ландшафта', 1.4),
                (11, u'от горизонта до горизонта стрелой протянулся широкий мощёный тракт; через равные промежутки вдоль дороги стоят ухоженные магические башни, защищающие его от изменений', 1.5) )

class WILD_TRANSPORT(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    transport = rels.Column()

    records = [ (r.value, u'видно, как %s' % r.text, r.transport) for r in ROAD_TRANSPORT.records ]

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

def _get_safety(safety):
    return choose_from_interval(safety,  [(r.safety, r) for r in SAFETY.records])

def _get_road_transport(transport):
    return choose_from_interval(transport,  [(r.transport, r) for r in ROAD_TRANSPORT.records])

def _get_wild_transport(transport):
    return choose_from_interval(transport,  [(r.transport, r) for r in WILD_TRANSPORT.records])



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

    @classmethod
    def safety(self, x, y):
        from the_tale.game.map.storage import map_info_storage
        dominant_place = map_info_storage.item.get_dominant_place(x, y)

        if dominant_place:
            safety = dominant_place.safety
        else:
            safety = 1.0 - c.BATTLES_PER_TURN - c.WHILD_BATTLES_PER_TURN_BONUS

        return _get_safety(safety)


    @classmethod
    def transport(self, x, y):
        from the_tale.game.map.storage import map_info_storage
        from the_tale.game.heroes.position import Position

        dominant_place = map_info_storage.item.get_dominant_place(x, y)

        has_road = map_info_storage.item.roads_map[y][x].get('road')

        if dominant_place:
            transport = dominant_place.transport
        else:
            transport = Position.raw_transport()

        if has_road:
            return _get_road_transport(transport)
        else:
            return _get_wild_transport(transport)



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
