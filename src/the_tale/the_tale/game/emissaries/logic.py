
import smart_imports

smart_imports.all()


def save_emissary(emissary, new=False):

    data = {'name': emissary.utg_name.serialize(),
            'created_at_turn': emissary.created_at_turn,
            'updated_at_turn': emissary.updated_at_turn,
            'moved_at_turn': emissary.moved_at_turn,
            'moved_at': time.mktime(emissary.moved_at.timetuple()),
            'remove_reason': emissary.remove_reason.value,
            'gender': emissary.gender.value,
            'race': emissary.race.value,
            'health': emissary.health}

    arguments = {'place_id': emissary.place_id,
                 'clan_id': emissary.clan_id,
                 'data': s11n.to_json(data),
                 'state': emissary.state,
                 'updated_at': datetime.datetime.now()}

    if new:
        emissary_model = models.Emissary.objects.create(**arguments)

        emissary.id = emissary_model.id
        emissary.created_at = emissary_model.created_at
        emissary.updated_at = emissary_model.updated_at

        storage.emissaries.add_item(emissary.id, emissary)
    else:
        models.Emissary.objects.filter(id=emissary.id).update(**arguments)

    storage.emissaries.update_version()

    if not emissary.state.is_IN_GAME:
        storage.emissaries.refresh()


def create_emissary(initiator, clan, place_id, gender, race, utg_name):

    emissary = objects.Emissary(id=None,
                                created_at=None,
                                updated_at=None,
                                moved_at=datetime.datetime.now().replace(microsecond=0),
                                created_at_turn=game_turn.number(),
                                updated_at_turn=game_turn.number(),
                                moved_at_turn=game_turn.number(),
                                clan_id=clan.id,
                                place_id=place_id,
                                gender=gender,
                                race=race,
                                utg_name=utg_name,
                                state=relations.STATE.IN_GAME,
                                remove_reason=relations.REMOVE_REASON.NOT_REMOVED,
                                health=None)

    emissary.health = emissary.max_health

    save_emissary(emissary, new=True)

    message = 'Хранитель {keeper} нанял эмиссара {emissary} в город {place}'.format(keeper=initiator.nick_verbose,
                                                                                    emissary=emissary.utg_name.forms[3],
                                                                                    place=places_storage.places[place_id].utg_name.forms[3])

    clans_tt_services.chronicle.cmd_add_event(clan=clan,
                                              event=clans_relations.EVENT.EMISSARY_CREATED,
                                              tags=[initiator.meta_object().tag,
                                                    emissary.meta_object().tag],
                                              message=message)

    politic_power_logic.add_power_impacts([game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                        actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                        actor_id=initiator.id,
                                                                        target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                        target_id=emissary.id,
                                                                        amount=tt_clans_constants.INITIAL_EMISSARY_POWER)])

    return emissary


def load_emissary(emissary_id=None, emissary_model=None):
    try:
        if emissary_id is not None:
            emissary_model = models.Emissary.objects.get(id=emissary_id)
        elif emissary_model is None:
            return None
    except models.Emissary.DoesNotExist:
        return None

    data = s11n.from_json(emissary_model.data)

    return objects.Emissary(id=emissary_model.id,
                            created_at_turn=data['created_at_turn'],
                            updated_at_turn=data['updated_at_turn'],
                            moved_at_turn=data['moved_at_turn'],
                            state=emissary_model.state,
                            remove_reason=relations.REMOVE_REASON(data['remove_reason']),
                            clan_id=emissary_model.clan_id,
                            place_id=emissary_model.place_id,
                            gender=game_relations.GENDER(data['gender']),
                            race=game_relations.RACE(data['race']),
                            utg_name=utg_words.Word.deserialize(data['name']),
                            created_at=emissary_model.created_at,
                            updated_at=emissary_model.updated_at,
                            moved_at=datetime.datetime.fromtimestamp(data['moved_at']),
                            health=data.get('health', tt_clans_constants.MAXIMUM_EMISSARY_HEALTH))


def load_emissaries_for_clan(clan_id):
    emissaries_models = models.Emissary.objects.all().filter(clan_id=clan_id)

    return [load_emissary(emissary_model=model) for model in emissaries_models]


def load_emissaries_for_place(place_id):
    emissaries_models = models.Emissary.objects.all().filter(place_id=place_id)

    return [load_emissary(emissary_model=model) for model in emissaries_models]


def _remove_emissary(emissary_id, reason):

    with django_transaction.atomic():

        if not models.Emissary.objects.select_for_update().filter(id=emissary_id,
                                                                  state=relations.STATE.IN_GAME).exists():
            return

        emissary = storage.emissaries[emissary_id]

        emissary.state = relations.STATE.OUT_GAME
        emissary.remove_reason = reason
        emissary.updated_at_turn = game_turn.number()

        save_emissary(emissary)


def dismiss_emissary(initiator, emissary_id):
    _remove_emissary(emissary_id, reason=relations.REMOVE_REASON.DISMISSED)

    emissary = load_emissary(emissary_id)

    message = 'Хранитель {keeper} уволил эмиссара {emissary}'.format(keeper=initiator.nick_verbose,
                                                                     emissary=emissary.utg_name.forms[3])

    clans_tt_services.chronicle.cmd_add_event(clan=clans_logic.load_clan(emissary.clan_id),
                                              event=clans_relations.EVENT.EMISSARY_DISSMISSED,
                                              tags=[emissary.meta_object().tag,
                                                    initiator.meta_object().tag],
                                              message=message)


