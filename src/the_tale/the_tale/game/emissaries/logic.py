
import smart_imports

smart_imports.all()


def save_emissary(emissary, new=False):

    data = {'name': emissary.utg_name.serialize(),
            'created_at_turn': emissary.created_at_turn,
            'updated_at_turn': game_turn.number(),
            'moved_at_turn': emissary.moved_at_turn,
            'moved_at': time.mktime(emissary.moved_at.timetuple()),
            'remove_reason': emissary.remove_reason.value,
            'gender': emissary.gender.value,
            'race': emissary.race.value,
            'health': emissary.health,
            'attributes': emissary.attrs.serialize(),
            'traits': [trait.value for trait in emissary.traits],
            'abilities': emissary.abilities.serialize(),
            'place_rating_position': emissary.place_rating_position}

    arguments = {'place_id': emissary.place_id,
                 'clan_id': emissary.clan_id,
                 'data': data,
                 'state': emissary.state,
                 'updated_at': datetime.datetime.now()}

    if new:
        emissary_model = models.Emissary.objects.create(**arguments)

        emissary.id = emissary_model.id

        emissary.created_at = emissary_model.created_at
        emissary.updated_at = emissary_model.updated_at
        emissary.created_at_turn = data['created_at_turn']
        emissary.updated_at_turn = data['updated_at_turn']

        storage.emissaries.add_item(emissary.id, emissary)
    else:
        models.Emissary.objects.filter(id=emissary.id).update(**arguments)

        emissary.updated_at = arguments['updated_at']
        emissary.updated_at_turn = data['updated_at_turn']

    storage.emissaries.update_version()

    if not emissary.state.is_IN_GAME:
        storage.emissaries.remove_item(emissary.id)


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
                                health=None,
                                attrs=attributes.Attributes(),
                                traits=generate_traits(),
                                abilities=abilities.Abilities(),
                                place_rating_position=None)

    emissary.refresh_attributes()

    emissary.health = emissary.attrs.max_health

    save_emissary(emissary, new=True)

    message = 'Хранитель {keeper} нанял эмиссара {emissary} в город {place}'.format(keeper=initiator.nick_verbose,
                                                                                    emissary=emissary.utg_name.forms[3],
                                                                                    place=places_storage.places[place_id].utg_name.forms[3])

    clans_tt_services.chronicle.cmd_add_event(clan=clan,
                                              event=clans_relations.EVENT.EMISSARY_CREATED,
                                              tags=[initiator.meta_object().tag,
                                                    emissary.meta_object().tag,
                                                    emissary.place.meta_object().tag],
                                              message=message)

    politic_power_logic.add_power_impacts([game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                        actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                        actor_id=initiator.id,
                                                                        target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                        target_id=emissary.id,
                                                                        amount=expected_power_per_day())])

    return emissary


def load_emissary(emissary_id=None, emissary_model=None):
    try:
        if emissary_id is not None:
            emissary_model = models.Emissary.objects.get(id=emissary_id)
        elif emissary_model is None:
            return None
    except models.Emissary.DoesNotExist:
        return None

    data = emissary_model.data

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
                            health=data['health'],
                            attrs=attributes.Attributes.deserialize(data['attributes']),
                            traits=frozenset(relations.TRAIT(trait_id) for trait_id in data['traits']),
                            abilities=abilities.Abilities.deserialize(data['abilities']),
                            place_rating_position=data.get('place_rating_position'))


def load_emissaries_for_clan(clan_id):
    emissaries_ids = models.Emissary.objects.all().filter(clan_id=clan_id).values_list('id', flat=True)

    return [storage.emissaries.get_or_load(emissary_id) for emissary_id in emissaries_ids]


def count_active_emissaries_for_clan(clan_id):
    return models.Emissary.objects.all().filter(clan_id=clan_id,
                                                state=relations.STATE.IN_GAME).count()


def load_emissaries_for_place(place_id):
    emissaries_ids = models.Emissary.objects.all().filter(place_id=place_id).values_list('id', flat=True)

    return [storage.emissaries.get_or_load(emissary_id) for emissary_id in emissaries_ids]


def lock_emissary_for_update(emissary_id):
    return models.Emissary.objects.select_for_update().filter(id=emissary_id,
                                                              state=relations.STATE.IN_GAME).exists()


