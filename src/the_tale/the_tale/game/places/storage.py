
import smart_imports

smart_imports.all()


class PlacesStorage(utils_storage.CachedStorage):
    SETTINGS_KEY = 'places change time'
    EXCEPTION = exceptions.PlacesStorageError

    def _construct_object(self, model):
        return logic.load_place(place_model=model)

    def _save_object(self, place):
        return logic.save_place(place)

    def _get_all_query(self):
        return list(models.Place.objects.all())

    def _reset_cache(self):
        self._nearest_places = {}

    def _update_cached_data(self, item):
        # _nearest_places calculated in there getter
        pass

    def get_choices(self, exclude=()):
        self.sync()
        return [(place.id, place.name)
                for place in sorted(self.all(), key=lambda p: p.name)
                if place.id not in exclude]

    def get_by_coordinates(self, x, y):
        self.sync()
        for place in self.all():
            if place.x == x and place.y == y:
                return place

        return None

    def nearest_places_with_distance(self, center_place_id, number=None):
        # sync does not required

        if number is None:
            number = len(self)

        if number < 1:
            return []

        if center_place_id not in self._nearest_places:
            center_place = self[center_place_id]
            self._nearest_places[center_place_id] = [(navigation_logic.manhattan_distance(center_place.x, center_place.y,
                                                                                          place.x, place.y), place.id)
                                                     for place in self.all()]
            self._nearest_places[center_place_id].sort()

        places = self._nearest_places[center_place_id]

        if number >= len(places):
            return places

        stop_distance = places[number - 1][0]

        return [record for record in places if record[0] <= stop_distance]

    def nearest_places(self, center_place_id, number=None):
        return [self[place_id]
                for distance, place_id in self.nearest_places_with_distance(center_place_id, number)]

    def expected_minimum_quest_distance(self):
        radiuses_sum = sum(self.nearest_places_with_distance(p.id, c.MINIMUM_QUESTS_REGION_SIZE)[-1][0]
                           for p in self.all())

        # считаем как путешествие на среднюю дистанцию туда-обратно

        radius = radiuses_sum / len(self)

        return radius * 2

    def shift_all(self, dx, dy):
        self.sync()

        for place in self.all():
            place.shift(dx, dy)

        self.save_all()


places = PlacesStorage()


class BuildingsStorage(utils_storage.CachedStorage):
    SETTINGS_KEY = 'buildings change time'
    EXCEPTION = exceptions.BuildingsStorageError

    def _construct_object(self, model):
        return logic.load_building(building_model=model)

    def _save_object(self, building):
        return logic.save_building(building)

    def _get_all_query(self):
        return models.Building.objects.exclude(state=relations.BUILDING_STATE.DESTROYED)

    def _reset_cache(self):
        self._persons_to_buildings = {}

    def _update_cached_data(self, item):
        self._persons_to_buildings[item.person.id] = item

    def get_by_person_id(self, person_id):
        self.sync()
        return self._persons_to_buildings.get(person_id)

    def get_by_coordinates(self, x, y):
        self.sync()
        for building in self.all():
            if building.x == x and building.y == y:
                return building

        return None

    def shift_all(self, dx, dy):
        for building in self.all():
            building.shift(dx, dy)
        self.save_all()

    def get_choices(self):
        self.sync()

        buildings = {}

        for building in self.all():
            place_id = building.person.place_id

            if place_id not in buildings:
                buildings[place_id] = []

            buildings[place_id].append(building)

        for place_buildings in buildings.values():
            place_buildings.sort(key=lambda building: building.name)

        choices = []

        for place_id, buildings_list in buildings.items():
            place_choices = [(building.id, building.name) for building in buildings_list]
            choices.append((places[place_id].name, place_choices))

        choices.sort()

        return choices


buildings = BuildingsStorage()


class ResourceExchangeStorage(utils_storage.PrototypeStorage):
    SETTINGS_KEY = 'resource exchange change time'
    EXCEPTION = exceptions.ResourceExchangeStorageError
    PROTOTYPE = prototypes.ResourceExchangePrototype

    def get_exchanges_for_place(self, place):
        exchanges = []
        for exchange in self.all():
            if place.id in (exchange.place_1.id if exchange.place_1 is not None else None,
                            exchange.place_2.id if exchange.place_2 is not None else None):
                exchanges.append(exchange)
        return exchanges

    def get_exchange_for_bill_id(self, bill_id):
        for exchange in self.all():
            if exchange.bill_id == bill_id:
                return exchange
        return None


resource_exchanges = ResourceExchangeStorage()


class EffectsStorage(utils_storage.CachedStorage):
    SETTINGS_KEY = 'effects change time'
    EXCEPTION = exceptions.EffectsStorageError

    def _construct_object(self, item):
        return item

    def _save_object(self, item):
        raise NotImplementedError

    def _get_all_query(self):
        return tt_services.effects.cmd_list()

    def _reset_cache(self):
        self._effects_by_place = {}

    def _update_cached_data(self, item):
        if item.entity not in self._effects_by_place:
            self._effects_by_place[item.entity] = []

        self._effects_by_place[item.entity].append(item)

    def effects_for_place(self, place_id):
        self.sync()
        return self._effects_by_place.get(place_id, ())


effects = EffectsStorage()


class ClansRegionsStorage(utils_storage.DependentStorage):
    __slots__ = ('_places_version',
                 '_roads_version',
                 '_regions')

    def __init__(self):
        super().__init__()

        self._regions = {}

    def expected_version(self):
        return (places_storage.places.version,
                roads_storage.roads.version)

    def reset(self):
        super().reset()

        self._regions = {}

    def recalculate(self):
        for place in places.all():
            self._regions[place.id] = objects.ClanRegion(place.attrs.clan_protector, {place.id})

        for road in roads_storage.roads.all():
            if road.place_1.attrs.clan_protector == road.place_2.attrs.clan_protector:
                self._regions[road.place_1_id].merge(self._regions[road.place_2_id])
                self._regions[road.place_2_id] = self._regions[road.place_1_id]

    def region_for_place(self, place_id):
        self.sync()
        return self._regions[place_id]


clans_regions = ClansRegionsStorage()
