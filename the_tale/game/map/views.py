# coding: utf-8

from dext.common.utils import views as dext_views

from utg import relations as utg_relations
from utg import words as utg_words

from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.game import relations as game_relations

from the_tale.game.persons import relations as persons_relations

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.conf import map_settings

from the_tale.game.map.places import storage as places_storage
from the_tale.game.map.places import prototypes as places_prototypes
from the_tale.game.map.places import logic as places_logic
from the_tale.game.map.places import relations as places_relations

from the_tale.game.abilities.relations import ABILITY_TYPE



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

    place = places_storage.places_storage.get_by_coordinates(x, y)

    place_modifiers = None

    chronicle_records = []
    exchanges = []

    place_info = places_logic.place_info(place) if place is not None else None
        # place_modifiers = place.modifiers

        # chronicle_records = RecordPrototype.get_last_actor_records(place, places_conf.places_settings.CHRONICLE_RECORDS_NUMBER)

        # for exchange in places_storage.resource_exchange_storage.get_exchanges_for_place(place):
        #     resource_1, resource_2, place_2 = exchange.get_resources_for_place(place)
        #     exchanges.append((resource_1, resource_2, place_2, exchange.bill))

    terrain_points = []

    building = places_storage.buildings_storage.get_by_coordinates(x, y)



    return dext_views.Page('map/cell_info.html',
                           content={'place_info': place_info,
                                    'CITY_MODIFIERS': places_relations.CITY_MODIFIERS,
                                    'PERSON_TYPE': persons_relations.PERSON_TYPE,
                                    'RACE': game_relations.RACE,
                                    'GENDER': game_relations.GENDER,
                                    'HABIT_TYPE': game_relations.HABIT_TYPE,

                                    'building': building,
                                    'place_modifiers': place_modifiers,
                                    'exchanges': exchanges,
                                    'cell': cell,
                                    'terrain': terrain,
                                    'nearest_place_name': nearest_place_name,
                                    'PlaceParametersDescription': places_prototypes.PlaceParametersDescription,
                                    'x': x,
                                    'y': y,
                                    'terrain_points': terrain_points,
                                    'chronicle_records': chronicle_records,
                                    'hero': heroes_logic.load_hero(account_id=context.account.id) if context.account.is_authenticated() else None,
                                    'resource': context.resource,
                                    'ABILITY_TYPE': ABILITY_TYPE})