def _remove_emissary(emissary_id, reason):

    with django_transaction.atomic():

        if not lock_emissary_for_update(emissary_id):
            return

        for event in storage.events.emissary_events(emissary_id):
            stop_event_due_emissary_left_game(event)

        emissary = storage.emissaries[emissary_id]

        emissary.state = relations.STATE.OUT_GAME
        emissary.remove_reason = reason

        save_emissary(emissary)


def dismiss_emissary(emissary_id):
    _remove_emissary(emissary_id, reason=relations.REMOVE_REASON.DISMISSED)

    emissary = storage.emissaries.get_or_load(emissary_id)

    message = linguistics_logic.technical_render('Эмиссар [emissary] [покинул|emissary] гильдию',
                                                 {'emissary': emissary.utg_name_form})

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[emissary.clan_id],
                                              event=clans_relations.EVENT.EMISSARY_DISSMISSED,
                                              tags=[emissary.meta_object().tag,
                                                    emissary.place.meta_object().tag],
                                              message=message)


def kill_emissary(emissary_id):
    _remove_emissary(emissary_id, reason=relations.REMOVE_REASON.KILLED)

    emissary = storage.emissaries.get_or_load(emissary_id)

    message = linguistics_logic.technical_render('Эмиссар [emissary] [убит|emissary]',
                                                 {'emissary': emissary.utg_name_form})

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[emissary.clan_id],
                                              event=clans_relations.EVENT.EMISSARY_KILLED,
                                              tags=[emissary.meta_object().tag],
                                              message=message)


def damage_emissary(emissary_id):

    with django_transaction.atomic():

        if not models.Emissary.objects.select_for_update().filter(id=emissary_id,
                                                                  state=relations.STATE.IN_GAME).exists():
            return

        emissary = storage.emissaries[emissary_id]

        emissary.health = max(0, emissary.health - emissary.attrs.damage_to_health)

        save_emissary(emissary)

    message = linguistics_logic.technical_render('На эмиссара [emissary|вн] совершено покушение',
                                                 {'emissary': emissary.utg_name_form})

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[emissary.clan_id],
                                              event=clans_relations.EVENT.EMISSARY_DAMAGED,
                                              tags=[emissary.meta_object().tag],
                                              message=message)


def damage_emissaries():
    powers = politic_power_logic.get_emissaries_power([emissary.id for emissary in storage.emissaries.all()])

    for emissary_id, power in powers.items():
        if power > 0:
            continue

        damage_emissary(emissary_id)


def refresh_emissaries_attributes():
    for emissary in storage.emissaries.all():
        emissary.refresh_attributes()

    storage.emissaries.save_all()


def kill_dead_emissaries():
    for emissary in storage.emissaries.all():
        if emissary.health <= 0:
            kill_emissary(emissary.id)


def move_emissary(emissary_id, new_place_id):

    with django_transaction.atomic():

        if not lock_emissary_for_update(emissary_id):
            return

        emissary = storage.emissaries[emissary_id]

        if emissary.place_id == new_place_id:
            return

        # reset power
        current_power = politic_power_logic.get_emissaries_power(emissaries_ids=[emissary.id])[emissary.id]

        impact = game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                              actor_type=tt_api_impacts.OBJECT_TYPE.ACCOUNT,
                                              actor_id=accounts_logic.get_system_user_id(),
                                              target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                              target_id=emissary.id,
                                              amount=-current_power + expected_power_per_day())

        politic_power_logic.add_power_impacts([impact])

        # modify emissary
        old_place = emissary.place

        emissary.place_id = new_place_id
        emissary.place_rating_position = None
        emissary.moved_at_turn = game_turn.number()
        emissary.moved_at = datetime.datetime.now()

        save_emissary(emissary)

    new_place = places_storage.places[new_place_id]

    message = linguistics_logic.technical_render('Эмиссар [emissary] [переехал|emissary] из города [old_place] в город [new_place]',
                                                 {'emissary': emissary.utg_name_form,
                                                  'old_place': old_place.utg_name_form,
                                                  'new_place': new_place.utg_name_form})

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[emissary.clan_id],
                                              event=clans_relations.EVENT.EMISSARY_MOVED,
                                              tags=[emissary.meta_object().tag,
                                                    old_place.meta_object().tag,
                                                    new_place.meta_object().tag],
                                              message=message)


