
import smart_imports

smart_imports.all()


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
                           content={'current_map_version': storage.map_info.version,
                                    'resource': context.resource})


@utils_api.Processor(versions=(conf.settings.REGION_API_VERSION,))
@dext_views.IntArgumentProcessor(error_message='Неверный формат номера хода', get_name='turn', context_name='turn', default_value=None)
@resource('api', 'region', name='api-region')
def region(context):
    if context.turn is None:
        region = models.MapRegion.objects.latest('created_at')
    else:
        try:
            region = models.MapRegion.objects.get(turn_number=context.turn)
        except models.MapRegion.DoesNotExist:
            raise dext_views.ViewError(code='no_region_found', message='Описание карты для заданного хода не найдено')

    return dext_views.AjaxOk(content={'region': region.data,
                                      'turn': region.turn_number})


@utils_api.Processor(versions=(conf.settings.REGION_VERSIONS_API_VERSION,))
@resource('api', 'region-versions', name='api-region-versions')
def region_versions(context):
    return dext_views.AjaxOk(content={'turns': list(models.MapRegion.objects.values_list('turn_number', flat=True))})


@dext_views.IntArgumentProcessor(error_message='Неверная X координата', get_name='x', context_name='x')
@dext_views.IntArgumentProcessor(error_message='Неверная Y координата', get_name='y', context_name='y')
@resource('cell-info')
def cell_info(context):

    x, y = context.x, context.y

    if x < 0 or y < 0 or x >= conf.settings.WIDTH or y >= conf.settings.HEIGHT:
        raise dext_views.ViewError(code='outside_map', message='Запрашиваемая зона не принадлежит карте')

    map_info = storage.map_info.item

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

    place_inner_circle = None
    persons_inner_circles = None

    events = None

    if place:
        place_inner_circle = politic_power_logic.get_inner_circle(place_id=place.id)
        persons_inner_circles = {person.id: politic_power_logic.get_inner_circle(person_id=person.id)
                                 for person in place.persons}

        total_events, events = chronicle_tt_services.chronicle.cmd_get_last_events(tags=[place.meta_object().tag],
                                                                                   number=conf.settings.CHRONICLE_RECORDS_NUMBER)

        tt_api_events_log.fill_events_wtih_meta_objects(events)

    return dext_views.Page('map/cell_info.html',
                           content={'place': place,
                                    'building': building,
                                    'places_power_storage': politic_power_storage.places,
                                    'persons_power_storage': politic_power_storage.persons,
                                    'persons_inner_circles': persons_inner_circles,
                                    'place_inner_circle': place_inner_circle,
                                    'place_bills': places_info.place_info_bills(place) if place else None,
                                    'place_chronicle': events,
                                    'exchanges': exchanges,
                                    'cell': cell,
                                    'terrain': terrain,
                                    'nearest_place_name': nearest_place_name,
                                    'x': x,
                                    'y': y,
                                    'terrain_points': terrain_points,
                                    'hero': heroes_logic.load_hero(account_id=context.account.id) if context.account.is_authenticated else None,
                                    'resource': context.resource,
                                    'ABILITY_TYPE': abilities_relations.ABILITY_TYPE})
