# coding: utf-8
import random

# from django.utils.log import getLogger
from django.conf import settings as project_settings

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

from questgen.quests.spying import Spying
from questgen.quests.hunt import Hunt
from questgen.quests.hometown import Hometown
from questgen.quests.search_smith import SearchSmith
from questgen.quests.delivery import Delivery
from questgen.quests.caravan import Caravan
from questgen.quests.collect_debt import CollectDebt
from questgen.quests.help_friend import HelpFriend
from questgen.quests.interfere_enemy import InterfereEnemy
from questgen.quests.help import Help
from questgen.quests.pilgrimage import Pilgrimage


from the_tale.game.balance import constants as c

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import waymarks_storage

from the_tale.game.persons.storage import persons_storage
from the_tale.game.persons.models import PERSON_STATE

from the_tale.game.quests.conf import quests_settings
from the_tale.game.quests.prototypes import QuestPrototype
from the_tale.game.quests import uids

# logger = getLogger('the-tale.workers.game_logic')

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
QUESTS_BASE += [CollectDebt, Caravan, Delivery, Spying, Hunt, Hometown, SearchSmith, HelpFriend, InterfereEnemy, Help, Pilgrimage]

NORMAL_QUESTS = [CollectDebt.TYPE, Spying.TYPE, Delivery.TYPE, Caravan.TYPE, Help.TYPE]


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

        for person in persons_storage.all():
            if person.place.id == hero.position.place.id and hero.quests.is_person_interfered(person.id):
                kb += facts.NotFirstInitiator(person=uids.person(person))

    kb.validate_consistency(WORLD_RESTRICTIONS)


    kb += [facts.UpgradeEquipmentCost(money=QuestPrototype.upgrade_equipment_cost(hero))]

    return kb


def create_random_quest_for_hero(hero):

    special = (c.QUESTS_SPECIAL_FRACTION > random.uniform(0, 1))

    # logger.warn('create quest: %s' % {True: 'SPECIAL', False: 'NORMAL'}[special])

    try:

        if special:
            try:
                return _create_random_quest_for_hero(hero, special=True)
            except questgen_exceptions.RollBackError:
                # logger.warn('special quest failed')
                pass

        return _create_random_quest_for_hero(hero, special=False)

    except questgen_exceptions.RollBackError:
        # logger.warn('normal quest failed')
        return _create_random_quest_for_hero(hero, special=False, without_restrictions=True)


def get_first_quests(hero, special):
    if special:
        quests = hero.get_special_quests()
        if quests:
            return quests

    if random.uniform(0, 1) < c.QUESTS_PILGRIMAGE_FRACTION:
        return [Pilgrimage.TYPE]

    return NORMAL_QUESTS

@retry_on_exception(max_retries=quests_settings.MAX_QUEST_GENERATION_RETRIES, exceptions=[questgen_exceptions.RollBackError])
def _create_random_quest_for_hero(hero, special, without_restrictions=False):
    knowledge_base = get_knowledge_base(hero, without_restrictions=without_restrictions)

    selector = Selector(knowledge_base, QUESTS_BASE)

    hero_uid = uids.hero(hero)

    start_place = selector.place_for(objects=(hero_uid,))

    # current_time = TimePrototype.get_current_turn_number()

    excluded_quests = []
    # for quest_type, turn_number in hero.quests.history.items():
    #     if turn_number + c.QUESTS_LOCK_TIME.get(quest_type, 0) >= current_time:
    #         excluded_quests.append(quest_type)

    quests_facts = selector.create_quest_from_place(nesting=0,
                                                    initiator_position=start_place,
                                                    allowed=get_first_quests(hero, special=special),
                                                    excluded=excluded_quests,
                                                    tags=('can_start', ))

    knowledge_base += quests_facts

    transformators.activate_events(knowledge_base) # TODO: after remove restricted states
    transformators.remove_restricted_states(knowledge_base)
    transformators.remove_broken_states(knowledge_base) # MUST be called after all graph changes
    transformators.determine_default_choices(knowledge_base) # MUST be called after all graph changes and on valid graph
    transformators.remove_unused_actors(knowledge_base)

    knowledge_base.validate_consistency(WORLD_RESTRICTIONS)
    knowledge_base.validate_consistency(QUEST_RESTRICTIONS)

    states_to_percents = analysers.percents_collector(knowledge_base)

    quest = QuestPrototype(hero=hero, knowledge_base=knowledge_base, states_to_percents=states_to_percents)

    if quest.machine.can_do_step():
        quest.machine.step() # do first step to setup pointer

    return quest