def kill_emissary(emissary_id):
    _remove_emissary(emissary_id, reason=relations.REMOVE_REASON.KILLED)

    emissary = load_emissary(emissary_id)

    message = 'Эмиссар {emissary} был убит'.format(emissary=emissary.name)

    clans_tt_services.chronicle.cmd_add_event(clan=clans_logic.load_clan(emissary.clan_id),
                                              event=clans_relations.EVENT.EMISSARY_KILLED,
                                              tags=[emissary.meta_object().tag],
                                              message=message)


def damage_emissary(emissary_id):

    with django_transaction.atomic():

        if not models.Emissary.objects.select_for_update().filter(id=emissary_id,
                                                                  state=relations.STATE.IN_GAME).exists():
            return

        emissary = storage.emissaries[emissary_id]

        emissary.health = max(0, emissary.health - 1)
        emissary.updated_at_turn = game_turn.number()

        save_emissary(emissary)

    message = 'На эмиссара {emissary} совершено покушение.'.format(emissary=emissary.utg_name.forms[3])

    clans_tt_services.chronicle.cmd_add_event(clan=clans_logic.load_clan(emissary.clan_id),
                                              event=clans_relations.EVENT.EMISSARY_DAMAGED,
                                              tags=[emissary.meta_object().tag],
                                              message=message)


def damage_emissaries():
    powers = politic_power_logic.get_emissaries_power([emissary.id for emissary in storage.emissaries.all()])

    for emissary_id, power in powers.items():
        if power > 0:
            continue

        damage_emissary(emissary_id)


def kill_dead_emissaries():
    for emissary in storage.emissaries.all():
        if emissary.health <= 0:
            kill_emissary(emissary.id)


def move_emissary(initiator, emissary_id, new_place_id):

    with django_transaction.atomic():

        if not models.Emissary.objects.select_for_update().filter(id=emissary_id,
                                                                  state=relations.STATE.IN_GAME).exclude(place_id=new_place_id).exists():
            return

        emissary = load_emissary(emissary_id)

        old_place = emissary.place

        emissary.place_id = new_place_id
        emissary.moved_at_turn = game_turn.number()
        emissary.moved_at = datetime.datetime.now()
        emissary.updated_at_turn = game_turn.number()

        save_emissary(emissary)

    new_place = places_storage.places[new_place_id]

    message = 'Хранитель {keeper} переместил эмиссара {emissary} из города «{old_place}» в город «{new_place}»'
    message = message.format(keeper=initiator.nick_verbose,
                             emissary=emissary.utg_name.forms[3],
                             old_place=old_place.name,
                             new_place=new_place.name)

    clans_tt_services.chronicle.cmd_add_event(clan=clans_logic.load_clan(emissary.clan_id),
                                              event=clans_relations.EVENT.EMISSARY_MOVED,
                                              tags=[emissary.meta_object().tag,
                                                    initiator.meta_object().tag,
                                                    old_place.meta_object().tag,
                                                    new_place.meta_object().tag],
                                              message=message)


def tt_power_impacts(place_inner_circle, can_change_place_power, actor_type, actor_id, emissary, amount, fame):

    # this power, only to emissary
    if emissary.state.is_IN_GAME:
        emissary_power = round(amount * emissary.place.attrs.freedom)

        yield game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                           actor_type=actor_type,
                                           actor_id=actor_id,
                                           target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                           target_id=emissary.id,
                                           amount=emissary_power)

    yield from places_logic.tt_power_impacts(inner_circle=place_inner_circle,
                                             actor_type=actor_type,
                                             actor_id=actor_id,
                                             place=emissary.place,
                                             amount=amount if can_change_place_power else 0,
                                             fame=fame)


def impacts_from_hero(hero, emissary, power, impacts_generator=tt_power_impacts):

    emissary_power = hero.modify_politics_power(power, emissary=emissary)

    has_place_in_preferences = hero.preferences.has_place_in_preferences(emissary.place)

    can_change_power = hero.can_change_place_power(emissary.place)

    yield from impacts_generator(place_inner_circle=has_place_in_preferences,
                                 can_change_place_power=can_change_power,
                                 actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                 actor_id=hero.id,
                                 emissary=emissary,
                                 amount=emissary_power,
                                 fame=c.HERO_FAME_PER_HELP if 0 < power else 0)


def form_choices(empty_choice=True):
    choices = []

    if empty_choice:
        choices.append(('', '----'))

    clans = clans_logic.load_clans(clans_ids=list(storage.emissaries.emissaries_by_clan.keys()))
    clans = [clan for clan in clans if clan.state.is_ACTIVE]

    clans = {clan.id: clan for clan in clans}

    for clan_id, emissaries in storage.emissaries.emissaries_by_clan.items():
        clan = clans[clan_id]

        clan_choices = [(emissary.id, emissary.name) for emissary in emissaries]

        clan_choices.sort(key=lambda choice: choice[1])

        choices.append(('[{}] {}'.format(clan.abbr, clan.name), clan_choices))

    return sorted(choices, key=lambda choice: choice[0])


def sync_power():
    game_tt_services.emissary_impacts.cmd_scale_impacts(target_types=[tt_api_impacts.OBJECT_TYPE.EMISSARY],
                                                        scale=tt_clans_constants.EMISSARY_POWER_REDUCE_FRACTION)
