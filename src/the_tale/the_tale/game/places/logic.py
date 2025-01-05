
import smart_imports

smart_imports.all()


def tt_power_impacts(inner_circle, actor_type, actor_id, place, amount: int, fame: int):

    impact_types = [game_tt_services.IMPACT_TYPE.OUTER_CIRCLE]

    if inner_circle:
        impact_types.append(game_tt_services.IMPACT_TYPE.INNER_CIRCLE)

    for impact_type in impact_types:
        yield game_tt_services.PowerImpact(type=impact_type,
                                           actor_type=actor_type,
                                           actor_id=actor_id,
                                           target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                           target_id=place.id,
                                           amount=amount)

    if actor_type.is_HERO and 0 < fame:
        yield game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                           actor_type=actor_type,
                                           actor_id=actor_id,
                                           target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                           target_id=place.id,
                                           amount=fame)

    if not inner_circle:
        return


def impacts_from_hero(hero, place, power, inner_circle_places, impacts_generator=tt_power_impacts):
    can_change_power = hero.can_change_place_power(place)

    place_power = politic_power_logic.final_politic_power(power=power,
                                                          place=place,
                                                          hero=hero)

    yield from impacts_generator(inner_circle=hero.preferences.place_is_hometown(place) or (place.id in inner_circle_places),
                                 actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                 actor_id=hero.id,
                                 place=place,
                                 amount=place_power if can_change_power else 0,
                                 fame=c.HERO_FAME_PER_HELP if 0 < power else 0)


def load_place(place_id=None, place_model=None):
    try:
        if place_id is not None:
            place_model = models.Place.objects.get(id=place_id)
        elif place_model is None:
            return None
    except models.Place.DoesNotExist:
        return None

    data = s11n.from_json(place_model.data)

    place = objects.Place(id=place_model.id,
                          x=place_model.x,
                          y=place_model.y,
                          created_at_turn=place_model.created_at_turn,
                          updated_at_turn=place_model.updated_at_turn,
                          updated_at=place_model.updated_at,
                          created_at=place_model.created_at,
                          habit_honor=habits.Honor(raw_value=place_model.habit_honor),
                          habit_honor_positive=place_model.habit_honor_positive,
                          habit_honor_negative=place_model.habit_honor_negative,
                          habit_peacefulness=habits.Peacefulness(raw_value=place_model.habit_peacefulness),
                          habit_peacefulness_positive=place_model.habit_peacefulness_positive,
                          habit_peacefulness_negative=place_model.habit_peacefulness_negative,
                          is_frontier=place_model.is_frontier,
                          description=place_model.description,
                          race=place_model.race,
                          persons_changed_at_turn=place_model.persons_changed_at_turn,
                          utg_name=utg_words.Word.deserialize(data['name']),
                          attrs=attributes.Attributes.deserialize(data.get('attributes', {})),
                          races=races.Races.deserialize(data['races']),
                          modifier=place_model.modifier)

    place.attrs.sync()

    return place


def save_place(place, new=False):
    data = {'name': place.utg_name.serialize(),
            'attributes': place.attrs.serialize(),
            'races': place.races.serialize()}

    arguments = {'x': place.x,
                 'y': place.y,
                 'updated_at_turn': game_turn.number(),
                 'updated_at': datetime.datetime.now(),
                 'is_frontier': place.is_frontier,
                 'description': place.description,
                 'data': s11n.to_json(data),
                 'habit_honor_positive': place.habit_honor_positive,
                 'habit_honor_negative': place.habit_honor_negative,
                 'habit_peacefulness_positive': place.habit_peacefulness_positive,
                 'habit_peacefulness_negative': place.habit_peacefulness_negative,
                 'habit_honor': place.habit_honor.raw_value,
                 'habit_peacefulness': place.habit_peacefulness.raw_value,
                 'modifier': place._modifier,
                 'race': place.race,
                 'persons_changed_at_turn': place.persons_changed_at_turn}

    if new:
        place_model = models.Place.objects.create(created_at_turn=game_turn.number(), **arguments)
        place.id = place_model.id
        storage.places.add_item(place.id, place)
    else:
        models.Place.objects.filter(id=place.id).update(**arguments)

    storage.places.update_version()

    place.updated_at = datetime.datetime.now()


