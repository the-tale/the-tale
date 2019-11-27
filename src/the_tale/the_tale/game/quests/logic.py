
import smart_imports

smart_imports.all()


QUESTS_LOGGER = logging.getLogger('the-tale.game.quests')

WORLD_RESTRICTIONS = [questgen_restrictions.SingleLocationForObject(),
                      questgen_restrictions.ReferencesIntegrity()]
QUEST_RESTRICTIONS = [questgen_restrictions.SingleStartStateWithNoEnters(),
                      questgen_restrictions.FinishStateExists(),
                      questgen_restrictions.AllStatesHasJumps(),
                      questgen_restrictions.ConnectedStateJumpGraph(),
                      questgen_restrictions.NoCirclesInStateJumpGraph(),
                      questgen_restrictions.MultipleJumpsFromNormalState(),
                      questgen_restrictions.ChoicesConsistency(),
                      questgen_restrictions.QuestionsConsistency(),
                      questgen_restrictions.FinishResultsConsistency()]


QUESTS_BASE = questgen_quests_quests_base.QuestsBase()
QUESTS_BASE += [quest.quest_class for quest in relations.QUESTS.records]


class HeroQuestInfo(object):
    __slots__ = ('id',
                 'level',
                 'position_place_id',
                 'is_first_quest_path_required',
                 'is_short_quest_path_required',
                 'preferences_mob_id',
                 'preferences_place_id',
                 'preferences_friend_id',
                 'preferences_enemy_id',
                 'preferences_equipment_slot',
                 'interfered_persons',
                 'quests_priorities',
                 'excluded_quests',
                 'prefered_quest_markers')

    def __init__(self,
                 id,
                 level,
                 position_place_id,
                 is_first_quest_path_required,
                 is_short_quest_path_required,
                 preferences_mob_id,
                 preferences_place_id,
                 preferences_friend_id,
                 preferences_enemy_id,
                 preferences_equipment_slot,
                 interfered_persons,
                 quests_priorities,
                 excluded_quests,
                 prefered_quest_markers):
        self.id = id
        self.level = level
        self.position_place_id = position_place_id
        self.is_first_quest_path_required = is_first_quest_path_required
        self.is_short_quest_path_required = is_short_quest_path_required
        self.preferences_mob_id = preferences_mob_id
        self.preferences_place_id = preferences_place_id
        self.preferences_friend_id = preferences_friend_id
        self.preferences_enemy_id = preferences_enemy_id
        self.preferences_equipment_slot = preferences_equipment_slot
        self.interfered_persons = interfered_persons
        self.quests_priorities = quests_priorities
        self.excluded_quests = excluded_quests
        self.prefered_quest_markers = prefered_quest_markers

    def serialize(self):
        return {'id': self.id,
                'level': self.level,
                'position_place_id': self.position_place_id,
                'is_first_quest_path_required': self.is_first_quest_path_required,
                'is_short_quest_path_required': self.is_short_quest_path_required,
                'preferences_mob_id': self.preferences_mob_id,
                'preferences_place_id': self.preferences_place_id,
                'preferences_friend_id': self.preferences_friend_id,
                'preferences_enemy_id': self.preferences_enemy_id,
                'preferences_equipment_slot': self.preferences_equipment_slot.value if self.preferences_equipment_slot else None,
                'interfered_persons': self.interfered_persons,
                'quests_priorities': [(quest_type.value, priority) for quest_type, priority in self.quests_priorities],
                'excluded_quests': list(self.excluded_quests),
                'prefered_quest_markers': list(self.prefered_quest_markers)}

    @classmethod
    def deserialize(cls, data):
        return cls(id=data['id'],
                   level=data['level'],
                   position_place_id=data['position_place_id'],
                   is_first_quest_path_required=data['is_first_quest_path_required'],
                   is_short_quest_path_required=data['is_short_quest_path_required'],
                   preferences_mob_id=data['preferences_mob_id'],
                   preferences_place_id=data['preferences_place_id'],
                   preferences_friend_id=data['preferences_friend_id'],
                   preferences_enemy_id=data['preferences_enemy_id'],
                   preferences_equipment_slot=heroes_relations.EQUIPMENT_SLOT(data['preferences_equipment_slot']) if data['preferences_equipment_slot'] is not None else None,
                   interfered_persons=data['interfered_persons'],
                   quests_priorities=[(relations.QUESTS(quest_type), priority) for quest_type, priority in data['quests_priorities']],
                   excluded_quests=set(data['excluded_quests']),
                   prefered_quest_markers=set(data['prefered_quest_markers']))

    def __eq__(self, other):
        return self.serialize() == other.serialize()

    def __neq__(self, other):
        return not self.__eq__(other)


