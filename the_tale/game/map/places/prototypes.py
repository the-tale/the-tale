# coding: utf-8
import random
import math

from dext.utils import s11n

from game.game_info import GENDER
from textgen import words

from common.utils import bbcode
from common.utils.prototypes import BasePrototype
from common.utils.decorators import lazy_property

from game import names
from game.balance import constants as c
from game.prototypes import TimePrototype, GameTime

from game.balance import formulas as f
from game.balance.enums import RACE

from game.helpers import add_power_management

from game.map.conf import map_settings

from game.map.places.models import Place, Building, ResourceExchange
from game.map.places.conf import places_settings
from game.map.places.exceptions import PlacesException
from game.map.places.modifiers import MODIFIERS, PlaceModifierBase
from game.map.places.relations import BUILDING_STATE, RESOURCE_EXCHANGE_TYPE, CITY_PARAMETERS
from game.map.places import signals

class PlaceParametersDescription(object):
    PLACE_SIZE = (u'размер города', u'Влияет на количество жителей в городе, развитие специализаций и на потребление товаров жителями. Зависит от производства товаров.')
    ECONOMIC_SIZE = (u'размер экономики', u'Определяет скорость производства товаров городом. Зависит от <strong>изменения</strong> влияния персонажей в городе за определённый период (примерное количество недель: %d).' % places_settings.POWER_HISTORY_WEEKS)
    TERRAIN_RADIUS = (u'радиус влияния', u'Радиус в котором город может оказывать влияние на карту (в клетках).')
    PRODUCTION = (u'производство', u'Скорость производства товаров, зависит от размера экономики города и от персонажей, проживающих в нём.')
    GOODS = (u'товары', u'Чтобы расти, город должен производить товары. Если их накапливается достаточно, то размер города увеличивается. Если товары кончаются, то уменьшается.')
    SAFETY = (u'безопасность', u'Насколько безопасно в окрестностях города (вероятность пройти по дороге не подвергнувшись нападению).')
    TRANSPORT = (u'транспорт', u'Уровень развития транспортной инфраструктуры (с какой скоростью герои путешествуют в окрестностях города).')
    FREEDOM = (u'свобода', u'На сколько активна политическая жизнь в городе (как сильно изменяется влияние персонажей от действий героев).')