def create_place(x, y, size, utg_name, race, is_frontier=False):
    place = objects.Place(id=None,
                          x=x,
                          y=y,
                          updated_at=datetime.datetime.now(),
                          updated_at_turn=game_turn.number(),
                          created_at=datetime.datetime.now(),
                          created_at_turn=game_turn.number(),
                          habit_honor=habits.Honor(raw_value=0),
                          habit_honor_positive=0,
                          habit_honor_negative=0,
                          habit_peacefulness=habits.Peacefulness(raw_value=0),
                          habit_peacefulness_positive=0,
                          habit_peacefulness_negative=0,
                          is_frontier=is_frontier,
                          description='',
                          race=race,
                          persons_changed_at_turn=game_turn.number(),
                          attrs=attributes.Attributes(size=size),
                          utg_name=utg_name,
                          races=races.Races(),
                          modifier=modifiers.CITY_MODIFIERS.NONE)
    # place.refresh_attributes()
    save_place(place, new=True)
    return place


def api_list_url():
    arguments = {'api_version': conf.settings.API_LIST_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return utils_urls.url('game:places:api-list', **arguments)


def api_show_url(place):
    arguments = {'api_version': conf.settings.API_SHOW_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return utils_urls.url('game:places:api-show', place.id, **arguments)


def refresh_all_places_attributes():
    for place in storage.places.all():
        place.refresh_attributes()
        save_place(place)


def get_available_positions(center_x, center_y, building_position_radius=c.BUILDING_POSITION_RADIUS):  # pylint: disable=R0914
    positions = set()

    for i in range(0, building_position_radius + 1):
        for j in range(0, building_position_radius + 1):
            positions.add((center_x + i, center_y + j))
            positions.add((center_x - i, center_y + j))
            positions.add((center_x + i, center_y - j))
            positions.add((center_x - i, center_y - j))

    positions = set(pos for pos in positions
                    if 0 <= pos[0] < map_conf.settings.WIDTH and 0 <= pos[1] < map_conf.settings.HEIGHT)

    removed_positions = set()

    for place in storage.places.all():
        removed_positions.add((place.x, place.y))

    for building in storage.buildings.all():
        removed_positions.add((building.x, building.y))

    for road in roads_storage.roads.all():
        removed_positions.update(road.get_cells())

    result = positions - removed_positions

    return result if result else get_available_positions(center_x, center_y, building_position_radius=building_position_radius + 1)


def create_building(person, utg_name, position=None):
    building = storage.buildings.get_by_person_id(person.id)

    if building:
        return building

    # remove any destroyed buildings for person
    models.Building.objects.filter(person_id=person.id).delete()

    if position is None:
        position = random.choice(list(get_available_positions(person.place.x, person.place.y)))

    x, y = position

    building = objects.Building(id=None,
                                x=x,
                                y=y,
                                type=person.type.building_type,
                                created_at_turn=game_turn.number(),
                                state=relations.BUILDING_STATE.WORKING,
                                utg_name=utg_name,
                                person_id=person.id)

    save_building(building, new=True)

    return building


def save_building(building, new=False):
    data = {'name': building.utg_name.serialize()}

    arguments = {'x': building.x,
                 'y': building.y,
                 'created_at_turn': building.created_at_turn,
                 'state': building.state,
                 'type': building.type,
                 'place_id': building.place.id,
                 'person_id': building.person.id,
                 'data': s11n.to_json(data)}

    if new:
        building_model = models.Building.objects.create(**arguments)
        building.id = building_model.id
        storage.buildings.add_item(building.id, building)
    else:
        models.Building.objects.filter(id=building.id).update(**arguments)

    storage.buildings.update_version()


def load_building(building_id=None, building_model=None):
    try:
        if building_id is not None:
            building_model = models.Building.objects.get(id=building_id)
        elif building_model is None:
            return None
    except models.Building.DoesNotExist:
        return None

    data = s11n.from_json(building_model.data)

    building = objects.Building(id=building_model.id,
                                x=building_model.x,
                                y=building_model.y,
                                created_at_turn=building_model.created_at_turn,
                                utg_name=utg_words.Word.deserialize(data['name']),
                                type=building_model.type,
                                state=building_model.state,
                                person_id=building_model.person_id)

    return building


def destroy_building(building):
    building.state = relations.BUILDING_STATE.DESTROYED
    save_building(building)

    storage.buildings.update_version()
    storage.buildings.refresh()


def sync_power_economic(places, max_economic):
    if not places:
        return

    places = sorted(places, key=lambda place: politic_power_storage.places.total_power_fraction(place.id))

    values = utils_logic.distribute_values_on_interval(number=len(places), min=1, max=max_economic)

    for place, economic in zip(places, values):
        place.attrs.set_power_economic(economic)


def sync_money_economic(places, max_economic):

    if not places:
        return

    impacts = game_tt_services.money_impacts.cmd_get_targets_impacts(targets=[(tt_api_impacts.OBJECT_TYPE.PLACE, place.id)
                                                                              for place in places])

    places_money = {impact.target_id: impact.amount for impact in impacts}

    places = sorted(places, key=lambda place: places_money.get(place.id, 0))

    values = utils_logic.distribute_values_on_interval(number=len(places), min=1, max=max_economic)

    for place, economic in zip(places, values):
        place.attrs.set_money_economic(economic)


def load_heroes_fame():
    from pathlib import Path

    with (Path(__file__).parent / 'fixtures' / 'heroes_fame.json').open('r') as f:
        data = s11n.from_json(f.read())

    fame = {}

    for hero_id, fames in data.items():
        place_ids = {place_id for place_id, fame in fames}

        for place_id in range(1, 74):
            if place_id in place_ids:
                continue
            if place_id in (54, 56, 57, 69):
                continue
            fames.append((place_id, 0))

        fame[int(hero_id)] = objects.Popularity(dict(fames))

    return fame


_heroes_fame = load_heroes_fame()


# code is changed due to moving the game to the read-only mode
def get_hero_popularity(hero_id):
    if hero_id in _heroes_fame:
        return _heroes_fame[hero_id]

    raise NotImplementedError()


def add_fame(hero_id, fames):
    impacts = []

    for place_id, fame in fames:
        impacts.append(game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                    actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                    actor_id=hero_id,
                                                    target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                    target_id=place_id,
                                                    amount=fame))

    politic_power_logic.add_power_impacts(impacts)


def sync_fame():
    game_tt_services.fame_impacts.cmd_scale_impacts(target_types=[tt_api_impacts.OBJECT_TYPE.PLACE],
                                                    scale=c.PLACE_FAME_REDUCE_FRACTION)


def sync_money():
    game_tt_services.money_impacts.cmd_scale_impacts(target_types=[tt_api_impacts.OBJECT_TYPE.PLACE],
                                                     scale=c.PLACE_MONEY_REDUCE_FRACTION)


def get_start_place_for_race(race):
    choices = [place for place in storage.places.all() if not place.is_frontier]
    choices.sort(key=lambda place: -place.attrs.safety)

    choices = choices[:int(len(choices) * conf.settings.START_PLACE_SAFETY_PERCENTAGE) + 1]

    if not choices:
        choices = list(storage.places.all())

    race_choices = [place for place in choices if place.race == race]

    if race_choices:
        choices = race_choices

    return choices[0]


def choose_place_cell_by_terrain(place_id, terrains, exclude_place_if_can=False, limit=conf.settings.CHOOSE_BY_TERRAIN_LIMIT):
    cell_choices = ()

    if terrains:
        cell_choices = [cell for cell in map_storage.cells.place_cells(place_id)
                        if map_storage.cells(*cell).terrain in terrains]

    if not cell_choices:
        cell_choices = map_storage.cells.place_cells(place_id)

    place = storage.places[place_id]

    if exclude_place_if_can and len(cell_choices) > 1:
        coordinates = (place.x, place.y)

        if coordinates in cell_choices:
            cell_choices.remove(coordinates)

    choices = [(navigation_logic.manhattan_distance(*cell, place.x, place.y), cell)
               for cell in cell_choices]
    choices.sort()

    if limit:
        # фунция используется для выбора клеток для посещения в рамках заданий с механикой «побродить вокруг»
        # ограничивает радиус выбора, чтобы герой не уходил далеко от города (актуально для городов фронтира)
        choices = list(choices[:limit])

    return random.choice(choices)[1]


def register_money_transaction(hero_id, place_id, amount):
    spending = game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.MONEY,
                                                         hero_id=hero_id,
                                                         place_id=place_id,
                                                         amount=amount,
                                                         transaction=uuid.uuid4())
    politic_power_logic.add_power_impacts([spending])


