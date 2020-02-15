import smart_imports

smart_imports.all()


class MapInfoStorage(utils_storage.SingleStorage):
    SETTINGS_KEY = 'map info change time'
    EXCEPTION = map_exceptions.MapStorageError

    def _construct_zero_item(self):
        return None

    def refresh(self):
        self.clear()

        try:
            self._item = map_prototypes.MapInfoPrototype(map_prototypes.MapInfoPrototype._model_class.objects.order_by('-turn_number',
                                                                                                                       '-id')[0])
        except IndexError:
            self._item = None

        self._version = global_settings[self.SETTINGS_KEY]

    def _get_next_version(self):
        return '%d-%f' % (game_turn.number(), time.time())


map_info = MapInfoStorage()


class CellInfo:
    __slots__ = ('terrain', 'dominant_place_id', 'place_id', 'nearest_place_id', 'building_id', 'roads_ids', 'transport', 'safety')

    def __init__(self):
        self.reset()

    def reset(self):
        self.terrain = None

        self.dominant_place_id = None
        self.place_id = None
        self.nearest_place_id = None
        self.building_id = None
        self.roads_ids = []

        self.transport = 0
        self.safety = 0

    def battles_per_turn(self):
        return 1.0 - self.safety

    def contains_object(self):
        return (self.roads_ids or
                self.place_id is not None or
                self.building_id is not None)

    def dominant_place(self):
        from the_tale.game.places import storage as places_storage

        if self.dominant_place_id is None:
            return None

        return places_storage.places[self.dominant_place_id]

    def nearest_place(self):
        from the_tale.game.places import storage as places_storage
        # must be always setupped
        return places_storage.places[self.nearest_place_id]

    def place(self):
        from the_tale.game.places import storage as places_storage

        if self.place_id is None:
            return None

        return places_storage.places[self.place_id]

    def building(self):
        from the_tale.game.places import storage as places_storage

        if self.building_id is None:
            return None

        return places_storage.buildings[self.building_id]

    def roads(self):
        from the_tale.game.roads import storage as roads_storage

        for road_id in self.roads_ids:
            yield roads_storage.roads[road_id]

    def _transport_effects(self):
        yield ('мир', c.CELL_TRANSPORT_BASE)

        if self.terrain.meta_height.is_HILLS:
            yield ('холмы', c.CELL_TRANSPORT_HILLS)

        if self.terrain.meta_height.is_MOUNTAINS:
            yield ('горы', c.CELL_TRANSPORT_MOUNTAINS)

        if not self.contains_object():
            if self.terrain.meta_vegetation.is_TREES:
                yield ('леса', c.CELL_TRANSPORT_TREES)

            if self.terrain.meta_terrain.is_SWAMP:
                yield ('болота', c.CELL_TRANSPORT_SWAMP)

            if self.terrain.meta_terrain.is_JUNGLE:
                yield ('джунгли', c.CELL_TRANSPORT_JUNGLE)

            yield ('магические потоки', c.CELL_TRANSPORT_MAGIC)

        dominant_place = self.dominant_place()

        if dominant_place is None or dominant_place.is_frontier:
            yield ('бездорожье фронтира', -c.WHILD_TRANSPORT_PENALTY)

        if dominant_place is None:
            return

        yield (dominant_place.name, dominant_place.attrs.transport)

        if self.place_id:
            yield ('городские дороги', c.CELL_TRANSPORT_HAS_MAIN_ROAD)

        elif self.roads_ids:
            # дороги всегда должны иметь бонус к транспорту по сравниению с любым другим объектом (кроме города)
            # чтобы при прочих равных герой двигался по дорогам
            yield (f'дорога из {self.dominant_place().utg_name.forms[1]}', c.CELL_TRANSPORT_HAS_MAIN_ROAD)

        else:
            # building or none
            yield ('просёлочные дороги', c.CELL_TRANSPORT_HAS_OFF_ROAD)

    def transport_effects(self):
        effects = list(self._transport_effects())

        transport = sum(value for name, value in effects)

        if transport < c.CELL_TRANSPORT_MIN:
            effects.append(('Серый Орден', c.CELL_TRANSPORT_MIN - transport))

        return effects

    def _safety_effects(self):
        yield ('мир', 1.0 - c.BATTLES_PER_TURN)

        if self.terrain.meta_height.is_HILLS:
            yield ('холмы', c.CELL_SAFETY_HILLS)

        if self.terrain.meta_height.is_MOUNTAINS:
            yield ('горы', c.CELL_SAFETY_MOUNTAINS)

        if self.terrain.meta_vegetation.is_TREES:
            yield ('леса', c.CELL_SAFETY_TREES)

        dominant_place = self.dominant_place()

        if dominant_place is None or dominant_place.is_frontier:
            yield ('монстры фронтира', -c.WHILD_BATTLES_PER_TURN_BONUS)

        if dominant_place is None:
            return

        yield (dominant_place.name, dominant_place.attrs.safety)

        if not self.contains_object():
            # берём модуль, поскольку безопасность города может быть отрицательной,
            # а нехватка патрулей всегда должна давать штраф
            yield ('нехватка патрулей', c.CELL_SAFETY_NO_PATRULES * abs(dominant_place.attrs.safety))

    def safety_effects(self):
        effects = list(self._safety_effects())

        safety = sum(value for name, value in effects)

        if safety < c.CELL_SAFETY_MIN:
            effects.append(('Серый Орден', c.CELL_SAFETY_MIN - safety))

        if safety > 1:
            effects.append(('демоны', 1 - safety))

        return effects

    def normal_travel_cost(self):
        return self.travel_cost(expected_battle_complexity=1.0)

    def travel_cost(self, expected_battle_complexity):
        return navigation_pathfinder.cell_travel_cost(transport=self.transport,
                                                      safety=self.safety,
                                                      expected_battle_complexity=expected_battle_complexity)


