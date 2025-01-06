
import smart_imports

smart_imports.all()


def calculate_power_fractions(all_powers):
    # находим минимальное отрицательное влияние и компенсируем его при расчёте долей
    minimum_power = 0.0

    for power in all_powers.values():
        minimum_power = min(minimum_power, power)

    total_power = 0.0

    for power in all_powers.values():
        total_power += (power - minimum_power)

    if total_power == 0:
        return {power_id: 1.0 / len(all_powers)
                for power_id, current_power in all_powers.items()}

    return {power_id: ((current_power - minimum_power) / total_power)
            for power_id, current_power in all_powers.items()}


def sync_power():
    game_tt_services.personal_impacts.cmd_scale_impacts(target_types=[tt_api_impacts.OBJECT_TYPE.PERSON,
                                                                      tt_api_impacts.OBJECT_TYPE.PLACE],
                                                        scale=tt_politic_power_constants.POWER_REDUCE_FRACTION)

    game_tt_services.crowd_impacts.cmd_scale_impacts(target_types=[tt_api_impacts.OBJECT_TYPE.PERSON,
                                                                   tt_api_impacts.OBJECT_TYPE.PLACE],
                                                     scale=tt_politic_power_constants.POWER_REDUCE_FRACTION)
    storage.places.reset()
    storage.persons.reset()


def get_inner_circle(place_id=None, person_id=None):
    if place_id is not None:
        target = (tt_api_impacts.OBJECT_TYPE.PLACE, place_id)
        size = conf.settings.PLACE_INNER_CIRCLE_SIZE
    elif person_id is not None:
        target = (tt_api_impacts.OBJECT_TYPE.PERSON, person_id)
        size = conf.settings.PERSON_INNER_CIRCLE_SIZE
    else:
        raise NotImplementedError

    ratings = game_tt_services.personal_impacts.cmd_get_impacters_ratings(targets=[target],
                                                                          actor_types=[tt_api_impacts.OBJECT_TYPE.HERO],
                                                                          limit=10**6)
    return objects.InnerCircle(rating=[(impact.actor_id, impact.amount)
                                       for impact in ratings[target]
                                       if 1 <= abs(impact.amount)],
                               size=size)


def load_job_powers():
    from pathlib import Path

    with (Path(__file__).parent / 'fixtures' / 'job_powers.json').open('r') as f:
        data = s11n.from_json(f.read())

    return {int(key): jobs_objects.JobPower(positive=value['p'], negative=value['n']) for key, value in data.items()}


_job_powers = load_job_powers()


# code is changed due to moving game to the read-only mode
def get_job_power(person_id=None):
    return _job_powers[person_id]


def load_emissaries_power():
    from pathlib import Path

    with (Path(__file__).parent / 'fixtures' / 'emissaries_power.json').open('r') as f:
        data = s11n.from_json(f.read())

    return {int(key): value for key, value in data.items()}


_emissaries_power = load_emissaries_power()


# code is changed due to moving game to the read-only mode
def get_emissaries_power(emissaries_ids):
    return {emissary_id: _emissaries_power.get(emissary_id, 0) for emissary_id in emissaries_ids}


def add_power_impacts(impacts):
    transaction = uuid.uuid4()
    current_turn = game_turn.number()

    inner_circle = []
    outer_circle = []
    jobs = []
    fame = []
    money = []
    emissary_power = []

    for impact in impacts:
        impact.transaction = transaction
        impact.turn = current_turn

        if impact.type.is_INNER_CIRCLE:
            inner_circle.append(impact)
        elif impact.type.is_OUTER_CIRCLE:
            outer_circle.append(impact)
        elif impact.type.is_JOB:
            jobs.append(impact)
        elif impact.type.is_FAME:
            fame.append(impact)
        elif impact.type.is_MONEY:
            money.append(impact)
        elif impact.type.is_EMISSARY_POWER:
            emissary_power.append(impact)
        else:
            raise NotImplementedError

    if inner_circle:
        game_tt_services.personal_impacts.cmd_add_power_impacts(inner_circle)

    if outer_circle:
        game_tt_services.crowd_impacts.cmd_add_power_impacts(outer_circle)

    if jobs:
        game_tt_services.job_impacts.cmd_add_power_impacts(jobs)

    if fame:
        game_tt_services.fame_impacts.cmd_add_power_impacts(fame)

    if money:
        game_tt_services.money_impacts.cmd_add_power_impacts(money)

    if emissary_power:
        game_tt_services.emissary_impacts.cmd_add_power_impacts(emissary_power)


def get_last_power_impacts(limit,
                           storages=(game_tt_services.personal_impacts,
                                     game_tt_services.crowd_impacts),
                           actors=((None, None),),
                           target_type=None,
                           target_id=None):
    impacts = []

    for storage in storages:
        for actor_type, actor_id in actors:
            impacts.extend(storage.cmd_get_last_power_impacts(limit,
                                                              actor_type=actor_type,
                                                              actor_id=actor_id,
                                                              target_type=target_type,
                                                              target_id=target_id))

    impacts.sort(key=lambda impact: (impact.turn, impact.time), reverse=True)

    return impacts[:limit]


def final_politic_power(power: int, place=None, person=None, hero=None, bonus: float=0.0) -> int:
    multiplier = 1.0 + bonus

    if place:
        multiplier += place.attrs.politic_power_bonus

    if person:
        multiplier += person.attrs.politic_power_bonus

    if hero:
        multiplier += hero.politic_power_bonus()

    multiplier = max(0, multiplier)

    return int(math.ceil(power * multiplier))