def update_effects():
    effects_to_remove = []
    effects_to_update = []

    for effect in storage.effects.all():

        if not effect.require_updating():
            continue

        if effect.step():
            effects_to_update.append(effect)
        else:
            effects_to_remove.append(effect)

    for effect in effects_to_remove:
        tt_services.effects.cmd_remove(effect.id)

    for effect in effects_to_update:
        tt_services.effects.cmd_update(effect)

    places_storage.effects.update_version()
    places_storage.effects.refresh()


def register_effect(place_id, attribute, value, name, delta=None, info=None, refresh_effects=False, refresh_places=False):
    effect = tt_api_effects.Effect(id=None,
                                   attribute=attribute,
                                   entity=place_id,
                                   value=value,
                                   name=name,
                                   delta=delta,
                                   info=info)

    effect_id = tt_services.effects.cmd_register(effect, unique=attribute.type.is_REWRITABLE)

    if refresh_effects:
        storage.effects.update_version()
        storage.effects.refresh()

    if refresh_places:
        place = places_storage.places[place_id]

        place.refresh_attributes()
        places_logic.save_place(place)

        places_storage.places.update_version()

    return effect_id


def remove_effect(effect_id, place_id, refresh_effects=False, refresh_places=False):
    tt_services.effects.cmd_remove(effect_id)

    if refresh_effects:
        storage.effects.update_version()
        storage.effects.refresh()

    if refresh_places and place_id is not None:
        place = places_storage.places[place_id]

        place.refresh_attributes()
        places_logic.save_place(place)

        places_storage.places.update_version()


