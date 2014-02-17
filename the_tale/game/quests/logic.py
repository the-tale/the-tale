# coding: utf-8
import time

from django.conf import settings as project_settings
from django.utils.log import getLogger

from dext.utils.decorators import retry_on_exception
from dext.utils.urls import url

from questgen import facts
from questgen import restrictions
from questgen import exceptions as questgen_exceptions
from questgen import transformators
from questgen import analysers
from questgen.knowledge_base import KnowledgeBase
from questgen.selectors import Selector
from questgen.quests.quests_base import QuestsBase
from questgen.relations import PLACE_TYPE as QUEST_PLACE_TYPE

from the_tale.common.utils.logic import shuffle_values_by_priority

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import waymarks_storage

from the_tale.game.persons.storage import persons_storage
from the_tale.game.persons.models import PERSON_STATE

from the_tale.game.quests.conf import quests_settings
from the_tale.game.quests.prototypes import QuestPrototype
from the_tale.game.quests import uids
from the_tale.game.quests.relations import QUESTS

QUESTS_LOGGER = getLogger('the-tale.game.quests')

WORLD_RESTRICTIONS = [restrictions.SingleLocationForObject(),
                      restrictions.ReferencesIntegrity()]
QUEST_RESTRICTIONS =  [restrictions.SingleStartStateWithNoEnters(),
                       restrictions.FinishStateExists(),
                       restrictions.AllStatesHasJumps(),
                       restrictions.ConnectedStateJumpGraph(),
                       restrictions.NoCirclesInStateJumpGraph(),
                       restrictions.MultipleJumpsFromNormalState(),
                       restrictions.ChoicesConsistency(),
                       restrictions.QuestionsConsistency(),
                       restrictions.FinishResultsConsistency()]


QUESTS_BASE = QuestsBase()
QUESTS_BASE += [quest.quest_class for quest in QUESTS.records]


def choose_quest_path_url():
    return url('game:quests:api-choose', api_version='1.0', api_client=project_settings.API_CLIENT)


def fill_places_for_first_quest(kb, hero):
    best_distance = waymarks_storage.average_path_length * 2
    best_destination = None

    for place in places_storage.all():
        if place.id == hero.position.place.id:
            continue
        path_length = waymarks_storage.look_for_road(hero.position.place, place).length
        if path_length < best_distance:
            best_distance = path_length
            best_destination = place

    kb += facts.Place(uid=uids.place(best_destination),
                      terrains=[terrain.value for terrain in best_destination.terrains],
                      externals={'id': best_destination.id},
                      type=best_destination.modifier.TYPE.quest_type if best_destination.modifier else QUEST_PLACE_TYPE.NONE)
    kb += facts.Place(uid=uids.place(hero.position.place),
                      terrains=[terrain.value for terrain in hero.position.place.terrains],
                      externals={'id': hero.position.place.id},
                      type=hero.position.place.modifier.TYPE.quest_type if hero.position.place.modifier else QUEST_PLACE_TYPE.NONE)


def fill_places_for_short_paths(kb, hero):
    for place in places_storage.all():
        if place.id != hero.position.place.id:
            path_length = waymarks_storage.look_for_road(hero.position.place, place).length
            if path_length > waymarks_storage.average_path_length:
                continue

        kb += facts.Place(uid=uids.place(place),
                          terrains=[terrain.value for terrain in place.terrains],
                          externals={'id': place.id},
                          type=place.modifier.TYPE.quest_type if place.modifier else QUEST_PLACE_TYPE.NONE)