def rename_emissary(emissary_id, new_name):

    with django_transaction.atomic():

        if not lock_emissary_for_update(emissary_id):
            return

        emissary = storage.emissaries[emissary_id]

        game_names.sync_properties(new_name, emissary.gender)

        old_name = emissary.utg_name

        emissary.utg_name = new_name

        save_emissary(emissary)

    message = linguistics_logic.technical_render('Эмиссар [old_name] [изменил|old_name] имя на [new_name|вн]',
                                                 {'old_name': utg_words.WordForm(old_name),
                                                  'new_name': utg_words.WordForm(new_name)})

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[emissary.clan_id],
                                              event=clans_relations.EVENT.EMISSARY_RENAMED,
                                              tags=[emissary.meta_object().tag,
                                                    emissary.place.meta_object().tag],
                                              message=message)


def tt_power_impacts(place_inner_circle, can_change_place_power, actor_type, actor_id, emissary, amount: int, fame: int):

    if emissary.state.is_IN_GAME:
        yield game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                           actor_type=actor_type,
                                           actor_id=actor_id,
                                           target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                           target_id=emissary.id,
                                           amount=amount)

    yield from places_logic.tt_power_impacts(inner_circle=place_inner_circle,
                                             actor_type=actor_type,
                                             actor_id=actor_id,
                                             place=emissary.place,
                                             amount=amount if can_change_place_power else 0,
                                             fame=fame)


def impacts_from_hero(hero, emissary, power, impacts_generator=tt_power_impacts):

    if 0 < power:
        bonus = emissary.attrs.positive_power
    elif power < 0:
        bonus = emissary.attrs.negative_power
    else:
        bonus = 0

    emissary_power = politic_power_logic.final_politic_power(power=power,
                                                             place=emissary.place,
                                                             hero=hero,
                                                             bonus=bonus)

    yield from impacts_generator(place_inner_circle=hero.preferences.place_is_hometown(emissary.place),
                                 can_change_place_power=hero.can_change_place_power(emissary.place),
                                 actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                 actor_id=hero.id,
                                 emissary=emissary,
                                 amount=emissary_power,
                                 fame=c.HERO_FAME_PER_HELP if 0 < power else 0)


def form_choices(empty_choice=True, own_clan_id=None):
    choices = []

    if empty_choice:
        choices.append(('', '----'))

    own_clan_name = None

    for clan_id, emissaries in storage.emissaries.emissaries_by_clan.items():

        if clan_id not in clans_storage.infos:
            continue

        clan = clans_storage.infos[clan_id]

        clan_choices = [(emissary.id, f'{emissary.name} из {emissary.place.utg_name.forms[1]}')
                        for emissary in emissaries]

        clan_choices.sort(key=lambda choice: choice[1])

        clan_name = f'[{clan.abbr}] {clan.name}'

        if clan_id == own_clan_id:
            own_clan_name = clan_name

        choices.append((clan_name, clan_choices))

    choices.sort(key=lambda choice: (choice[0] != '', choice[0] != own_clan_name, choice[0]))

    return choices


def sync_power():
    game_tt_services.emissary_impacts.cmd_scale_impacts(target_types=[tt_api_impacts.OBJECT_TYPE.EMISSARY],
                                                        scale=tt_emissaries_constants.EMISSARY_POWER_REDUCE_FRACTION)


def _choose_trait(excluded_traits, type):
    allowed_traits = [trait for trait in relations.TRAIT.records
                      if trait not in excluded_traits and trait.type == type]

    choosen_trait = random.choice(allowed_traits)

    excluded_traits.add(choosen_trait)
    excluded_traits.update(trait for trait in relations.TRAIT.records
                           if choosen_trait.attribute == trait.attribute)

    return choosen_trait


def generate_traits():
    excluded_traits = set()

    traits = set()

    for _ in range(tt_emissaries_constants.POSITIVE_TRAITS_NUMBER):
        traits.add(_choose_trait(excluded_traits, relations.TRAIT_TYPE.POSITIVE))

    for _ in range(tt_emissaries_constants.NEGATIVE_TRAITS_NUMBER):
        traits.add(_choose_trait(excluded_traits, relations.TRAIT_TYPE.NEGATIVE))

    return frozenset(traits)


def save_event(event, new=False):

    data = {'created_at_turn': event.created_at_turn,
            'updated_at_turn': game_turn.number(),
            'steps_processed': event.steps_processed,
            'stop_after_steps': event.stop_after_steps,
            'event': event.concrete_event.serialize()}

    arguments = {'emissary_id': event.emissary_id,
                 'data': data,
                 'state': event.state,
                 'updated_at': datetime.datetime.now(),
                 'stop_reason': event.stop_reason.value}

    if new:
        event_model = models.Event.objects.create(**arguments)

        event.id = event_model.id
        event.created_at = event_model.created_at
        event.updated_at = event_model.updated_at
        event.created_at_turn = data['updated_at_turn']
        event.updated_at_turn = data['updated_at_turn']

        storage.events.add_item(event.id, event)
    else:
        models.Event.objects.filter(id=event.id).update(**arguments)

        event.updated_at = arguments['updated_at']
        event.updated_at_turn = data['updated_at_turn']

    storage.events.update_version()

    if not event.state.is_RUNNING:
        storage.events.remove_item(event.id)