def task_board_places(place):
    return storage.places.nearest_places(place.id, number=tt_emissaries_constants.TASK_BOARD_PLACES_NUMBER)


def protector_candidates(place_id):
    clans_ids = set()

    for emissary in emissaries_storage.emissaries.emissaries_in_place(place_id):
        for event in emissaries_storage.events.emissary_events(emissary.id):
            if event.concrete_event.TYPE.is_REVOLUTION:
                clans_ids.add(emissary.clan_id)

    return clans_ids


def protector_candidates_for_ui(place_id):
    candidates = [clans_storage.infos[clan_id] for clan_id in protector_candidates(place_id)]
    candidates.sort(key=lambda info: info.name)

    return candidates


def remove_protectorat(place, refresh_effects=False, refresh_places=False):
    clan_id = place.attrs.clan_protector

    if clan_id is None:
        return

    tt_services.effects.cmd_remove_effects(entity=place.id,
                                           attribute=relations.ATTRIBUTE.CLAN_PROTECTOR)

    clan_info = clans_storage.infos[clan_id]

    template = 'Последний эмиссар гильдии «[clan]» покинул [place|вн]. Гильдия перестала быть протектором города.'
    message = linguistics_logic.technical_render(template,
                                                 {'clan': lexicon_dictionary.text(clan_info.name),
                                                  'place': place.utg_name_form})

    emissaries_logic.notify_clans(place_id=place.id,
                                  exclude_clans_ids=(),
                                  message=message,
                                  roles=clans_relations.ROLES_TO_NOTIFY)

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[clan_id],
                                              event=clans_relations.EVENT.PROTECTORAT_LOST,
                                              tags=[place.meta_object().tag],
                                                    message=f'Потерян протекторат над городом «{place.name}»')

    if refresh_effects:
        storage.effects.update_version()
        storage.effects.refresh()

    if refresh_places and place.id is not None:
        place = places_storage.places[place.id]

        place.refresh_attributes()
        places_logic.save_place(place)

        places_storage.places.update_version()


def sync_protectorat(place):
    clan_id = place.attrs.clan_protector

    if clan_id is None:
        return

    emissaries_in_place = emissaries_storage.emissaries.emissaries_in_place(place.id)

    if clan_id in {emissary.clan_id for emissary in emissaries_in_place}:
        return

    remove_protectorat(place,
                       refresh_effects=True,
                       refresh_places=True)


def monitor_protectorates():
    for place in storage.places.all():
        sync_protectorat(place)