def choose_quest_path_url():
    return dext_urls.url('game:quests:api-choose', api_version='1.0', api_client=django_settings.API_CLIENT)


def fact_place(place):
    return questgen_facts.Place(uid=uids.place(place.id),
                                terrains=[terrain.value for terrain in place.terrains],
                                externals={'id': place.id},
                                type=place.modifier_quest_type())


def fact_mob(mob):
    return questgen_facts.Mob(uid=uids.mob(mob.id),
                              terrains=[terrain.value for terrain in mob.terrains],
                              externals={'id': mob.id})


def fact_person(person):
    return questgen_facts.Person(uid=uids.person(person.id),
                                 profession=person.type.quest_profession,
                                 externals={'id': person.id,
                                            'type': game_relations.ACTOR.PERSON.value})


def fact_emissary(emissary):
    return questgen_facts.Person(uid=uids.emissary(emissary.id),
                                 profession=None,
                                 externals={'id': emissary.id,
                                            'type': game_relations.ACTOR.EMISSARY.value})


def fact_social_connection(connection_type, person_uid, connected_person_uid):
    return questgen_facts.SocialConnection(person_to=person_uid,
                                           person_from=connected_person_uid,
                                           type=connection_type.questgen_type)


def fact_located_in(person):
    return questgen_facts.LocatedIn(object=uids.person(person.id), place=uids.place(person.place.id))


def fill_places_for_first_quest(kb, hero_info):
    best_distance = c.QUEST_AREA_MAXIMUM_RADIUS
    best_destination = None

    hero_place = places_storage.places[hero_info.position_place_id]

    for place in places_storage.places.all():
        if place.id == hero_info.position_place_id:
            continue

        path_length = navigation_logic.manhattan_distance(hero_place.x,
                                                          hero_place.y,
                                                          place.x,
                                                          place.y)

        if path_length < best_distance:
            best_distance = path_length
            best_destination = place

    kb += fact_place(best_destination)
    kb += fact_place(places_storage.places[hero_info.position_place_id])


def fill_places(kb, hero_info, max_distance):
    places = []

    hero_place = places_storage.places[hero_info.position_place_id]

    for place in places_storage.places.all():
        path_length = navigation_logic.manhattan_distance(hero_place.x,
                                                          hero_place.y,
                                                          place.x,
                                                          place.y)

        if path_length > max_distance:
            continue

        places.append((path_length, place))

    places.sort(key=lambda x: x[0])

    chosen_places = []

    for base_distance, place in places:
        for chosen_place in chosen_places:
            path_length = navigation_logic.manhattan_distance(chosen_place.x,
                                                              chosen_place.y,
                                                              place.x,
                                                              place.y)

            if path_length > max_distance:
                break

        else:
            chosen_places.append(place)

    for place in chosen_places:
        uid = uids.place(place.id)

        if uid in kb:
            continue

        kb += fact_place(place)


