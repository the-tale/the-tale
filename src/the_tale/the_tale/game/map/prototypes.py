
import smart_imports

smart_imports.all()


class MapInfoPrototype(utils_prototypes.BasePrototype):
    _model_class = models.MapInfo
    _readonly = ('id', 'turn_number', 'world_id', 'width', 'height')

    @utils_decorators.lazy_property
    def terrain(self):
        data = s11n.from_json(self._model.terrain)
        terrain = []
        for row in data:
            terrain.append([])
            for cell in row:
                terrain[-1].append(relations.TERRAIN(cell))
        return terrain

    @utils_decorators.lazy_property
    def statistics(self):
        statistics = s11n.from_json(self._model.statistics)
        statistics['race_percents'] = dict((game_relations.RACE(int(key)), value) for key, value in statistics['race_percents'].items())
        statistics['person_race_percents'] = dict((game_relations.RACE(int(key)), value) for key, value in statistics['person_race_percents'].items())
        statistics['race_cities'] = dict((game_relations.RACE(int(key)), value) for key, value in statistics['race_cities'].items())
        statistics['terrain_percents'] = dict((relations.MAP_STATISTICS(int(key)), value) for key, value in statistics['terrain_percents'].items())
        return statistics

    @utils_decorators.lazy_property
    def cells(self):
        return generator.descriptors.UICells.deserialize(s11n.from_json(self._model.cells))

    @utils_decorators.lazy_property
    def terrain_percents(self):
        return self.statistics['terrain_percents']

    @utils_decorators.lazy_property
    def race_percents(self):
        return self.statistics['race_percents']

    @utils_decorators.lazy_property
    def roads_map(self):
        return generator.drawer.get_roads_map(w=conf.settings.WIDTH, h=conf.settings.HEIGHT, roads=roads_storage.roads.all())

    @utils_decorators.lazy_property
    def person_race_percents(self):
        return self.statistics['person_race_percents']

    @property
    def race_cities(self):
        return self.statistics['race_cities']

    ######################
    # object operations
    ######################

    @classmethod
    def remove_old_infos(cls):
        map_info_ids, world_info_ids = zip(*models.MapInfo.objects.order_by('-created_at', '-turn_number')[:2].values_list('id', 'world_id'))
        models.MapInfo.objects.exclude(id__in=map_info_ids).delete()
        models.WorldInfo.objects.exclude(id__in=world_info_ids).delete()

    @classmethod
    def create(cls, turn_number, width, height, terrain, world):
        terrain_percents = {}

        terrain_squares = collections.defaultdict(int)

        for y in range(0, height):
            for x in range(0, width):
                cell = world.generator.cell_info(x, y)

                if cell.height < -0.2:
                    terrain_squares[relations.MAP_STATISTICS.LOWLANDS] += 1
                elif cell.height < 0.3:
                    terrain_squares[relations.MAP_STATISTICS.PLAINS] += 1
                else:
                    terrain_squares[relations.MAP_STATISTICS.UPLANDS] += 1

                if cell.vegetation == deworld_layers.VEGETATION_TYPE.DESERT:
                    terrain_squares[relations.MAP_STATISTICS.DESERTS] += 1
                elif cell.vegetation == deworld_layers.VEGETATION_TYPE.GRASS:
                    terrain_squares[relations.MAP_STATISTICS.GRASS] += 1
                else:
                    terrain_squares[relations.MAP_STATISTICS.FORESTS] += 1

        total_cells = width * height

        terrain_percents = dict((id_.value, float(square) / total_cells) for id_, square in terrain_squares.items())

        person_race_percents = map_logic.get_person_race_percents(persons_storage.persons.all())
        race_percents = map_logic.get_race_percents(places_storage.places.all())

        # race to cities percents
        race_cities = dict((race.value, 0) for race in game_relations.RACE.records)
        for place_model in places_models.Place.objects.all():
            place = places_logic.load_place(place_model=place_model)
            race_cities[place.race.value] += 1

        statistics = {'terrain_percents': terrain_percents,
                      'person_race_percents': person_race_percents,
                      'race_percents': race_percents,
                      'race_cities': race_cities}

        model = models.MapInfo.objects.create(turn_number=turn_number,
                                              width=width,
                                              height=height,
                                              terrain=s11n.to_json([[cell.value for cell in row] for row in terrain]),
                                              cells=s11n.to_json(generator.descriptors.UICells.create(world.generator).serialize()),
                                              world=world._model,
                                              statistics=s11n.to_json(statistics))
        return cls(model)


class WorldInfoPrototype(utils_prototypes.BasePrototype):
    _model_class = models.WorldInfo
    _readonly = ('id',)
    _get_by = ('id', )

    @utils_decorators.lazy_property
    def generator(self):
        world_data = s11n.from_json(self._model.data)
        return deworld.World.deserialize(config=deworld.BaseConfig, data=world_data)

    @classmethod
    def create(cls, w, h):
        generator = deworld.World(w=w, h=h, config=deworld.BaseConfig)

        model = models.WorldInfo.objects.create(data=s11n.to_json(generator.serialize()))

        return cls(model)

    @classmethod
    def create_from_generator(cls, generator):
        model = models.WorldInfo.objects.create(data=s11n.to_json(generator.serialize()))
        return cls(model)