def create_event(initiator, emissary, concrete_event, days):

    event = objects.Event(id=None,
                          created_at=None,
                          updated_at=None,
                          steps_processed=0,
                          created_at_turn=game_turn.number(),
                          updated_at_turn=game_turn.number(),
                          emissary_id=emissary.id,
                          state=relations.EVENT_STATE.RUNNING,
                          stop_reason=relations.EVENT_STOP_REASON.NOT_STOPPED,
                          concrete_event=concrete_event,
                          stop_after_steps=days * 24)

    save_event(event, new=True)

    message = 'Эмиссар [emissary] [начал|emissary] мероприятие «[event]» в городе [place|пр] по команде хранителя [keeper]'
    message = linguistics_logic.technical_render(message,
                                                 {'emissary': emissary.utg_name_form,
                                                  'event': lexicon_dictionary.text(concrete_event.TYPE.text),
                                                  'place': places_storage.places[emissary.place_id].utg_name_form,
                                                  'keeper': lexicon_dictionary.text(initiator.nick_verbose)})

    clan = clans_logic.load_clan(emissary.clan_id)

    clans_tt_services.chronicle.cmd_add_event(clan=clan,
                                              event=clans_relations.EVENT.EMISSARY_EVENT_CREATED,
                                              tags=[initiator.meta_object().tag,
                                                    emissary.meta_object().tag,
                                                    emissary.place.meta_object().tag,
                                                    concrete_event.TYPE.meta_object().tag],
                                              message=message)

    return event


def load_event(event_id=None, event_model=None):
    try:
        if event_id is not None:
            event_model = models.Event.objects.get(id=event_id)
        elif event_model is None:
            return None
    except models.Event.DoesNotExist:
        return None

    data = event_model.data

    return objects.Event(id=event_model.id,
                         created_at_turn=data['created_at_turn'],
                         updated_at_turn=data['updated_at_turn'],
                         state=event_model.state,
                         stop_reason=event_model.stop_reason,
                         emissary_id=event_model.emissary_id,
                         created_at=event_model.created_at,
                         updated_at=event_model.updated_at,
                         concrete_event=events.TYPES[relations.EVENT_TYPE(data['event']['type'])].deserialize(data['event']),
                         stop_after_steps=data.get('stop_after_steps', 1),
                         steps_processed=data.get('steps_processed', 0))


def _stop_event(event, reason):
    if not reason.is_FINISHED:
        event.concrete_event.on_cancel(event)

    event.state = relations.EVENT_STATE.STOPPED
    event.stop_reason = reason
    event.updated_at = datetime.datetime.now()

    save_event(event)


def cancel_event(initiator, event):
    _stop_event(event, reason=relations.EVENT_STOP_REASON.STOPPED_BY_PLAYER)

    message = 'Хранитель {keeper} остановил мероприятие эмиссара {emissary} «{event}»'
    message = message.format(keeper=initiator.nick_verbose,
                             emissary=event.emissary.utg_name.forms[1],
                             event=event.concrete_event.TYPE.text)

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[event.emissary.clan_id],
                                              event=clans_relations.EVENT.EMISSARY_EVENT_CANCELED,
                                              tags=[event.emissary.meta_object().tag,
                                                    event.emissary.place.meta_object().tag,
                                                    initiator.meta_object().tag,
                                                    event.concrete_event.TYPE.meta_object().tag],
                                              message=message)


def finish_event(event, with_error=False):
    _stop_event(event, reason=relations.EVENT_STOP_REASON.FINISHED)

    emissary = storage.emissaries.get_or_load(event.emissary_id)

    if with_error:
        message = 'Мероприятие эмиссара {emissary} «{event}» завершилось неудачно. Поставленые цели не достигнуты.'
    else:
        message = 'Закончилось мероприятие эмиссара {emissary} «{event}»'

    message = message.format(emissary=emissary.utg_name.forms[1],
                             event=event.concrete_event.TYPE.text)

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[emissary.clan_id],
                                              event=clans_relations.EVENT.EMISSARY_EVENT_FINISHED,
                                              tags=[emissary.meta_object().tag,
                                                    emissary.place.meta_object().tag,
                                                    event.concrete_event.TYPE.meta_object().tag],
                                              message=message)


