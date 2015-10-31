# coding: utf-8
import datetime
import random
import math

from dext.common.utils import s11n

from the_tale.amqp_environment import environment

from the_tale.common.utils import bbcode
from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.game import names
from the_tale.game.relations import GENDER, RACE

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

from the_tale.game.prototypes import TimePrototype, GameTime
from the_tale.game.power import add_power_management

from the_tale.game.map.conf import map_settings

from the_tale.game.map.places.models import Place, Building, ResourceExchange
from the_tale.game.map.places.conf import places_settings
from the_tale.game.map.places import exceptions
from the_tale.game.map.places.modifiers import MODIFIERS, PlaceModifierBase
from the_tale.game.map.places.relations import BUILDING_STATE, RESOURCE_EXCHANGE_TYPE, CITY_PARAMETERS
from the_tale.game.map.places import signals
from the_tale.game.map.places.races import Races
from the_tale.game.map.places import habits


class PlaceParametersDescription(object):
    PLACE_SIZE = (u'размер города', u'Влияет на количество советников в городе, развитие специализаций и на потребление товаров его жителями. Зависит от производства товаров.')
    ECONOMIC_SIZE = (u'размер экономики', u'Определяет скорость производства товаров городом. Зависит от общей суммы влияния, поступившего в город, в результате выполнения героями заданий за определённый период времени (примерное количество недель: %d). Влияние от задания может быть отрицательным. Чем больше суммарное влияние по сравнению с другими городами, тем больше размер экономики.' % places_settings.POWER_HISTORY_WEEKS)
    TERRAIN_RADIUS = (u'радиус изменений', u'Радиус в котором город изменяет мир (в клетках).')
    POLITIC_RADIUS = (u'радиус владений', u'Максимальное расстояние, на которое могут распространяться границы владений города (в клетках).')
    PRODUCTION = (u'производство', u'Скорость производства товаров. Зависит от размера экономики города и состава его совета.')
    GOODS = (u'товары', u'Чтобы расти, город должен производить товары. Если их накапливается достаточно, то размер города увеличивается. Если товары кончаются, то уменьшается.')
    KEEPERS_GOODS = (u'дары Хранителей', u'Хранители могут подарить городу дополнительные товары, которые будут постепенно переводиться в производство (%2.f%% в час, но не менее %d). Чтобы сделать городу подарок, Вы можете использовать соответствующую Карту Судьбы.' % (c.PLACE_KEEPERS_GOODS_SPENDING*100, c.PLACE_GOODS_BONUS))
    SAFETY = (u'безопасность', u'Насколько безопасно в окрестностях города (вероятность пройти по миру, не подвергнувшись нападению).')
    TRANSPORT = (u'транспорт', u'Уровень развития транспортной инфраструктуры (с какой скоростью герои путешествуют в окрестностях города).')
    FREEDOM = (u'свобода', u'Насколько активна политическая жизнь в городе (как сильно изменяется влияние советников от действий героев).')
    TAX = (u'пошлина', u'Размер пошлины, которую платят герои при посещении города (процент от наличности в кошельке героя).')
    STABILITY = (u'стабильность', u'Отражает текущую ситуацию в городе и влияет на многие его параметры. Уменьшается от изменений, происходящих в городе (при принятии законов), и постепенно восстанавливается до 100%.')