def setup_places(kb, hero_info):
    if hero_info.is_first_quest_path_required:
        fill_places_for_first_quest(kb, hero_info)
    elif hero_info.is_short_quest_path_required:
        fill_places(kb, hero_info, max_distance=c.QUEST_AREA_SHORT_RADIUS)
    else:
        fill_places(kb, hero_info, max_distance=c.QUEST_AREA_RADIUS)

    hero_position_uid = uids.place(hero_info.position_place_id)
    if hero_position_uid not in kb:
        kb += fact_place(places_storage.places[hero_info.position_place_id])

    kb += questgen_facts.LocatedIn(object=uids.hero(hero_info.id), place=hero_position_uid)

    if len(list(kb.filter(questgen_facts.Place))) < 2:
        fill_places(kb, hero_info, max_distance=c.QUEST_AREA_MAXIMUM_RADIUS)


def setup_persons(kb, hero_info):
    for person in persons_storage.persons.all():
        place_uid = uids.place(person.place.id)

        if place_uid not in kb:
            continue

        f_person = fact_person(person)
        kb += f_person
        kb += questgen_facts.LocatedIn(object=f_person.uid, place=place_uid)


def setup_social_connections(kb):
    persons_in_kb = {f_person.externals['id']: f_person.uid for f_person in kb.filter(questgen_facts.Person)}

    for person_id, person_uid in persons_in_kb.items():
        person = persons_storage.persons[person_id]

        for connection_type, connected_person_id in persons_storage.social_connections.get_person_connections(person):
            if connected_person_id not in persons_in_kb:
                continue
            kb += fact_social_connection(connection_type, person_uid, persons_in_kb[connected_person_id])


def setup_preferences(kb, hero_info):
    hero_uid = uids.hero(hero_info.id)

    if hero_info.preferences_mob_id is not None:
        f_mob = fact_mob(mobs_storage.mobs[hero_info.preferences_mob_id])
        if f_mob.uid not in kb:
            kb += f_mob
        kb += questgen_facts.PreferenceMob(object=hero_uid, mob=f_mob.uid)

    if hero_info.preferences_place_id is not None:
        f_place = fact_place(places_storage.places[hero_info.preferences_place_id])
        if f_place.uid not in kb:
            kb += f_place
        kb += questgen_facts.PreferenceHometown(object=hero_uid, place=f_place.uid)

    if hero_info.preferences_friend_id is not None:
        friend = persons_storage.persons[hero_info.preferences_friend_id]

        f_place = fact_place(friend.place)
        f_person = fact_person(friend)

        if f_place.uid not in kb:
            kb += f_place

        if f_person.uid not in kb:
            kb += f_person

        kb += questgen_facts.PreferenceFriend(object=hero_uid, person=f_person.uid)
        kb += questgen_facts.ExceptBadBranches(object=f_person.uid)

    if hero_info.preferences_enemy_id:
        enemy = persons_storage.persons[hero_info.preferences_enemy_id]

        f_place = fact_place(enemy.place)
        f_person = fact_person(enemy)

        if f_place.uid not in kb:
            kb += f_place

        if f_person.uid not in kb:
            kb += f_person

        kb += questgen_facts.PreferenceEnemy(object=hero_uid, person=f_person.uid)
        kb += questgen_facts.ExceptGoodBranches(object=f_person.uid)

    if hero_info.preferences_equipment_slot:
        kb += questgen_facts.PreferenceEquipmentSlot(object=hero_uid, equipment_slot=hero_info.preferences_equipment_slot.value)


def get_knowledge_base(hero_info, without_restrictions=False):  # pylint: disable=R0912

    kb = questgen_knowledge_base.KnowledgeBase()

    hero_uid = uids.hero(hero_info.id)

    kb += questgen_facts.Hero(uid=hero_uid, externals={'id': hero_info.id})

    setup_places(kb, hero_info)
    setup_persons(kb, hero_info)
    setup_preferences(kb, hero_info)
    setup_social_connections(kb)

    if not without_restrictions:

        for person in persons_storage.persons.all():
            if person.place.id == hero_info.position_place_id and person.id in hero_info.interfered_persons:
                kb += questgen_facts.NotFirstInitiator(person=uids.person(person.id))

    kb.validate_consistency(WORLD_RESTRICTIONS)

    kb += [questgen_facts.UpgradeEquipmentCost(money=prototypes.QuestPrototype.upgrade_equipment_cost(hero_info))]

    return kb


