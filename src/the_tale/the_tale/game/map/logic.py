
import smart_imports

smart_imports.all()


def create_test_map_info():
    from . import prototypes
    storage.map_info.set_item(prototypes.MapInfoPrototype.create(turn_number=0,
                                                                 width=conf.settings.WIDTH,
                                                                 height=conf.settings.HEIGHT,
                                                                 terrain=[[relations.TERRAIN.PLANE_GREENWOOD for j in range(conf.settings.WIDTH)] for i in range(conf.settings.HEIGHT)],  # pylint: disable=W0612
                                                                 world=prototypes.WorldInfoPrototype.create(w=conf.settings.WIDTH, h=conf.settings.HEIGHT)))


_TERRAIN_LINGUISTICS_CACHE = {}


def get_terrain_linguistics_restrictions(terrain):

    if _TERRAIN_LINGUISTICS_CACHE:
        return _TERRAIN_LINGUISTICS_CACHE[terrain]

    for terrain_record in relations.TERRAIN.records:
        _TERRAIN_LINGUISTICS_CACHE[terrain_record] = (linguistics_restrictions.get(terrain_record),
                                                      linguistics_restrictions.get(terrain_record.meta_terrain),
                                                      linguistics_restrictions.get(terrain_record.meta_height),
                                                      linguistics_restrictions.get(terrain_record.meta_vegetation))

    return _TERRAIN_LINGUISTICS_CACHE[terrain]


def region_url(turn=None):
    arguments = {'api_version': conf.settings.REGION_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    if turn is not None:
        arguments['turn'] = turn

    return dext_urls.url('game:map:api-region', **arguments)


def region_versions_url():
    arguments = {'api_version': conf.settings.REGION_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return dext_urls.url('game:map:api-region-versions', **arguments)


def get_person_race_percents(persons):
    race_powers = dict((race.value, 0) for race in game_relations.RACE.records)

    for person in persons:
        race_powers[person.race.value] += politic_power_storage.persons.total_power_fraction(person.id)

    total_power = sum(race_powers.values())

    if total_power == 0:
        return {race.value: 1.0 / len(game_relations.RACE.records) for race in game_relations.RACE.records}

    return {race: power / total_power for race, power in race_powers.items()}


def get_race_percents(places):
    race_powers = dict((race.value, 0) for race in game_relations.RACE.records)

    for place in places:
        for race in game_relations.RACE.records:
            race_powers[race.value] += place.races.get_race_percents(race) * place.attrs.size

    total_power = sum(race_powers.values()) + 1  # +1 - to prevent division by 0

    return dict((race_id, float(power) / total_power) for race_id, power in race_powers.items())