@add_power_management(places_settings.POWER_HISTORY_LENGTH, exceptions.PlacesPowerError)
class PlacePrototype(BasePrototype, names.ManageNameMixin):
    _model_class = Place
    _readonly = ('id', 'x', 'y', 'heroes_number', 'updated_at', 'created_at', 'habit_honor_positive', 'habit_honor_negative', 'habit_peacefulness_positive', 'habit_peacefulness_negative', 'is_frontier')
    _bidirectional = ('description', 'size', 'expected_size', 'goods', 'keepers_goods', 'production', 'safety', 'freedom', 'transport', 'race', 'persons_changed_at_turn', 'tax', 'stability')
    _get_by = ('id',)

    @property
    def updated_at_game_time(self): return GameTime(*f.turns_to_game_time(self._model.updated_at_turn))

    @property
    def is_new(self):
        return (datetime.datetime.now() - self.created_at).total_seconds() < places_settings.NEW_PLACE_LIVETIME

    @property
    def new_for(self):
        return self.created_at + datetime.timedelta(seconds=places_settings.NEW_PLACE_LIVETIME)

    def shift(self, dx, dy):
        self._model.x += dx
        self._model.y += dy

    def get_modifier(self): return MODIFIERS[self._model.modifier](self) if self._model.modifier is not None else None
    def set_modifier(self, value):
        if isinstance(value, PlaceModifierBase):
            self._model.modifier = value.get_id()
        else:
            self._model.modifier = value
    modifier = property(get_modifier, set_modifier)

    def sync_modifier(self):
        if self.modifier and not self.modifier.is_enough_power:
            old_modifier = self.modifier
            self.modifier = None
            signals.place_modifier_reseted.send(self.__class__, place=self, old_modifier=old_modifier)

    @property
    def description_html(self): return bbcode.render(self._model.description)

    def linguistics_restrictions(self):
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage

        restrictions = [restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.RACE, self.race.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.HABIT_HONOR, self.habit_honor.interval.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.HABIT_PEACEFULNESS, self.habit_honor.interval.value).id,
                        restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.TERRAIN, self.terrain.value).id]

        if self.modifier:
            restrictions.extend(self.modifier.TYPE.linguistics_restrictions())

        return tuple(restrictions)


    @property
    def terrain_change_power(self):
        power = self.size
        if self.modifier:
            power = self.modifier.modify_terrain_change_power(power)
        return int(round(power))

    @property
    def terrain_owning_radius(self):
        radius = self.size * 1.25
        if self.modifier:
            radius = self.modifier.modify_terrain_owning_radius(radius)
        return radius

    @property
    def terrain_radius(self):
        return self.terrain_change_power

    @property
    def depends_from_all_heroes(self):
        return self.is_frontier

    def update_heroes_number(self):
        from the_tale.game.heroes.preferences import HeroPreferences
        self._model.heroes_number = HeroPreferences.count_citizens_of(self, all=self.depends_from_all_heroes)

    def update_heroes_habits(self):
        from the_tale.game.heroes.preferences import HeroPreferences

        habits_values = HeroPreferences.count_habit_values(self, all=self.depends_from_all_heroes)

        self._model.habit_honor_positive = habits_values[0][0]
        self._model.habit_honor_negative = habits_values[0][1]
        self._model.habit_peacefulness_positive = habits_values[1][0]
        self._model.habit_peacefulness_negative = habits_values[1][1]

    @classmethod
    def _habit_change_speed(cls, current_value, positive, negative):
        positive = abs(positive)
        negative = abs(negative)

        if positive < negative:
            if positive < 0.0001:
                result = -c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM
            else:
                result = -min(c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM, negative / positive)
        elif positive > negative:
            if negative < 0.0001:
                result = c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM
            else:
                result = min(c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM, positive / negative)
        else:
            result = 0

        return result - c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM_PENALTY * (float(current_value) / c.HABITS_BORDER)

    @property
    def habit_honor_change_speed(self):
        return self._habit_change_speed(self.habit_honor.raw_value, self.habit_honor_positive, self.habit_honor_negative)

    @property
    def habit_peacefulness_change_speed(self):
        return self._habit_change_speed(self.habit_peacefulness.raw_value, self.habit_peacefulness_positive, self.habit_peacefulness_negative)

    def sync_habits(self):
        self.habit_honor.change(self.habit_honor_change_speed)
        self.habit_peacefulness.change(self.habit_peacefulness_change_speed)

    @lazy_property
    def habit_honor(self):
        honor = habits.Honor(raw_value=self._model.habit_honor)
        honor.owner = self
        return honor

    @lazy_property
    def habit_peacefulness(self):
        peacefulness = habits.Peacefulness(raw_value=self._model.habit_peacefulness)
        peacefulness.owner = self
        return peacefulness

    def can_habit_event(self):
        return random.uniform(0, 1) < c.PLACE_HABITS_EVENT_PROBABILITY

    @property
    def persons(self):
        from the_tale.game.persons.storage import persons_storage
        from the_tale.game.persons.relations import PERSON_STATE
        return sorted(persons_storage.filter(place_id=self.id, state=PERSON_STATE.IN_GAME), key=lambda p: -p.power)

    @property
    def total_persons_power(self): return sum([person.power for person in self.persons])

    @property
    def modifiers(self):
        return sorted([modifier(self) for modifier in MODIFIERS.values()], key=lambda m: -m.power)

    def mark_as_updated(self): self._model.updated_at_turn = TimePrototype.get_current_turn_number()

    @property
    def max_persons_number(self): return places_settings.SIZE_TO_PERSONS_NUMBER[self.size]


    def add_person(self):
        from the_tale.game.persons.relations import PERSON_TYPE
        from the_tale.game.persons.prototypes import PersonPrototype

        race = random.choice(RACE.records)
        gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))

        new_person = PersonPrototype.create(place=self,
                                            race=race,
                                            gender=gender,
                                            tp=random.choice(PERSON_TYPE.records),
                                            utg_name=names.generator.get_name(race, gender))

        signals.place_person_arrived.send(self.__class__, place=self, person=new_person)

        return new_person

    @property
    def can_add_person(self): return self.persons_changed_at_turn + c.PLACE_ADD_PERSON_DELAY < TimePrototype.get_current_turn_number()

    def sync_persons(self, force_add):
        for person in self.persons:
            if person.is_stable:
                continue
            person.move_out_game()
            person.save()
            signals.place_person_left.send(self.__class__, place=self, person=person)

        persons_count = len(self.persons)

        while persons_count < self.max_persons_number:

            if force_add or persons_count == 0 or self.can_add_person:
                self.add_person()
                persons_count += 1

            if not force_add:
                break

        self.sync_race()

    @lazy_property
    def data(self):
        data = s11n.from_json(self._model.data)
        if 'nearest_cells' in data:
            data['nearest_cells'] = map(tuple, data['nearest_cells'])
        return data

    def get_nearest_cells(self):
        if 'nearest_cells' not in self.data:
            self.data['nearest_cells'] = []
        return self.data['nearest_cells']
    def set_nearest_cells(self, value): self.data['nearest_cells'] = value
    nearest_cells = property(get_nearest_cells, set_nearest_cells)

    @lazy_property
    def races(self):
        if 'races' not in self.data:
            self.data['races'] = {}
        return Races(data=self.data['races'])

    @lazy_property
    def stability_modifiers(self):
        if 'stability_modifiers' not in self.data:
            self.data['stability_modifiers'] = []
        return self.data['stability_modifiers']

    @property
    def terrains(self):
        from the_tale.game.map.storage import map_info_storage
        map_info = map_info_storage.item
        terrains = set()
        for cell in self.nearest_cells:
            terrains.add(map_info.terrain[cell[1]][cell[0]])
        return terrains

    @property
    def terrain(self):
        from the_tale.game.map.storage import map_info_storage
        map_info = map_info_storage.item
        return map_info.terrain[self.y][self.x]

    def sync_race(self):
        self.races.update(persons=self.persons)

        dominant_race = self.races.dominant_race

        if dominant_race and self.race != dominant_race:
            old_race = self.race
            self.race = dominant_race
            signals.place_race_changed.send(self.__class__, place=self, old_race=old_race, new_race=self.race)

    def _stability_renewing_speed(self):
        if not self.stability_modifiers:
            return 0

        delta = c.PLACE_STABILITY_RECOVER_SPEED / len(self.stability_modifiers)

        if self.modifier:
            delta = self.modifier.modify_stability_renewing_speed(delta)

        return delta

    def sync_stability(self):
        if not self.stability_modifiers:
            return

        delta = self._stability_renewing_speed()

        new_modifiers = [(text, min(0, value + delta) if value < 0 else max(0, value - delta))
                         for text, value in self.stability_modifiers]

        new_modifiers = [modifier for modifier in new_modifiers if not (-0.001 < modifier[1] < 0.001)]

        self.stability_modifiers[:] = []
        self.stability_modifiers.extend(new_modifiers)

    def sync_parameters(self):
        self.stability = min(1.0, sum(power[1] for power in self.get_stability_powers()))

        self.production = sum(power[1] for power in self.get_production_powers())
        self.safety = sum(power[1] for power in self.get_safety_powers())
        self.freedom = sum(power[1] for power in self.get_freedom_powers())
        self.transport = sum(power[1] for power in self.get_transport_powers())

        self.tax = sum(power[1] for power in self.get_tax_powers())

    def set_expected_size(self, expected_size):
        self.expected_size = expected_size

    def sync_size(self, hours):

        self.goods += hours * self.production
        self.keepers_goods -= self.get_next_keepers_goods_spend_amount()

        if self.goods >= c.PLACE_GOODS_TO_LEVEL:
            self.size += 1
            if self.size <= places_settings.MAX_SIZE:
                self.goods = int(c.PLACE_GOODS_TO_LEVEL * c.PLACE_GOODS_AFTER_LEVEL_UP)
            else:
                self.size = places_settings.MAX_SIZE
                self.goods = c.PLACE_GOODS_TO_LEVEL
        elif self.goods <= 0:
            self.size -= 1
            if self.size > 0:
                self.goods = int(c.PLACE_GOODS_TO_LEVEL * c.PLACE_GOODS_AFTER_LEVEL_DOWN)
            else:
                self.size = 1
                self.goods = 0

    def get_experience_modifier(self):
        return self.modifier.EXPERIENCE_MODIFIER if self.modifier else 0

    def _update_powers(self, powers, parameter):
        from the_tale.game.map.places.storage import resource_exchange_storage

        for exchange in resource_exchange_storage.get_exchanges_for_place(self):
            resource_1, resource_2, place_2 = exchange.get_resources_for_place(self)
            if resource_1.parameter == parameter:
                powers.append((place_2.name if place_2 is not None else resource_2.text, -resource_1.amount * resource_1.direction))
            if resource_2.parameter == parameter:
                powers.append((place_2.name if place_2 is not None else resource_1.text, resource_2.amount * resource_2.direction))


    def get_stability_powers(self):

        powers = [ (u'город', 1.0) ]
        powers += self.stability_modifiers

        stability = sum(power[1] for power in powers)

        if stability < places_settings.MIN_STABILITY:
            powers.append((u'Серый Орден', places_settings.MIN_STABILITY - stability))


        return powers

    def get_next_keepers_goods_spend_amount(self):
        return min(self.keepers_goods, max(int(self.keepers_goods * c.PLACE_KEEPERS_GOODS_SPENDING), c.PLACE_GOODS_BONUS))

    def get_production_powers(self):

        powers = [ (u'экономика', f.place_goods_production(self.expected_size)),
                   (u'потребление', -f.place_goods_consumption(self.size)),
                   (u'стабильность', (1.0-self.stability) * c.PLACE_STABILITY_MAX_PRODUCTION_PENALTY)]

        if self.get_next_keepers_goods_spend_amount():
            powers.append((u'дары Хранителей', self.get_next_keepers_goods_spend_amount()))

        self._update_powers(powers, CITY_PARAMETERS.PRODUCTION)

        if self.modifier and self.modifier.PRODUCTION_MODIFIER:
            powers.append((self.modifier.NAME, self.modifier.PRODUCTION_MODIFIER))

        persons_powers = [(person.full_name, person.production) for person in self.persons]
        powers.extend(sorted(persons_powers, key=lambda p: -p[1]))
        return powers

    def get_safety_powers(self):
        powers = [(u'город', 1.0),
                  (u'монстры', -c.BATTLES_PER_TURN)]

        if self.is_frontier:
            powers.append((u'дикие земли', -c.WHILD_BATTLES_PER_TURN_BONUS))

        powers.append((u'стабильность', (1.0-self.stability) * c.PLACE_STABILITY_MAX_SAFETY_PENALTY))

        self._update_powers(powers, CITY_PARAMETERS.SAFETY)

        if self.modifier and self.modifier.SAFETY_MODIFIER:
            powers.append((self.modifier.NAME, self.modifier.SAFETY_MODIFIER))

        persons_powers = [(person.full_name, person.safety) for person in self.persons]
        powers.extend(sorted(persons_powers, key=lambda p: -p[1]))

        safety = sum(power[1] for power in powers)

        if safety < places_settings.MIN_SAFETY:
            powers.append((u'Серый Орден', places_settings.MIN_SAFETY - safety))

        return powers

    def get_transport_powers(self):
        powers = [(u'дороги', 1.0),
                  (u'трафик', -c.TRANSPORT_FROM_PLACE_SIZE_PENALTY * self.size)]

        if self.is_frontier:
            powers.append((u'бездорожье', -c.WHILD_TRANSPORT_PENALTY))

        powers.append((u'стабильность', (1.0-self.stability) * c.PLACE_STABILITY_MAX_TRANSPORT_PENALTY))

        self._update_powers(powers, CITY_PARAMETERS.TRANSPORT)

        if self.modifier and self.modifier.TRANSPORT_MODIFIER:
            powers.append((self.modifier.NAME, self.modifier.TRANSPORT_MODIFIER))

        persons_powers = [(person.full_name, person.transport) for person in self.persons]
        powers.extend(sorted(persons_powers, key=lambda p: -p[1]))

        transport = sum(power[1] for power in powers)

        if transport < places_settings.MIN_TRANSPORT:
            powers.append((u'Серый Орден', places_settings.MIN_TRANSPORT - transport))

        return powers

    def get_freedom_powers(self):
        powers = [(u'город', 1.0),
                  (u'стабильность', (1.0-self.stability) * c.PLACE_STABILITY_MAX_FREEDOM_PENALTY)]

        if self.modifier and self.modifier.FREEDOM_MODIFIER:
            powers.append((self.modifier.NAME, self.modifier.FREEDOM_MODIFIER))

        persons_powers = [(person.full_name, person.freedom) for person in self.persons]
        powers.extend(sorted(persons_powers, key=lambda p: -p[1]))
        return powers

    def get_tax_powers(self):
        powers = [(u'город', 0.0)]

        self._update_powers(powers, CITY_PARAMETERS.TAX)

        return powers


    @classmethod
    def create(cls, x, y, size, utg_name, race=RACE.HUMAN, is_frontier=False):
        from the_tale.game.map.places.storage import places_storage

        model = Place.objects.create( x=x,
                                      y=y,
                                      created_at_turn=TimePrototype.get_current_turn_number(),
                                      data=s11n.to_json({'name': utg_name.serialize()}),
                                      is_frontier=is_frontier,
                                      race=race,
                                      size=size)
        prototype = cls(model)

        places_storage.add_item(prototype.id, prototype)
        places_storage.update_version()

        return prototype

    def save(self):
        from the_tale.game.map.places.storage import places_storage

        self.races.serialize()

        self._model.habit_honor = self.habit_honor.raw_value
        self._model.habit_peacefulness = self.habit_peacefulness.raw_value
        self._model.data = s11n.to_json(self.data)
        self._model.save(force_update=True)

        places_storage.update_version()

    def cmd_change_power(self, power, positive_bonus, negative_bonus):
        if environment.workers.highlevel is None:
            return
        environment.workers.highlevel.cmd_change_power(power_delta=power, positive_bonus=positive_bonus, negative_bonus=negative_bonus, person_id=None, place_id=self.id)


    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'race': self.race.value,
                'name': self.name,
                'size': self.size}