class CellsStorage:
    __slots__ = ('_places_version',
                 '_buildings_version',
                 '_roads_version',
                 '_map_info_version',

                 '_map',

                 '_places_terrains',
                 '_places_area',
                 '_places_cells',

                 '_navigators')

    def __init__(self):
        self._places_version = None
        self._buildings_version = None
        self._roads_version = None
        self._map_info_version = None

        self._map = []
        self._places_terrains = {}
        self._places_area = {}
        self._places_cells = {}

        self._navigators = {risk_level: navigation_navigator.Navigator()
                            for risk_level in heroes_relations.RISK_LEVEL.records}

        for y in range(map_conf.settings.HEIGHT):
            self._map.append([CellInfo() for x in range(map_conf.settings.WIDTH)])

    def is_changed(self):
        return (places_storage.places.version != self._places_version or
                places_storage.buildings.version != self._buildings_version or
                roads_storage.roads.version != self._roads_version or
                map_info.version != self._map_info_version)

    def actualize_versions(self):
        self._places_version = places_storage.places.version
        self._buildings_version = places_storage.buildings.version
        self._roads_version = roads_storage.roads.version
        self._map_info_version = map_info.version

    def reset_versions(self):
        self._places_version = None
        self._buildings_version = None
        self._roads_version = None
        self._map_info_version = None

    def _cells_iterator(self):
        for y in range(map_conf.settings.HEIGHT):
            for x in range(map_conf.settings.WIDTH):
                yield x, y, self._map[y][x]

    def __call__(self, x, y):
        self.sync()
        return self._map[y][x]

    def get_map(self):
        self.sync()
        return self._map

    def place_terrains(self, place_id):
        self.sync()
        return self._places_terrains[place_id]

    def place_area(self, place_id):
        self.sync()
        return self._places_area[place_id]

    def place_cells(self, place_id):
        self.sync()
        return self._places_cells[place_id]

    def sync(self, force=False):

        if not force and not self.is_changed():
            return

        self.reset()

        nearest_cells.update(self._map)

        self.sync_terrain()
        self.sync_places_caches()

        self.sync_transport()
        self.sync_safety()

        for risk_level in heroes_relations.RISK_LEVEL.records:
            travel_cost = navigation_pathfinder.TravelCost(map=self._map,
                                                           expected_battle_complexity=risk_level.expected_battle_complexity)
            self._navigators[risk_level].sync(travel_cost)

        self.actualize_versions()

    def reset(self):
        from the_tale.game.places import storage as places_storage

        self.reset_versions()

        for x, y, cell in self._cells_iterator():
            cell.reset()

        self._places_terrains = {place.id: set() for place in places_storage.places.all()}
        self._places_area = {place.id: 0 for place in places_storage.places.all()}
        self._places_cells = {place.id: [] for place in places_storage.places.all()}

    def sync_terrain(self):
        for x, y, cell in self._cells_iterator():
            cell.terrain = map_info.item.terrain[y][x]

    def sync_places_caches(self):
        for x, y, cell in self._cells_iterator():
            if cell.dominant_place_id is None:
                continue

            self._places_terrains[cell.dominant_place_id].add(cell.terrain)
            self._places_area[cell.dominant_place_id] += 1
            self._places_cells[cell.dominant_place_id].append((x, y))

    def sync_transport(self):
        for x, y, cell in self._cells_iterator():
            cell.transport = sum(value for name, value in cell.transport_effects())

    def sync_safety(self):
        for x, y, cell in self._cells_iterator():
            cell.safety = sum(value for name, value in cell.safety_effects())

    def find_path_to_place(self, from_x, from_y, to_place_id, cost_modifiers, risk_level):
        self.sync()

        return self._navigators[risk_level].build_path_to_place(from_x=from_x,
                                                                from_y=from_y,
                                                                to_place_id=to_place_id,
                                                                cost_modifiers=cost_modifiers)

    def get_path_between_places(self, from_place_id, to_place_id, cost_modifiers, risk_level):
        self.sync()

        return self._navigators[risk_level].get_path_between_places(from_place_id=from_place_id,
                                                                    to_place_id=to_place_id,
                                                                    cost_modifiers=cost_modifiers)[0]


cells = CellsStorage()