@add_power_management(places_settings.POWER_HISTORY_LENGTH, PlacesException)
class PlacePrototype(BasePrototype):
    _model_class = Place
    _readonly = ('id', 'x', 'y', 'name', 'heroes_number', 'updated_at')
    _bidirectional = ('description', 'size', 'expected_size', 'goods', 'production', 'safety', 'freedom', 'transport')
    _get_by = ('id',)

    @property
    def updated_at_game_time(self): return GameTime(*f.turns_to_game_time(self._model.updated_at_turn))

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

    @lazy_property
    def normalized_name(self): return words.WordBase.deserialize(s11n.from_json(self._model.name_forms))

    def set_name_forms(self, name_forms):
        self._model.name_forms = s11n.to_json(name_forms.serialize())
        del self.normalized_name
        self._model.name = name_forms.normalized

    @property
    def description_html(self): return bbcode.render(self._model.description)

    @property
    def terrain_change_power(self):
        power = self.size
        if self.modifier:
            power = self.modifier.modify_terrain_change_power(power)
        return int(round(power))

    @property
    def terrain_radius(self):
        return self.terrain_change_power

    def update_heroes_number(self):
        from game.heroes.preferences import HeroPreferences
        self._model.heroes_number = HeroPreferences.count_citizens_of(self)

    @property
    def persons(self):
        from game.persons.storage import persons_storage
        from game.persons.models import PERSON_STATE
        return sorted(persons_storage.filter(place_id=self.id, state=PERSON_STATE.IN_GAME), key=lambda p: -p.power)

    @property
    def total_persons_power(self): return sum([person.power for person in self.persons])

    @property
    def modifiers(self):
        return sorted([modifier(self) for modifier in MODIFIERS.values()], key=lambda m: -m.power)

    def mark_as_updated(self): self._model.updated_at_turn = TimePrototype.get_current_turn_number()

    @property
    def max_persons_number(self): return places_settings.SIZE_TO_PERSONS_NUMBER[self.size]

    def sync_persons(self):
        from game.persons.relations import PERSON_TYPE
        from game.persons.prototypes import PersonPrototype

        for person in self.persons:
            if person.is_stable:
                continue
            person.move_out_game()
            person.save()
            signals.place_person_left.send(self.__class__, place=self, person=person)

        persons_count = len(self.persons)

        while persons_count < self.max_persons_number:
            race = random.choice(RACE._ALL)
            gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))

            new_person = PersonPrototype.create(place=self,
                                                race=race,
                                                gender=gender,
                                                tp=random.choice(PERSON_TYPE._records),
                                                name=names.generator.get_name(race, gender))
            persons_count += 1
            signals.place_person_arrived.send(self.__class__, place=self, person=new_person)

        self.sync_race()

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self._model.data)
            if 'nearest_cells' in self._data:
                self._data['nearest_cells'] = map(tuple, self._data['nearest_cells'])
        return self._data

    def get_nearest_cells(self):
        if 'nearest_cells' not in self.data:
            self.data['nearest_cells'] = []
        return self.data['nearest_cells']
    def set_nearest_cells(self, value): self.data['nearest_cells'] = value
    nearest_cells = property(get_nearest_cells, set_nearest_cells)

    @property
    def terrains(self):
        from game.map.storage import map_info_storage
        map_info = map_info_storage.item
        terrains = set()
        for cell in self.nearest_cells:
            terrains.add(map_info.terrain[cell[1]][cell[0]])
        return terrains


    def get_race(self):
        if not hasattr(self, '_race'):
            self._race = RACE(self._model.race)
        return self._race
    def set_race(self, value):
        self.race.update(value)
        self._model.race = self.race.value
    race = property(get_race, set_race)

    def sync_race(self):
        race_power = {}

        for person in self.persons:
            race_power[person.race] = race_power.get(person.race, 0) + person.power

        if len(race_power) == 0:
            return

        dominant_race = max(race_power.items(), key=lambda x: x[1])[0]

        if self.race != dominant_race:
            old_race = RACE(self.race.value)
            self.race = dominant_race
            signals.place_race_changed.send(self.__class__, place=self, old_race=old_race, new_race=self.race)

    def sync_parameters(self):
        self.production = sum(power[1] for power in self.get_production_powers())
        self.safety = sum(power[1] for power in self.get_safety_powers())
        self.freedom = sum(power[1] for power in self.get_freedom_powers())
        self.transport = sum(power[1] for power in self.get_transport_powers())

    def set_expected_size(self, expected_size):
        self.expected_size = expected_size

    def sync_size(self, hours):
        self.goods += hours * self.production

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
        from game.map.places.storage import resource_exchange_storage

        for exchange in resource_exchange_storage.get_exchanges_for_place(self):
            resource_1, resource_2, place_2 = exchange.get_resources_for_place(self)
            if resource_1.parameter == parameter:
                powers.append((place_2.name, -resource_1.amount))
            if resource_2.parameter == parameter:
                powers.append((place_2.name, resource_2.amount))


    def get_production_powers(self):

        powers = [ (u'производство', f.place_goods_production(self.expected_size)),
                   (u'потребление', -f.place_goods_consumption(self.size))]

        self._update_powers(powers, CITY_PARAMETERS.PRODUCTION)

        if self.modifier and self.modifier.PRODUCTION_MODIFIER:
            powers.append((self.modifier.NAME, self.modifier.PRODUCTION_MODIFIER))

        persons_powers = [(person.name, person.production) for person in self.persons]
        powers.extend(sorted(persons_powers, key=lambda p: -p[1]))
        return powers

    def get_safety_powers(self):
        powers = [(u'город', 1.0),
                  (u'монстры', -c.BATTLES_PER_TURN)]

        self._update_powers(powers, CITY_PARAMETERS.SAFETY)

        if self.modifier and self.modifier.SAFETY_MODIFIER:
            powers.append((self.modifier.NAME, self.modifier.SAFETY_MODIFIER))

        persons_powers = [(person.name, person.safety) for person in self.persons]
        powers.extend(sorted(persons_powers, key=lambda p: -p[1]))
        return powers

    def get_transport_powers(self):
        powers = [(u'дороги', 1.0)]

        self._update_powers(powers, CITY_PARAMETERS.TRANSPORT)

        if self.modifier and self.modifier.TRANSPORT_MODIFIER:
            powers.append((self.modifier.NAME, self.modifier.TRANSPORT_MODIFIER))

        persons_powers = [(person.name, person.transport) for person in self.persons]
        powers.extend(sorted(persons_powers, key=lambda p: -p[1]))
        return powers

    def get_freedom_powers(self):
        powers = [(u'город', 1.0)]

        if self.modifier and self.modifier.FREEDOM_MODIFIER:
            powers.append((self.modifier.NAME, self.modifier.FREEDOM_MODIFIER))

        persons_powers = [(person.name, person.freedom) for person in self.persons]
        powers.extend(sorted(persons_powers, key=lambda p: -p[1]))
        return powers


    @classmethod
    def create(cls, x, y, size, name_forms):
        from game.map.places.storage import places_storage

        model = Place.objects.create( x=x,
                                      y=y,
                                      name=name_forms.normalized,
                                      name_forms=s11n.to_json(name_forms.serialize()),
                                      size=size)
        prototype = cls(model)

        places_storage.add_item(prototype.id, prototype)
        places_storage.update_version()

        return prototype

    def save(self):
        from game.map.places.storage import places_storage

        self._model.data = s11n.to_json(self.data)
        self._model.save(force_update=True)

        places_storage.update_version()


    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'race': self.race.value,
                'name': self.name,
                'size': self.size}