def stop_event_due_emissary_left_game(event):

    _stop_event(event, reason=relations.EVENT_STOP_REASON.EMISSARY_LEFT_GAME)

    message = 'Мероприятие эмиссара [emissary] «[event]» прекращено, так как [он|emissary] [прекратил|emissary] деятельность.'
    message = linguistics_logic.technical_render(message,
                                                 {'emissary': event.emissary.utg_name_form,
                                                  'event': lexicon_dictionary.text(event.concrete_event.TYPE.text)})

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[event.emissary.clan_id],
                                              event=clans_relations.EVENT.EMISSARY_EVENT_FINISHED,
                                              tags=[event.emissary.meta_object().tag,
                                                    event.emissary.place.meta_object().tag,
                                                    event.concrete_event.TYPE.meta_object().tag],
                                              message=message)


def stop_event_due_emissary_relocated(event):

    _stop_event(event, reason=relations.EVENT_STOP_REASON.EMISSARY_RELOCATED)

    message = 'Мероприятие эмиссара [emissary] «[event]» прекращено, так как [он|emissary] [переехал|emissary] в другой город.'
    message = linguistics_logic.technical_render(message,
                                                 {'emissary': event.emissary.utg_name_form,
                                                  'event': lexicon_dictionary.text(event.concrete_event.TYPE.text)})

    clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[event.emissary.clan_id],
                                              event=clans_relations.EVENT.EMISSARY_EVENT_FINISHED,
                                              tags=[event.emissary.meta_object().tag,
                                                    event.emissary.place.meta_object().tag,
                                                    event.concrete_event.TYPE.meta_object().tag],
                                              message=message)


def do_event_step(event_id):
    with django_transaction.atomic():

        # get emissary_id
        event = storage.events.get_or_load(event_id)

        if not lock_emissary_for_update(event.emissary_id):
            return False

        event = storage.events.get_or_load(event_id)

        if not event.state.is_RUNNING:
            return True

        success = event.concrete_event.on_step(event)

        if not success:
            return False

        event.steps_processed += 1

        save_event(event)

        if event.stop_after_steps <= event.steps_processed:
            success = event.concrete_event.on_finish(event)
            finish_event(event, with_error=not success)

    return True


def process_events():
    for event in storage.events.all():
        do_event_step(event_id=event.id)


def process_events_monitoring():
    for event in storage.events.all():
        if event.concrete_event.on_monitoring(event):
            save_event(event)


def emissaries_monitoring():
    for emissary in storage.emissaries.all():
        if clans_storage.infos[emissary.clan_id].state.is_REMOVED:
            dismiss_emissary(emissary.id)


def add_clan_experience():
    for event in storage.events.all():
        experience = int(math.ceil(tt_clans_constants.EXPERIENCE_PER_EVENT * event.emissary.attrs.clan_experience))

        clans_tt_services.currencies.cmd_change_balance(account_id=event.emissary.clan_id,
                                                        type='event_experience',
                                                        amount=experience,
                                                        asynchronous=False,
                                                        autocommit=True,
                                                        currency=clans_relations.CURRENCY.EXPERIENCE)


def add_emissaries_experience():
    for event in storage.events.all():
        event.emissary.abilities.grow(event.emissary.attrs, event.concrete_event.TYPE.abilities)

        save_emissary(event.emissary)


def expected_power_per_day():
    quest_card_probability = cards_logic.get_card_probability(cards_types.CARD.QUEST_FOR_EMISSARY)

    quests_in_day = tt_cards_constants.PREMIUM_PLAYER_SPEED * quest_card_probability

    return int(math.ceil(quests_in_day *
                         tt_politic_power_constants.MEDIUM_QUEST_POWER *
                         tt_clans_constants.FIGHTERS_TO_EMISSARY))


def resource_id(clan_id, place_id):
    raise NotImplementedError("logic is removed due to moving project to read-only state")


def change_event_points(resource_id, type, currency, amount):
    restrictions = clans_tt_services.currencies.Restrictions(hard_minimum=None,
                                                             soft_minimum=None,
                                                             soft_maximum=None,
                                                             hard_maximum=None)
    tt_services.events_currencies.cmd_change_balance(account_id=resource_id,
                                                     type=type,
                                                     amount=amount,
                                                     asynchronous=False,
                                                     autocommit=True,
                                                     restrictions=restrictions,
                                                     currency=currency)


