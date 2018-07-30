
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
