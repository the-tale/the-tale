
import smart_imports

smart_imports.all()


EffectsContainer = game_effects.create_container(relations.ATTRIBUTE)


class PlaceJob(jobs_objects.Job):
    ACTOR = 'place'

    ACTOR_TYPE = tt_api_impacts.OBJECT_TYPE.PLACE
    POSITIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE
    NEGATIVE_TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE

    # умножаем на 2, так как кажая остановка в городе, по сути, даёт влияние в 2-кратном размере
    # Город получит влияние и от задания, которое герой выполнил и от того, которое возьмёт
    NORMAL_POWER = f.normal_job_power(politic_power_conf.settings.PLACE_INNER_CIRCLE_SIZE) * 2

    def load_power(self, actor_id):
        return politic_power_logic.get_job_power(place_id=actor_id)

    def load_inner_circle(self, actor_id):
        return politic_power_logic.get_inner_circle(place_id=actor_id)

    def get_job_power(self, actor_id):
        current_place = storage.places[actor_id]

        return jobs_logic.job_power(power=politic_power_storage.places.total_power_fraction(current_place.id),
                                    powers=[politic_power_storage.places.total_power_fraction(place.id)
                                            for place in current_place.get_same_places()])

    def get_project_name(self, actor_id):
        name = storage.places[actor_id].utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))
        return 'Проект города {name}'.format(name=name)

    def get_objects(self, actor_id):
        return {'person': None,
                'place': storage.places[actor_id]}

    def get_effects_priorities(self, actor_id):
        return {effect: 1 for effect in jobs_effects.EFFECT.records}


def tt_power_impacts(inner_circle, actor_type, actor_id, place, amount, fame):
    amount = round(amount * place.attrs.freedom)

    impact_type = game_tt_services.IMPACT_TYPE.OUTER_CIRCLE

    if inner_circle:
        impact_type = game_tt_services.IMPACT_TYPE.INNER_CIRCLE

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

    target_type = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE

    if amount < 0:
        target_type = tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE

    yield game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                       actor_type=actor_type,
                                       actor_id=actor_id,
                                       target_type=target_type,
                                       target_id=place.id,
                                       amount=abs(amount))


def impacts_from_hero(hero, place, power, impacts_generator=tt_power_impacts):
    place_power = 0

    can_change_power = hero.can_change_place_power(place)

    place_power = hero.modify_politics_power(power, place=place)

    yield from impacts_generator(inner_circle=hero.preferences.has_place_in_preferences(place),
                                 actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                 actor_id=hero.id,
                                 place=place,
                                 amount=place_power if can_change_power else 0,
                                 fame=c.HERO_FAME_PER_HELP if 0 < place_power else 0)


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
                          effects=EffectsContainer.deserialize(data.get('effects')),
                          job=PlaceJob.deserialize(data['job']),
                          modifier=place_model.modifier)

    place.attrs.sync()

    return place


def save_place(place, new=False):
    data = {'name': place.utg_name.serialize(),
            'attributes': place.attrs.serialize(),
            'races': place.races.serialize(),
            'effects': place.effects.serialize(),
            'job': place.job.serialize()}

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
                          effects=EffectsContainer(),
                          job=jobs_logic.create_job(PlaceJob),
                          modifier=modifiers.CITY_MODIFIERS.NONE)
    # place.refresh_attributes()
    save_place(place, new=True)
    return place


def api_list_url():
    arguments = {'api_version': conf.settings.API_LIST_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return dext_urls.url('game:places:api-list', **arguments)


def api_show_url(place):
    arguments = {'api_version': conf.settings.API_SHOW_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return dext_urls.url('game:places:api-show', place.id, **arguments)


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


def get_hero_popularity(hero_id):
    impacts = game_tt_services.fame_impacts.cmd_get_actor_impacts(actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                  actor_id=hero_id,
                                                                  target_types=[tt_api_impacts.OBJECT_TYPE.PLACE])

    return objects.Popularity({impact.target_id: impact.amount for impact in impacts})


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

    if any(place.race == race for place in choices):
        choices = [place for place in choices if place.race == race]

    return choices[0]


def choose_place_cell_by_terrain(place_id, terrains, exclude_place_if_can=False):
    cell_choices = ()

    if terrains:
        cell_choices = [cell for cell in map_storage.cells.place_cells(place_id)
                        if map_storage.cells(*cell).terrain in terrains]

    if not cell_choices:
        cell_choices = map_storage.cells.place_cells(place_id)

    if exclude_place_if_can and len(cell_choices) > 1:
        place = storage.places[place_id]
        coordinates = (place.x, place.y)

        if coordinates in cell_choices:
            cell_choices.remove(coordinates)

    return random.choice(cell_choices)


def register_money_transaction(hero_id, place_id, amount):
    spending = game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.MONEY,
                                                         hero_id=hero_id,
                                                         place_id=place_id,
                                                         amount=amount,
                                                         transaction=uuid.uuid4())
    politic_power_logic.add_power_impacts([spending])


def update_stability_effects_deltas(renewing_speed, stability_effects):
    if not stability_effects:
        return

    # getattr used for processing of old effects, can be removed after 0.3.30
    stability_effects.sort(key=lambda effect: getattr(effect, 'id', 0))

    divider = 2
    speed_sum = 0

    for effect in stability_effects:
        delta = 0

        if divider < 1000:
            delta = renewing_speed / divider

        effect.delta = delta
        speed_sum += delta

        divider *= 2

    stability_effects[0].delta += (renewing_speed - speed_sum)


def update_effects():
    effects = list(storage.effects.all())

    for place in storage.places.all():
        stability_effects = [effect for effect in effects
                             if effect.attribute.is_STABILITY and
                                effect.entity == place.id]

        update_stability_effects_deltas(place.attrs.stability_renewing_speed, stability_effects)

    effects_to_remove = []
    effects_to_update = []

    for effect in effects:

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

    effect_id = tt_services.effects.cmd_register(effect)

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


def task_board_places(x, y):
    return storage.places.nearest_places(x, y, radius=tt_emissaries_constants.TASK_BOARD_RADIUS)
