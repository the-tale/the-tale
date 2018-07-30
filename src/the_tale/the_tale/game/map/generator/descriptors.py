
import smart_imports

smart_imports.all()


class WIND_DIRECTION(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    direction = rels.Column(unique=False)

    records = ((0, 'восточный', -math.pi * 8.0 / 8.0),
               (1, 'востоко-юго-восточный', -math.pi * 7.0 / 8.0),
               (2, 'юго-восточный', -math.pi * 6.0 / 8.0),
               (3, 'юго-юго-восточный', -math.pi * 5.0 / 8.0),
               (4, 'южный', -math.pi * 4.0 / 8.0),
               (5, 'юго-юго-западный', -math.pi * 3.0 / 8.0),
               (6, 'юго-западный', -math.pi * 2.0 / 8.0),
               (7, 'западо-юго-западный', -math.pi * 1.0 / 8.0),
               (8, 'западный', -math.pi * 0.0 / 8.0),
               (9, 'западный', math.pi * 0.0 / 8.0),
               (10, 'западо-северо-западный', math.pi * 1.0 / 8.0),
               (11, 'северо-западный', math.pi * 2.0 / 8.0),
               (12, 'северо-северо-западный', math.pi * 3.0 / 8.0),
               (13, 'северный', math.pi * 4.0 / 8.0),
               (14, 'северо-северо-восточный', math.pi * 5.0 / 8.0),
               (15, 'северо-восточный', math.pi * 6.0 / 8.0),
               (16, 'востоко-северо-восточный', math.pi * 7.0 / 8.0),
               (17, 'восточный', math.pi * 8.0 / 8.0))


# https://ru.wikipedia.org/wiki/Ветер
class WIND_POWER(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    power = rels.Column()

    records = ((0, 'штиль', 0.0),
               (1, 'тихий ветер', 0.05),
               (2, 'лёгкий ветер', 0.10),
               (3, 'слабый ветер', 0.17),
               (4, 'умеренный ветер', 0.25),
               (5, 'свежий ветер', 0.43),
               (6, 'сильный ветер', 0.55),
               (7, 'крепкий ветер', 0.65),
               (8, 'очень крепкий ветер', 0.75),
               (9, 'шторм', 0.85),
               (10, 'сильный шторм', 0.88),
               (11, 'жестокий шторм', 0.92),
               (12, 'ураган', 0.96))


class TEMPERATURE_POWER(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    temperature = rels.Column()

    records = ((0, 'ужасно холодно', 0.00),
               (1, 'очень холодно', 0.10),
               (2, 'холодно', 0.25),
               (3, 'прохладно', 0.35),
               (4, 'умеренная температура', 0.45),
               (5, 'тепло', 0.55),
               (6, 'жарко', 0.70),
               (7, 'очень жарко', 0.85),
               (8, 'ужасно жарко', 0.95))


class WETNESS_POWER(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    wetness = rels.Column()

    records = ((0, 'ужасно сухо', 0.00),
               (1, 'очень сухо', 0.05),
               (2, 'сухо', 0.15),
               (3, 'пониженная влажность', 0.30),
               (4, 'умеренная влажность', 0.40),
               (5, 'повышенная влажность', 0.60),
               (6, 'влажно', 0.70),
               (7, 'очень влажно', 0.85),
               (8, 'туман', 0.90),
               (9, 'сильный туман', 0.95))


class SAFETY(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    safety = rels.Column()

    records = ((1, 'ни один вменяемый герой никогда не сунется в это пропащее место', 0.000),
               (2, 'здесь есть только душераздирающие вопли, дикая магия, опаснейшие монстры и страх, пробирающий до костей', 0.101),
               (3, 'в округе нет ни одного безопасного места, за каждым поворотом, каждым камнем путника ждёт бой не на жизнь, а на смерть', 0.201),
               (4, 'ужасные крики то и дело пролетают по окрестностям, опасные твари ходят в открытую, далеко не каждый герой отважится зайти в это гиблое место', 0.301),
               (5, 'хищные взгляды множества голодных тварей не дадут расслабиться ни одному смельчаку, рискнувшему забраться в эту глушь', 0.401),
               (6, 'разбросанные тут и там кости и остатки походного скарба не предвещают ничего хорошего путникам', 0.501),
               (7, 'пейзаж выглядит устрашающе, присмотревшись, можно увидеть свежие следы хищных тварей', 0.601),
               (8, 'местность выглядит настораживающе, расслабляться не стоит — опасность рядом', 0.701),
               (9, 'окрестности выглядят безопаснее обычного, видимо, здесь часто ходят опытные герои', 0.801),
               (10, 'местность очень безопасная и ухоженная', 0.901))


class ROAD_TRANSPORT(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    transport = rels.Column()

    records = ((0, 'среди сплошного бездорожья нет и намёка на дорогу', 0.0),
               (1, 'среди бездорожья иногда проглядывают остатки заваленной буреломом да разбитыми телегами дороги', 0.5),
               (2, 'небольшая тропка петляет по округе, иногда переходя в широкие участки, как будто вспоминая о былых временах', 0.6),
               (3, 'старая неухоженная дорога то и дело пропадает из виду, скрываемая недавними изменениями ландшафта', 0.7),
               (4, 'колдобины на пару с остатками укатанного полотна пытаются сойти за дорогу', 0.8),
               (5, 'слегка потрёпанная грунтовая дорога периодически оборачивается колдобинами в местах с ослабевшей магической защитой', 0.9),
               (6, 'грунтовая дорога петляет, обходя наиболее изменчивые места ландшафта', 1.0),
               (7, 'надёжная ухоженная грунтовая дорога так и приглашает ходоков быстрее двигаться к своей цели', 1.1),
               (8, 'спрямлённая грунтовая дорога весело уходит вдаль, защищаемая от изменений редкими магическими башнями', 1.2),
               (9, 'прямая мощёная дорога то и дело прерывается грунтовыми участками в самых изменчивых своих местах', 1.3),
               (10, 'добротный мощёный тракт петляет, отгородившись магическими башнями от самых «диких» участков ландшафта', 1.4),
               (11, 'от горизонта до горизонта стрелой протянулся широкий мощёный тракт; через равные промежутки вдоль дороги стоят ухоженные магические башни, защищающие его от изменений', 1.5))


class WILD_TRANSPORT(rels.Relation):
    value = rels.Column(external=True, unique=True)
    text = rels.Column(unique=False)
    transport = rels.Column()

    records = [(r.value, 'видно, как %s' % r.text, r.transport) for r in ROAD_TRANSPORT.records]

# GROUND_WETNESS_POWERS = [(0.00, u'истрескавшаяся пыльная земля'),
#                          (0.10, u'высохшая земля'),
#                          (0.30, u'сухая земля'),
#                          (0.60, u'влажная земля'),
#                          (0.75, u'небольшые лужи'),
#                          (0.85, u'грязь и большие лужи'),
#                          (0.90, u'грязь, лужи и ручьи'),
#                          (0.95, u'грязевое месиво') ]


def _get_wind_direction(cell):
    return utils_logic.choose_nearest(math.atan2(cell.atmo_wind[1], cell.atmo_wind[0]),
                                      [(r.direction, r) for r in WIND_DIRECTION.records])


def _get_wind_power(cell):
    wind_power = math.hypot(*cell.atmo_wind)
    return utils_logic.choose_from_interval(wind_power, [(r.power, r) for r in WIND_POWER.records])


def _get_temperature(cell):
    return utils_logic.choose_from_interval(cell.mid_temperature, [(r.temperature, r) for r in TEMPERATURE_POWER.records])


def _get_wetness(cell):
    return utils_logic.choose_from_interval(cell.mid_wetness, [(r.wetness, r) for r in WETNESS_POWER.records])


def _get_safety(safety):
    return utils_logic.choose_from_interval(safety, [(r.safety, r) for r in SAFETY.records])


def _get_road_transport(transport):
    return utils_logic.choose_from_interval(transport, [(r.transport, r) for r in ROAD_TRANSPORT.records])


def _get_wild_transport(transport):
    return utils_logic.choose_from_interval(transport, [(r.transport, r) for r in WILD_TRANSPORT.records])


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
        dominant_place = storage.map_info.item.get_dominant_place(x, y)

        if dominant_place:
            safety = dominant_place.attrs.safety
        else:
            safety = 1.0 - c.BATTLES_PER_TURN - c.WHILD_BATTLES_PER_TURN_BONUS

        return _get_safety(safety)

    @classmethod
    def transport(self, x, y):
        from the_tale.game.heroes import position as heroes_position

        dominant_place = storage.map_info.item.get_dominant_place(x, y)

        has_road = storage.map_info.item.roads_map[y][x].get('road')

        if dominant_place:
            transport = dominant_place.attrs.transport
        else:
            transport = heroes_position.Position.raw_transport()

        if has_road:
            return _get_road_transport(transport)
        else:
            return _get_wild_transport(transport)


class UICells(object):

    def __init__(self, generator=None):  # pylint: disable=W0613
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

        for y in range(0, generator.h):
            row = []

            for x in range(0, generator.w):
                cell = generator.cell_info(x, y)
                randomized_cell = cell.randomize(seed=(x + y) * game_turn.game_datetime().day, fraction=conf.settings.CELL_RANDOMIZE_FRACTION)
                row.append(UICell(randomized_cell))

            cells.append(tuple(row))

        obj.cells = tuple(cells)

        return obj

    @classmethod
    def deserialize(cls, data):
        obj = cls()

        cells = []

        for row in data:
            cells_row = [UICell.deserialize(cell_data) for cell_data in row]
            cells.append(tuple(cells_row))

        obj.cells = tuple(cells)

        return obj
