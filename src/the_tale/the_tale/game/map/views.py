# coding: utf-8

from dext.common.utils import views as dext_views

from utg import relations as utg_relations
from utg import words as utg_words

from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.game.chronicle import prototypes as chronicle_prototypes
from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.conf import map_settings

from the_tale.game.places import storage as places_storage
from the_tale.game.places import info as places_info

from the_tale.game.abilities.relations import ABILITY_TYPE

from . import conf


########################################
# processors definition
########################################

########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='map')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())

########################################
# views
########################################


@resource('')
def index(context):
    return dext_views.Page('map/index.html',
                           content={'current_map_version': map_info_storage.version,
                                    'resource': context.resource})


@dext_views.IntArgumentProcessor(error_message=u'Неверная X координата', get_name='x', context_name='x')
@dext_views.IntArgumentProcessor(error_message=u'Неверная Y координата', get_name='y', context_name='y')
@resource('cell-info')
def cell_info(context):

    x, y = context.x, context.y

    if x < 0 or y < 0 or x >= map_settings.WIDTH or y >= map_settings.HEIGHT:
        raise dext_views.ViewError(code='outside_map', message=u'Запрашиваемая зона не принадлежит карте')

    map_info = map_info_storage.item

    terrain = map_info.terrain[y][x]

    cell = map_info.cells.get_cell(x, y)

    nearest_place_name = None
    nearest_place = map_info.get_dominant_place(x, y)
    if nearest_place:
        nearest_place_name = nearest_place.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))

    place = places_storage.places.get_by_coordinates(x, y)

    exchanges = []

    terrain_points = []

    building = places_storage.buildings.get_by_coordinates(x, y)

    return dext_views.Page('map/cell_info.html',
                           content={'place': place,
                                    'building': building,
                                    'place_bills': places_info.place_info_bills(place) if place else None,
                                    'place_chronicle': chronicle_prototypes.chronicle_info(place, conf.map_settings.CHRONICLE_RECORDS_NUMBER) if place else None,
                                    'exchanges': exchanges,
                                    'cell': cell,
                                    'terrain': terrain,
                                    'nearest_place_name': nearest_place_name,
                                    'x': x,
                                    'y': y,
                                    'terrain_points': terrain_points,
                                    'hero': heroes_logic.load_hero(account_id=context.account.id) if context.account.is_authenticated() else None,
                                    'resource': context.resource,
                                    'ABILITY_TYPE': ABILITY_TYPE})