def create_random_quest_for_hero(hero_info, logger):
    constructor = place_quest_constructor_fabric(place_uid=uids.place(hero_info.position_place_id))

    return create_random_quest_with_constructor(hero_info, constructor, logger)


def create_random_quest_for_emissary(hero_info, emissary, person_action, logger):
    constructor = emissary_quest_constructor_fabric(hero_uid=uids.hero(hero_info.id),
                                                    emissary=emissary,
                                                    person_action=person_action)

    return create_random_quest_with_constructor(hero_info, constructor, logger)


def create_random_quest_with_constructor(hero_info, constructor, logger):

    start_time = time.time()

    normal_mode = True

    quests = utils_logic.shuffle_values_by_priority(hero_info.quests_priorities)

    excluded_quests = hero_info.excluded_quests

    quest_type, knowledge_base = try_to_create_random_quest_for_hero(hero_info,
                                                                     quests,
                                                                     excluded_quests,
                                                                     without_restrictions=False,
                                                                     constructor=constructor,
                                                                     logger=logger)

    if knowledge_base is None:
        normal_mode = False
        quest_type, knowledge_base = try_to_create_random_quest_for_hero(hero_info,
                                                                         quests,
                                                                         excluded_quests=[],
                                                                         without_restrictions=True,
                                                                         constructor=constructor,
                                                                         logger=logger)

    spent_time = time.time() - start_time

    logger.info('hero[%(hero_id).6d]: %(spent_time)s %(is_normal)s %(quest_type)20s (allowed: %(allowed)s) (excluded: %(excluded)s)' %
                {'hero_id': hero_info.id,
                 'spent_time': spent_time,
                 'is_normal': normal_mode,
                 'quest_type': quest_type,
                 'allowed': ', '.join(quest.quest_class.TYPE for quest in quests),
                 'excluded': ', '.join(excluded_quests)})

    return knowledge_base


def try_to_create_random_quest_for_hero(hero_info, quests, excluded_quests, without_restrictions, constructor, logger):

    for quest_type in quests:
        if quest_type.quest_class.TYPE in excluded_quests:
            continue

        try:
            return quest_type, _create_random_quest_for_hero(hero_info,
                                                             constructor=constructor,
                                                             start_quests=[quest_type.quest_class.TYPE],
                                                             without_restrictions=without_restrictions)
        except questgen_exceptions.RollBackError as e:
            logger.info('hero[%(hero_id).6d]: can not create quest <%(quest_type)s>: %(exception)s' %
                        {'hero_id': hero_info.id,
                         'quest_type': quest_type,
                         'exception': e})
            continue

    return None, None


@dext_decorators.retry_on_exception(max_retries=conf.settings.MAX_QUEST_GENERATION_RETRIES, exceptions=[questgen_exceptions.RollBackError])
def _create_random_quest_for_hero(hero_info, constructor, start_quests, without_restrictions=False):
    knowledge_base = get_knowledge_base(hero_info, without_restrictions=without_restrictions)

    selector = questgen_selectors.Selector(knowledge_base, QUESTS_BASE, social_connection_probability=0)

    knowledge_base += constructor(selector, start_quests)

    questgen_transformators.activate_events(knowledge_base)  # TODO: after remove restricted states
    questgen_transformators.remove_restricted_states(knowledge_base)
    questgen_transformators.remove_broken_states(knowledge_base)  # MUST be called after all graph changes
    questgen_transformators.determine_default_choices(knowledge_base, preferred_markers=hero_info.prefered_quest_markers)  # MUST be called after all graph changes and on valid graph
    questgen_transformators.remove_unused_actors(knowledge_base)

    knowledge_base.validate_consistency(WORLD_RESTRICTIONS)
    knowledge_base.validate_consistency(QUEST_RESTRICTIONS)

    return knowledge_base