class BuildingPrototype(BasePrototype, names.ManageNameMixin):
    _model_class = Building
    _readonly = ('id', 'x', 'y', 'type', 'integrity', 'created_at_turn')
    _bidirectional = ('state',)
    _get_by = ('id',)

    @lazy_property
    def data(self):
        return s11n.from_json(self._model.data)

    def shift(self, dx, dy):
        self._model.x += dx
        self._model.y += dy

    @classmethod
    def get_by_coordinates(cls, x, y):
        try:
            return cls(Place.objects.get(x=x, y=y))
        except Place.DoesNotExist:
            return None

    @property
    def person(self):
        from the_tale.game.persons.storage import persons_storage
        return persons_storage[self._model.person_id]

    @property
    def place(self):
        from the_tale.game.map.places.storage import places_storage
        return places_storage[self._model.place_id]

    @property
    def terrain_change_power(self):
        # +1 to prevent power == 0
        power = self.place.terrain_change_power * self.integrity * c.BUILDING_TERRAIN_POWER_MULTIPLIER + 1
        return int(round(power))

    def amortization_delta(self, turns_number):
        from the_tale.game.map.places.storage import buildings_storage

        buildings_number = sum(buildings_storage.get_by_person_id(person.id) is not None
                               for person in self.place.persons)

        per_one_building = float(turns_number) / c.TURNS_IN_HOUR * c.BUILDING_AMORTIZATION_SPEED
        return per_one_building * c.BUILDING_AMORTIZATION_MODIFIER**(buildings_number-1)

    @property
    def amortization_in_day(self):
        return self.amortization_delta(c.TURNS_IN_HOUR*24)

    def amortize(self, turns_number):
        self._model.integrity -= self.amortization_delta(turns_number)
        if self.integrity <= 0.0001:
            self._model.integrity = 0

    @property
    def workers_to_full_repairing(self):
        return int(math.ceil((1.0 - self.integrity) * c.BUILDING_FULL_REPAIR_ENERGY_COST / c.BUILDING_WORKERS_ENERGY_COST))

    @property
    def repair_delta(self): return float(c.BUILDING_WORKERS_ENERGY_COST) / c.BUILDING_FULL_REPAIR_ENERGY_COST

    def repair(self):
        self._model.integrity = min(1.0, self.integrity + self.repair_delta)

    @property
    def need_repair(self): return self.integrity < 0.9999

    @property
    def terrain(self):
        from the_tale.game.map.storage import map_info_storage
        map_info = map_info_storage.item
        return map_info.terrain[self.y][self.x]


    def linguistics_restrictions(self):
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage

        return [restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.TERRAIN, self.terrain.value)]



    @classmethod
    def get_available_positions(cls, center_x, center_y, building_position_radius=places_settings.BUILDING_POSITION_RADIUS): # pylint: disable=R0914
        from the_tale.game.map.places.storage import places_storage, buildings_storage
        from the_tale.game.map.roads.storage import roads_storage
        from the_tale.game.map.roads.relations import PATH_DIRECTION

        positions = set()

        for i in xrange(0, building_position_radius+1):
            for j in xrange(0, building_position_radius+1):
                positions.add((center_x+i, center_y+j))
                positions.add((center_x-i, center_y+j))
                positions.add((center_x+i, center_y-j))
                positions.add((center_x-i, center_y-j))

        positions =  set(pos for pos in positions
                         if 0 <= pos[0] < map_settings.WIDTH and 0 <= pos[1] < map_settings.HEIGHT)

        removed_positions = set()

        for place in places_storage.all():
            removed_positions.add((place.x, place.y))

        for building in buildings_storage.all():
            removed_positions.add((building.x, building.y))

        for road in roads_storage.all_exists_roads():
            x, y = road.point_1.x, road.point_1.y
            for direction in road.path:
                if direction == PATH_DIRECTION.LEFT.value: x -= 1
                elif direction == PATH_DIRECTION.RIGHT.value: x += 1
                elif direction == PATH_DIRECTION.UP.value: y -= 1
                elif direction == PATH_DIRECTION.DOWN.value: y += 1

                removed_positions.add((x, y))

        result = positions - removed_positions

        return result if result else cls.get_available_positions(center_x, center_y, building_position_radius=building_position_radius+1)


    @classmethod
    def create(cls, person, utg_name):
        from the_tale.game.map.places.storage import buildings_storage

        building = buildings_storage.get_by_person_id(person.id)

        if building:
            return building

        # remove any destroyed buildings for person
        cls._model_class.objects.filter(person_id=person.id).delete()

        x, y = random.choice(list(cls.get_available_positions(person.place.x, person.place.y)))

        model = Building.objects.create(x=x,
                                        y=y,
                                        data=s11n.to_json({'name': utg_name.serialize()}),
                                        place=person.place._model,
                                        person=person._model,
                                        state=BUILDING_STATE.WORKING,
                                        created_at_turn=TimePrototype.get_current_turn_number(),
                                        type=person.type.building_type)

        prototype = cls(model=model)

        buildings_storage.add_item(prototype.id, prototype)
        buildings_storage.update_version()

        return prototype

    def destroy(self):
        from the_tale.game.map.places.storage import buildings_storage
        self.state = BUILDING_STATE.DESTROYED
        self.save()
        buildings_storage.update_version()
        buildings_storage.refresh()

    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'person': self._model.person_id,
                'place': self._model.place_id,
                'type': self.type.value}

    def save(self):
        from the_tale.game.map.places.storage import buildings_storage
        self._model.data = s11n.to_json(self.data)
        self._model.save()
        buildings_storage.update_version()


