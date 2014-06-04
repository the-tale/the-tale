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

from the_tale.game.balance import constants as c

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


def fact_place(place):
    return facts.Place(uid=uids.place(place),
                       terrains=[terrain.value for terrain in place.terrains],
                       externals={'id': place.id},
                       type=place.modifier.TYPE.quest_type if place.modifier else QUEST_PLACE_TYPE.NONE)

def fact_mob(mob):
    return facts.Mob(uid=uids.mob(mob),
                     terrains=[terrain.value for terrain in mob.terrains],
                     externals={'id': mob.id})

def fact_person(person):
    return facts.Person(uid=uids.person(person),
                        profession=person.type.quest_profession,
                        externals={'id': person.id})

def fill_places_for_first_quest(kb, hero):
    best_distance = c.QUEST_AREA_MAXIMUM_RADIUS
    best_destination = None

    for place in places_storage.all():
        if place.id == hero.position.place.id:
            continue
        path_length = waymarks_storage.look_for_road(hero.position.place, place).length
        if path_length < best_distance:
            best_distance = path_length
            best_destination = place

    kb += fact_place(best_destination)
    kb += fact_place(hero.position.place)


# def fill_places(kb, hero, max_distance):
#     for place in places_storage.all():

#         if place.id != hero.position.place.id:
#             path_length = waymarks_storage.look_for_road(hero.position.place, place).length
#             if path_length > max_distance:
#                 continue

#         uid = uids.place(place)

#         if uid in kb:
#             continue

#         kb += fact_place(place)


def fill_places(kb, hero, max_distance):
    places = []

    for place in places_storage.all():
        path_length = waymarks_storage.look_for_road(hero.position.place, place).length

        if path_length > max_distance:
            continue

        places.append((path_length, place))

    places.sort()


    chosen_places = []

    for base_distance, place in places:
        for chosen_place in chosen_places:
            path_length = waymarks_storage.look_for_road(chosen_place, place).length

            if path_length > max_distance:
                break

        else:
            chosen_places.append(place)


    for place in chosen_places:
        uid = uids.place(place)

        if uid in kb:
            continue

        kb += fact_place(place)


def setup_places(kb, hero):
    if hero.is_first_quest_path_required:
        fill_places_for_first_quest(kb, hero)
    elif hero.is_short_quest_path_required:
        fill_places(kb, hero, max_distance=c.QUEST_AREA_RADIUS)
    else:
        pass

    hero_position_uid = uids.place(hero.position.place)
    if hero_position_uid not in kb:
        kb += fact_place(hero.position.place)

    kb += facts.LocatedIn(object=uids.hero(hero), place=hero_position_uid)

    if len(list(kb.filter(facts.Place))) < 2:
        fill_places(kb, hero, max_distance=c.QUEST_AREA_MAXIMUM_RADIUS)


def setup_persons(kb, hero):
    for person in persons_storage.filter(state=PERSON_STATE.IN_GAME):
        place_uid = uids.place(person.place)

        if place_uid not in kb:
            continue

        f_person = fact_person(person)
        kb += f_person
        kb += facts.LocatedIn(object=f_person.uid, place=place_uid)


def setup_preferences(kb, hero):
    hero_uid = uids.hero(hero)

    if hero.preferences.mob:
        f_mob = fact_mob(hero.preferences.mob)
        if f_mob.uid not in kb:
            kb += f_mob
        kb += facts.PreferenceMob(object=hero_uid, mob=f_mob.uid)

    if hero.preferences.place:
        f_place = fact_place(hero.preferences.place)
        if f_place.uid not in kb:
            kb += f_place
        kb += facts.PreferenceHometown(object=hero_uid, place=f_place.uid)

    if hero.preferences.friend:
        f_place = fact_place(hero.preferences.friend.place)
        f_person = fact_person(hero.preferences.friend)

        if f_place.uid not in kb:
            kb += f_place

        if f_person.uid not in kb:
            kb += f_person

        kb += facts.PreferenceFriend(object=hero_uid, person=f_person.uid)
        kb += facts.ExceptBadBranches(object=f_person.uid)

    if hero.preferences.enemy:
        f_place = fact_place(hero.preferences.enemy.place)
        f_person = fact_person(hero.preferences.enemy)

        if f_place.uid not in kb:
            kb += f_place

        if f_person.uid not in kb:
            kb += f_person

        kb += facts.PreferenceEnemy(object=hero_uid, person=f_person.uid)
        kb += facts.ExceptGoodBranches(object=f_person.uid)

    if hero.preferences.equipment_slot:
        kb += facts.PreferenceEquipmentSlot(object=hero_uid, equipment_slot=hero.preferences.equipment_slot.value)



def get_knowledge_base(hero, without_restrictions=False): # pylint: disable=R0912

    kb = KnowledgeBase()

    hero_uid = uids.hero(hero)

    kb += facts.Hero(uid=hero_uid, externals={'id': hero.id})

    setup_places(kb, hero)
    setup_persons(kb, hero)
    setup_preferences(kb, hero)

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

    excluded_quests = hero.quests.excluded_quests(max_number=len(quests) / 2)

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
                        'allowed': ', '.join(quest.quest_class.TYPE for quest in quests),
                        'excluded': ', '.join(excluded_quests)})


    return quest


def try_to_create_random_quest_for_hero(hero, quests, excluded_quests, without_restrictions):

    for quest_type in quests:
        if quest_type.quest_class.TYPE in excluded_quests:
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
