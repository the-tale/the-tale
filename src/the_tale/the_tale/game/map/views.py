
import smart_imports

smart_imports.all()


########################################
# processors definition
########################################

########################################
# resource and global processors
########################################
resource = utils_views.Resource(name='map')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())

########################################
# views
########################################


@resource('')
def index(context):
    return utils_views.Page('map/index.html',
                            content={'current_map_version': storage.map_info.version,
                                     'resource': context.resource})


@utils_api.Processor(versions=(conf.settings.REGION_API_VERSION,))
@utils_views.IntArgumentProcessor(error_message='Неверный формат номера хода', get_name='turn', context_name='turn', default_value=None)
@resource('api', 'region', name='api-region')
def region(context):
    if context.turn is None:
        region = models.MapRegion.objects.latest('created_at')
    else:
        try:
            region = models.MapRegion.objects.get(turn_number=context.turn)
        except models.MapRegion.DoesNotExist:
            raise utils_views.ViewError(code='no_region_found', message='Описание карты для заданного хода не найдено')

    return utils_views.AjaxOk(content={'region': region.data,
                                       'turn': region.turn_number})


@utils_api.Processor(versions=(conf.settings.REGION_VERSIONS_API_VERSION,))
@resource('api', 'region-versions', name='api-region-versions')
def region_versions(context):
    return utils_views.AjaxOk(content={'turns': list(models.MapRegion.objects.values_list('turn_number', flat=True))})


@utils_views.IntArgumentProcessor(error_message='Неверная X координата', get_name='x', context_name='x')
@utils_views.IntArgumentProcessor(error_message='Неверная Y координата', get_name='y', context_name='y')
@resource('cell-info')
def cell_info(context):

    x, y = context.x, context.y

    if x < 0 or y < 0 or x >= conf.settings.WIDTH or y >= conf.settings.HEIGHT:
        raise utils_views.ViewError(code='outside_map', message='Запрашиваемая зона не принадлежит карте')

    map_info = storage.map_info.item

    terrain = map_info.terrain[y][x]

    cell = map_info.cells.get_cell(x, y)

    nearest_place_name = None
    nearest_place = storage.cells(x, y).dominant_place()
    if nearest_place:
        nearest_place_name = nearest_place.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))

    place = places_storage.places.get_by_coordinates(x, y)

    exchanges = []

    terrain_points = []

    place_inner_circle = None
    persons_inner_circles = None

    events = None

    hero = None

    if context.account.is_authenticated:
        hero = heroes_logic.load_hero(account_id=context.account.id)

    emissaries = None
    emissaries_powers = {}

    clan_region = None
    protector_candidates = None

    if place:
        clan_region = places_storage.clans_regions.region_for_place(place.id)

        place_inner_circle = politic_power_logic.get_inner_circle(place_id=place.id)
        persons_inner_circles = {person.id: politic_power_logic.get_inner_circle(person_id=person.id)
                                 for person in place.persons}

        total_events, events = chronicle_tt_services.chronicle.cmd_get_last_events(tags=[place.meta_object().tag],
                                                                                   number=conf.settings.CHRONICLE_RECORDS_NUMBER)

        tt_api_events_log.fill_events_wtih_meta_objects(events)

        emissaries = emissaries_logic.load_emissaries_for_place(place.id)
        emissaries = [emissary for emissary in emissaries if emissary.state.is_IN_GAME]

        emissaries_powers = politic_power_logic.get_emissaries_power([emissary.id for emissary in emissaries])

        emissaries_logic.sort_for_ui(emissaries, emissaries_powers)

        protector_candidates = places_logic.protector_candidates_for_ui(place.id)

    path_modifier = None
    path_modifier_effects = None

    if hero and place:
        path_modifier, path_modifier_effects = heroes_logic.get_place_path_modifiers_info(hero, place)

    return utils_views.Page('map/cell_info.html',
                            content={'place': place,
                                     'building': storage.cells(x, y).building(),
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
                                     'hero': hero,
                                     'resource': context.resource,
                                     'cells': storage.cells,
                                     'path_modifier': path_modifier,
                                     'path_modifier_effects': path_modifier_effects,
                                     'emissaries': emissaries,
                                     'emissaries_powers': emissaries_powers,
                                     'clans_infos': clans_storage.infos,
                                     'clan_region': clan_region,
                                     'protector_candidates': protector_candidates})