class ResourceExchangePrototype(BasePrototype):
    _model_class = ResourceExchange
    _readonly = ('id', 'bill_id', 'resource_1', 'resource_2')
    _bidirectional = ()
    _get_by = ('id',)

    @property
    def place_1(self):
        from the_tale.game.map.places.storage import places_storage
        return places_storage.get(self._model.place_1_id)

    @property
    def place_2(self):
        from the_tale.game.map.places.storage import places_storage
        return places_storage.get(self._model.place_2_id)

    @lazy_property
    def bill(self):
        from the_tale.game.bills.prototypes import BillPrototype
        return BillPrototype.get_by_id(self.bill_id)

    def get_resources_for_place(self, place):
        if place.id == self.place_1.id:
            return (self.resource_1, self.resource_2, self.place_2)
        if place.id == self.place_2.id:
            return (self.resource_2, self.resource_1, self.place_1)
        return (RESOURCE_EXCHANGE_TYPE.NONE, RESOURCE_EXCHANGE_TYPE.NONE, None)

    @classmethod
    def create(cls, place_1, place_2, resource_1, resource_2, bill):
        from the_tale.game.map.places.storage import resource_exchange_storage

        model = cls._model_class.objects.create(bill=bill._model if bill is not None else None,
                                                place_1=place_1._model if place_1 is not None else None,
                                                place_2=place_2._model if place_2 is not None else None,
                                                resource_1=resource_1,
                                                resource_2=resource_2)
        prototype = cls(model=model)

        resource_exchange_storage.add_item(prototype.id, prototype)
        resource_exchange_storage.update_version()

        return prototype

    def remove(self):
        from the_tale.game.map.places.storage import resource_exchange_storage

        self._model.delete()

        resource_exchange_storage.update_version()
        resource_exchange_storage.refresh()