def withdraw_event_points(clan_id, place_id, currency):
    resource_id = emissaries_logic.resource_id(clan_id=clan_id,
                                               place_id=place_id)
    withdraw_event_points_by_resource_id(resource_id, currency)


def withdraw_event_points_by_resource_id(resource_id, currency):
    emissaries_logic.change_event_points(resource_id=resource_id,
                                         type='on_effect_activation',
                                         currency=currency,
                                         amount=-tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER)


# TODO: here can be racing on emissaries update
def update_emissaries_ratings():
    powers = politic_power_logic.get_emissaries_power([emissary.id for emissary in storage.emissaries.all()])

    for place in places_storage.places.all():
        emissaries = [emissary for emissary in storage.emissaries.all() if emissary.place_id == place.id]

        # reversed emissary id used to guaranty proper sorting of emissaries with equal power
        # older emissary should has greater rating
        places_powers = [(powers[emissary.id], -emissary.id, emissary.id) for emissary in emissaries]
        places_powers.sort(reverse=True)

        for rating_position, (_, _, emissary_id) in enumerate(places_powers):
            storage.emissaries[emissary_id].place_rating_position = rating_position

    storage.emissaries.save_all()


def can_clan_participate_in_pvp(clan_id):
    return any(emissary.can_participate_in_pvp() for emissary in storage.emissaries.emissaries_by_clan.get(clan_id, ()))


def has_clan_space_for_emissary(clan_id, attributes):
    in_game_emissaries_number = count_active_emissaries_for_clan(clan_id)

    return in_game_emissaries_number < attributes.emissary_maximum


def sort_for_ui(emissaries, powers):
    emissaries.sort(key=lambda emissary: (emissary.state.value, -powers[emissary.id]))


def cancel_events_except_one(event, cancel_event_callback):
    for emissary_event in storage.events.emissary_events(event.emissary_id):
        if emissary_event.id == event.id:
            continue

        cancel_event_callback(emissary_event)


def notify_clans(place_id, message, roles, exclude_clans_ids):
    clans_to_notify = {emissary.clan_id
                       for emissary in storage.emissaries.emissaries_in_place(place_id)
                       if emissary.state.is_IN_GAME and emissary.clan_id not in exclude_clans_ids}

    accounts_to_notify = clans_logic.get_members_with_roles(clans_ids=clans_to_notify,
                                                            roles=roles)

    personal_messages_logic.send_message(sender_id=accounts_logic.get_system_user_id(),
                                         recipients_ids=accounts_to_notify,
                                         body=message)


def send_event_success_message(event, account, suffix):
    emissaries_with_event = []

    for event_candiate in storage.events.clan_events(event.emissary.clan_id):
        if event_candiate.concrete_event.TYPE != event.concrete_event.TYPE:
            continue

        emissaries_with_event.append(event_candiate.emissary)

    url_template = '[url="{}"]{}[/url]'

    emissaries_text = ', '.join(url_template.format(utils_urls.full_url('https', 'game:emissaries:show', emissary.id),
                                                    emissary.utg_name.forms[1])
                                for emissary in emissaries_with_event)

    if len(emissaries_with_event) == 1:
        message = f'Благодаря усилиям эмиссара {emissaries_text} {suffix}'
    else:
        message = f'Благодаря усилиям эмиссаров {emissaries_text} {suffix}'

    personal_messages_logic.send_message(sender_id=accounts_logic.get_system_user_id(),
                                         recipients_ids=[account.id],
                                         body=message)


def remove_orphan_event_effects(logger=None):
    for effect in places_storage.effects.all():

        if effect.attribute.type.is_REWRITABLE:
            continue

        if effect.info is None:
            continue

        if 'event' not in effect.info:
            continue

        event = storage.events.get_or_load(effect.info['event'])

        if event is None:
            places_logic.remove_effect(effect.id, place_id=None)

            if logger:
                logger.info(f'effect {effect.id} orphan due event not exists')

            continue

        if event.state.is_STOPPED:
            places_logic.remove_effect(effect.id, place_id=None)

            if logger:
                logger.info(f'effect {effect.id} orphan due event is stopped')

            continue

        if event.concrete_event.effect_id != effect.id:
            places_logic.remove_effect(effect.id, place_id=None)

            if logger:
                logger.info(f'effect {effect.id} orphan due event has other effect')

            continue