class BuildingPrototype(BasePrototype):
    _model_class = Building
    _readonly = ('id', 'x', 'y', 'type', 'integrity')
    _bidirectional = ('state',)
    _get_by = ('id',)

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
    def name(self): return self.normalized_name.normalized

    @lazy_property
    def normalized_name(self): return words.WordBase.deserialize(s11n.from_json(self._model.name_forms))

    def set_name_forms(self, name_forms):
        self._model.name_forms = s11n.to_json(name_forms.serialize())
        del self.normalized_name

    @property
    def person(self):
        from game.persons.storage import persons_storage
        return persons_storage[self._model.person_id]

    @property
    def place(self):
        from game.map.places.storage import places_storage
        return places_storage[self._model.place_id]

    @property
    def terrain_change_power(self):
        # +1 to prevent power == 0
        power = self.place.terrain_change_power * self.integrity * c.BUILDING_TERRAIN_POWER_MULTIPLIER + 1
        return int(round(power))

    def amortization_delta(self, turns_number):
        from game.map.places.storage import buildings_storage

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
            self.destroy()
            signals.building_destroyed_by_amortization.send(self.__class__, place=self.place, person=self.person)

    @property
    def workers_to_full_repairing(self):
        return int(math.ceil((1.0 - self.integrity) * c.BUILDING_FULL_REPAIR_ENERGY_COST / c.BUILDING_WORKERS_ENERGY_COST))

    @property
    def repair_delta(self): return float(c.BUILDING_WORKERS_ENERGY_COST) / c.BUILDING_FULL_REPAIR_ENERGY_COST

    def repair(self):
        self._model.integrity = min(1.0, self.integrity + self.repair_delta)

    @property
    def need_repair(self): return self.integrity < 0.9999

    @classmethod
    def get_available_positions(cls, center_x, center_y, building_position_radius=places_settings.BUILDING_POSITION_RADIUS): # pylint: disable=R0914
        from game.map.places.storage import places_storage, buildings_storage
        from game.map.roads.storage import roads_storage
        from game.map.roads.relations import PATH_DIRECTION

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
    def create(cls, person, name_forms):
        from game.map.places.storage import buildings_storage

        building = buildings_storage.get_by_person_id(person.id)

        if building:
            return building

        # remove any destroyed buildings for person
        cls._model_class.objects.filter(person_id=person.id).delete()

        x, y = random.choice(list(cls.get_available_positions(person.place.x, person.place.y)))

        model = Building.objects.create(x=x,
                                        y=y,
                                        name_forms=s11n.to_json(name_forms.serialize()),
                                        place=person.place._model,
                                        person=person._model,
                                        state=BUILDING_STATE.WORKING,
                                        type=person.type.building_type)

        prototype = cls(model=model)

        buildings_storage.add_item(prototype.id, prototype)
        buildings_storage.update_version()

        return prototype

    def destroy(self):
        from game.map.places.storage import buildings_storage
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
        from game.map.places.storage import buildings_storage
        self._model.save()
        buildings_storage.update_version()


class ResourceExchangePrototype(BasePrototype):
    _model_class = ResourceExchange
    _readonly = ('id', 'bill_id', 'resource_1', 'resource_2')
    _bidirectional = ()
    _get_by = ('id',)

    @property
    def place_1(self):
        from game.map.places.storage import places_storage
        return places_storage[self._model.place_1_id]

    @property
    def place_2(self):
        from game.map.places.storage import places_storage
        return places_storage[self._model.place_2_id]

    @lazy_property
    def bill(self):
        from game.bills.prototypes import BillPrototype
        return BillPrototype.get_by_id(self.bill_id)

    def get_resources_for_place(self, place):
        if place.id == self.place_1.id:
            return (self.resource_1, self.resource_2, self.place_2)
        if place.id == self.place_2.id:
            return (self.resource_2, self.resource_1, self.place_1)
        return (RESOURCE_EXCHANGE_TYPE.NONE, RESOURCE_EXCHANGE_TYPE.NONE, None)

    @classmethod
    def create(cls, place_1, place_2, resource_1, resource_2, bill):
        from game.map.places.storage import resource_exchange_storage

        model = cls._model_class.objects.create(bill=bill._model if bill is not None else None,
                                                place_1=place_1._model,
                                                place_2=place_2._model,
                                                resource_1=resource_1,
                                                resource_2=resource_2)
        prototype = cls(model=model)

        resource_exchange_storage.add_item(prototype.id, prototype)
        resource_exchange_storage.update_version()

        return prototype

    def remove(self):
        from game.map.places.storage import resource_exchange_storage

        self._model.delete()

        resource_exchange_storage.update_version()
        resource_exchange_storage.refresh()