def get_knowledge_base(hero, without_restrictions=False): # pylint: disable=R0912

    kb = KnowledgeBase()

    hero_uid = uids.hero(hero)

    kb += facts.Hero(uid=hero_uid, externals={'id': hero.id})

    # fill places
    if hero.is_first_quest_path_required:
        fill_places_for_first_quest(kb, hero)
    elif hero.is_short_quest_path_required:
        fill_places_for_short_paths(kb, hero)
    else:
        pass

    hero_position_uid = uids.place(hero.position.place)
    if hero_position_uid not in kb:
        kb += facts.Place(uid=hero_position_uid,
                          terrains=[terrain.value for terrain in hero.position.place.terrains],
                          externals={'id': hero.position.place.id},
                          type=hero.position.place.modifier.TYPE.quest_type if hero.position.place.modifier else QUEST_PLACE_TYPE.NONE)

    kb += facts.LocatedIn(object=hero_uid, place=hero_position_uid)

    if len(list(kb.filter(facts.Place))) < 2:
        for place in places_storage.all():
            place_uid = uids.place(place)
            if place_uid not in kb:
                kb += facts.Place(uid=place_uid,
                                  terrains=[terrain.value for terrain in place.terrains],
                                  externals={'id': place.id},
                                  type=place.modifier.TYPE.quest_type if place.modifier else QUEST_PLACE_TYPE.NONE)


    # fill persons
    for person in persons_storage.filter(state=PERSON_STATE.IN_GAME):
        person_uid = uids.person(person)
        place_uid = uids.place(person.place)

        if place_uid not in kb:
            continue

        kb += facts.Person(uid=person_uid, profession=person.type.quest_profession, externals={'id': person.id})
        kb += facts.LocatedIn(object=person_uid, place=place_uid)

    pref_mob = hero.preferences.mob
    if pref_mob:
        mob_uid = uids.mob(pref_mob)
        kb += ( facts.Mob(uid=mob_uid, terrains=[terrain.value for terrain in pref_mob.terrains], externals={'id': pref_mob.id}),
                facts.PreferenceMob(object=hero_uid, mob=mob_uid) )

    pref_place = hero.preferences.place
    place_uid = uids.place(pref_place) if pref_place is not None else None
    if place_uid in kb:
        kb += ( facts.PreferenceHometown(object=hero_uid, place=place_uid),
                facts.ExceptBadBranches(object=place_uid))

    pref_friend = hero.preferences.friend
    friend_uid = uids.person(pref_friend) if pref_friend is not None else None
    if friend_uid in kb:
        kb += ( facts.PreferenceFriend(object=hero_uid, person=friend_uid),
                facts.ExceptBadBranches(object=friend_uid) )

    pref_enemy = hero.preferences.enemy
    enemy_uid = uids.person(pref_enemy) if pref_enemy is not None else None
    if enemy_uid in kb:
        kb += ( facts.PreferenceEnemy(object=hero_uid, person=enemy_uid),
                facts.ExceptGoodBranches(object=enemy_uid) )

    pref_equipment_slot = hero.preferences.equipment_slot
    if pref_equipment_slot:
        kb += facts.PreferenceEquipmentSlot(object=hero_uid, equipment_slot=pref_equipment_slot.value)


    if not without_restrictions:

        for person in persons_storage.filter(state=PERSON_STATE.IN_GAME):
            if person.place.id == hero.position.place.id and hero.quests.is_person_interfered(person.id):
                kb += facts.NotFirstInitiator(person=uids.person(person))

    kb.validate_consistency(WORLD_RESTRICTIONS)


    kb += [facts.UpgradeEquipmentCost(money=QuestPrototype.upgrade_equipment_cost(hero))]

    return kb


def create_random_quest_for_hero(hero):

    start_time = time.time()

    normal_mode = True

    quests = shuffle_values_by_priority(hero.get_quests())

    excluded_quests = []
    last_quests = sorted(hero.quests.history.items(), key=lambda item: -item[1])
    if last_quests:
        excluded_quests.append(last_quests[0][0])

    quest = try_to_create_random_quest_for_hero(hero, quests, excluded_quests, without_restrictions=False)

    if quest is None:
        normal_mode = False
        quest = try_to_create_random_quest_for_hero(hero, quests, excluded_quests=[], without_restrictions=True)

    spent_time = time.time() - start_time

    QUESTS_LOGGER.info(u'hero[%(hero_id).6d]: %(spent_time)s %(is_normal)s %(quest_type)20s (allowed: %(allowed)s) (excluded: %(excluded)s)' %
                       {'hero_id': hero.id,
                        'spent_time': spent_time,
                        'is_normal': normal_mode,
                        'quest_type': quest.quests_stack[-1].type,
                        'allowed': ', '.join(quest.name for quest in quests),
                        'excluded': ', '.join(excluded_quests)})


    return quest


def try_to_create_random_quest_for_hero(hero, quests, excluded_quests, without_restrictions):

    for quest_type in quests:
        if quest_type in excluded_quests:
            continue

        try:
            return _create_random_quest_for_hero(hero, start_quests=[quest_type.quest_class.TYPE], without_restrictions=without_restrictions)
        except questgen_exceptions.RollBackError, e:
            QUESTS_LOGGER.info(u'hero[%(hero_id).6d]: can not create quest <%(quest_type)s>: %(exception)s' %
                       {'hero_id': hero.id,
                        'quest_type': quest_type,
                        'exception': e})
            continue

    return None


@retry_on_exception(max_retries=quests_settings.MAX_QUEST_GENERATION_RETRIES, exceptions=[questgen_exceptions.RollBackError])
def _create_random_quest_for_hero(hero, start_quests, without_restrictions=False):
    knowledge_base = get_knowledge_base(hero, without_restrictions=without_restrictions)

    selector = Selector(knowledge_base, QUESTS_BASE)

    hero_uid = uids.hero(hero)

    start_place = selector.place_for(objects=(hero_uid,))

    quests_facts = selector.create_quest_from_place(nesting=0,
                                                    initiator_position=start_place,
                                                    allowed=start_quests,
                                                    excluded=[],
                                                    tags=('can_start', ))

    knowledge_base += quests_facts

    transformators.activate_events(knowledge_base) # TODO: after remove restricted states
    transformators.remove_restricted_states(knowledge_base)
    transformators.remove_broken_states(knowledge_base) # MUST be called after all graph changes
    transformators.determine_default_choices(knowledge_base, preferred_markers=hero.prefered_quest_markers()) # MUST be called after all graph changes and on valid graph
    transformators.remove_unused_actors(knowledge_base)

    knowledge_base.validate_consistency(WORLD_RESTRICTIONS)
    knowledge_base.validate_consistency(QUEST_RESTRICTIONS)

    states_to_percents = analysers.percents_collector(knowledge_base)

    quest = QuestPrototype(hero=hero, knowledge_base=knowledge_base, states_to_percents=states_to_percents)

    if quest.machine.can_do_step():
        quest.machine.step() # do first step to setup pointer

    return quest