def place_quest_constructor_fabric(place_uid):

    def constructor(selector, start_quests):
        initiator_position = selector._kb[place_uid]

        selector.reserve(initiator_position)

        return selector.create_quest_from_place(nesting=0,
                                                initiator_position=initiator_position,
                                                allowed=start_quests,
                                                excluded=[],
                                                tags=('can_start', ))

    return constructor


def emissary_quest_constructor_fabric(hero_uid, emissary, person_action):

    def constructor(selector, start_quests):
        f_emissary = fact_emissary(emissary)
        f_emissary_place = fact_place(emissary.place)

        selector._kb += f_emissary
        selector._kb += questgen_facts.LocatedIn(object=f_emissary.uid, place=uids.place(emissary.place_id))

        if f_emissary_place.uid not in selector._kb:
            selector._kb += f_emissary_place

        if person_action.is_HELP:
            selector._kb += questgen_facts.OnlyGoodBranches(object=f_emissary.uid)
        elif person_action.is_HARM:
            selector._kb += questgen_facts.OnlyBadBranches(object=f_emissary.uid)
        else:
            raise NotImplementedError

        selector.reserve(f_emissary)
        selector.reserve(f_emissary_place)

        return selector.create_quest_from_person(nesting=0,
                                                 initiator=f_emissary,
                                                 allowed=start_quests,
                                                 excluded=[],
                                                 tags=('can_start', ))

    return constructor


def create_hero_info(hero):
    quests_priorities = hero.get_quests_priorities()

    return HeroQuestInfo(id=hero.id,
                         level=hero.level,
                         position_place_id=hero.position.cell().nearest_place_id,
                         is_first_quest_path_required=hero.is_first_quest_path_required,
                         is_short_quest_path_required=hero.is_short_quest_path_required,
                         preferences_mob_id=hero.preferences.mob.id if hero.preferences.mob else None,
                         preferences_place_id=hero.preferences.place.id if hero.preferences.place else None,
                         preferences_friend_id=hero.preferences.friend.id if hero.preferences.friend else None,
                         preferences_enemy_id=hero.preferences.enemy.id if hero.preferences.enemy else None,
                         preferences_equipment_slot=hero.preferences.equipment_slot,
                         interfered_persons=hero.quests.get_interfered_persons(),
                         quests_priorities=quests_priorities,
                         excluded_quests=hero.quests.excluded_quests(len(quests_priorities) // 2),
                         prefered_quest_markers=hero.prefered_quest_markers())


def request_quest_for_hero(hero, emissary_id=None, person_action=None):
    hero_info = create_hero_info(hero)
    amqp_environment.environment.workers.quests_generator.cmd_request_quest(hero.account_id,
                                                                            hero_info.serialize(),
                                                                            emissary_id=emissary_id,
                                                                            person_action=person_action)


def setup_quest_for_hero(hero, knowledge_base_data):

    # do nothing if hero has already had quest
    if not hero.actions.current_action.searching_quest:
        return

    knowledge_base = questgen_knowledge_base.KnowledgeBase.deserialize(knowledge_base_data, fact_classes=questgen_facts.FACTS)

    states_to_percents = questgen_analysers.percents_collector(knowledge_base)

    quest = prototypes.QuestPrototype(hero=hero, knowledge_base=knowledge_base, states_to_percents=states_to_percents)

    if quest.machine.can_do_step():
        quest.machine.step()  # do first step to setup pointer

    hero.actions.current_action.setup_quest(quest)


def extract_person_type(fact):
    return game_relations.ACTOR(fact.externals.get('type', game_relations.ACTOR.PERSON.value))
