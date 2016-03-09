# coding: utf-8
import random
import math

from dext.common.utils import s11n

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.game import names

from the_tale.game.balance import constants as c

from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.conf import map_settings

from . import models
from . import relations


class BuildingPrototype(BasePrototype, names.ManageNameMixin):
    _model_class = models.Building
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
            return cls(models.Place.objects.get(x=x, y=y))
        except models.Place.DoesNotExist:
            return None

    @property
    def person(self):
        from the_tale.game.persons import storage as persons_storage
        return persons_storage.persons[self._model.person_id]

    @property
    def place(self):
        from the_tale.game.places import storage
        return storage.places[self._model.place_id]

    @property
    def terrain_change_power(self):
        # +1 to prevent power == 0
        power = self.place.attrs.terrain_radius * self.integrity * c.BUILDING_TERRAIN_POWER_MULTIPLIER + 1
        return int(round(power))

    def amortization_delta(self, turns_number):
        from the_tale.game.places import storage

        buildings_number = sum(storage.buildings.get_by_person_id(person.id) is not None
                               for person in self.place.persons)

        per_one_building = float(turns_number) / c.TURNS_IN_HOUR * c.BUILDING_AMORTIZATION_SPEED * self.person.attrs.building_amortization_speed
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
    def get_available_positions(cls, center_x, center_y, building_position_radius=c.BUILDING_POSITION_RADIUS): # pylint: disable=R0914
        from the_tale.game.places import storage
        from the_tale.game.roads.storage import roads_storage
        from the_tale.game.roads.relations import PATH_DIRECTION

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

        for place in storage.places.all():
            removed_positions.add((place.x, place.y))

        for building in storage.buildings.all():
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
        from the_tale.game.places import storage

        building = storage.buildings.get_by_person_id(person.id)

        if building:
            return building

        # remove any destroyed buildings for person
        cls._model_class.objects.filter(person_id=person.id).delete()

        x, y = random.choice(list(cls.get_available_positions(person.place.x, person.place.y)))

        model = models.Building.objects.create(x=x,
                                        y=y,
                                        data=s11n.to_json({'name': utg_name.serialize()}),
                                        place_id=person.place_id,
                                        person_id=person.id,
                                        state=relations.BUILDING_STATE.WORKING,
                                        created_at_turn=TimePrototype.get_current_turn_number(),
                                        type=person.type.building_type)

        prototype = cls(model=model)

        storage.buildings.add_item(prototype.id, prototype)
        storage.buildings.update_version()

        return prototype

    def destroy(self):
        from the_tale.game.places import storage
        self.state = relations.BUILDING_STATE.DESTROYED
        self.save()
        storage.buildings.update_version()
        storage.buildings.refresh()

    def map_info(self):
        return {'id': self.id,
                'pos': {'x': self.x, 'y': self.y},
                'person': self._model.person_id,
                'place': self._model.place_id,
                'type': self.type.value}

    def save(self):
        from the_tale.game.places import storage
        self._model.data = s11n.to_json(self.data)
        self._model.save()
        storage.buildings.update_version()


class ResourceExchangePrototype(BasePrototype):
    _model_class = models.ResourceExchange
    _readonly = ('id', 'bill_id', 'resource_1', 'resource_2')
    _bidirectional = ()
    _get_by = ('id',)

    @property
    def place_1(self):
        from the_tale.game.places import storage
        return storage.places.get(self._model.place_1_id)

    @property
    def place_2(self):
        from the_tale.game.places import storage
        return storage.places.get(self._model.place_2_id)

    @lazy_property
    def bill(self):
        from the_tale.game.bills.prototypes import BillPrototype
        return BillPrototype.get_by_id(self.bill_id)

    def get_resources_for_place(self, place):
        if place.id == self.place_1.id:
            return (self.resource_1, self.resource_2, self.place_2)
        if place.id == self.place_2.id:
            return (self.resource_2, self.resource_1, self.place_1)
        return (relations.RESOURCE_EXCHANGE_TYPE.NONE, relations.RESOURCE_EXCHANGE_TYPE.NONE, None)

    @classmethod
    def create(cls, place_1, place_2, resource_1, resource_2, bill):
        from the_tale.game.places import storage

        model = cls._model_class.objects.create(bill=bill._model if bill is not None else None,
                                                place_1_id=place_1.id if place_1 is not None else None,
                                                place_2_id=place_2.id if place_2 is not None else None,
                                                resource_1=resource_1,
                                                resource_2=resource_2)
        prototype = cls(model=model)

        storage.resource_exchanges.add_item(prototype.id, prototype)
        storage.resource_exchanges.update_version()

        return prototype

    def remove(self):
        from the_tale.game.places import storage

        self._model.delete()

        storage.resource_exchanges.update_version()
        storage.resource_exchanges.refresh()
