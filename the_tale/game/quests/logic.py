# coding: utf-8
import time

from django.conf import settings as project_settings
from django.utils.log import getLogger

from dext.common.utils.decorators import retry_on_exception
from dext.common.utils.urls import url

from questgen import facts
from questgen import restrictions
from questgen import exceptions as questgen_exceptions
from questgen import transformators
from questgen import analysers
from questgen.knowledge_base import KnowledgeBase
from questgen.selectors import Selector
from questgen.quests.quests_base import QuestsBase
from questgen.relations import PLACE_TYPE as QUEST_PLACE_TYPE

from the_tale import amqp_environment

from the_tale.common.utils.logic import shuffle_values_by_priority

from the_tale.game.balance import constants as c

from the_tale.game.mobs import storage as mobs_storage

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import waymarks_storage

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons.relations import PERSON_STATE

from the_tale.game.quests.conf import quests_settings
from the_tale.game.quests.prototypes import QuestPrototype
from the_tale.game.quests import uids
from the_tale.game.quests import relations

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
        self.prefered_quest_markers  = prefered_quest_markers

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



def choose_quest_path_url():
    return url('game:quests:api-choose', api_version='1.0', api_client=project_settings.API_CLIENT)


def fact_place(place):
    return facts.Place(uid=uids.place(place.id),
                       terrains=[terrain.value for terrain in place.terrains],
                       externals={'id': place.id},
                       type=place.modifier.TYPE.quest_type if place.modifier else QUEST_PLACE_TYPE.NONE)

def fact_mob(mob):
    return facts.Mob(uid=uids.mob(mob.id),
                     terrains=[terrain.value for terrain in mob.terrains],
                     externals={'id': mob.id})

def fact_person(person):
    return facts.Person(uid=uids.person(person.id),
                        profession=person.type.quest_profession,
                        externals={'id': person.id})

def fact_social_connection(connection_type, person_uid, connected_person_uid):
    return facts.SocialConnection(person_to=person_uid,
                                  person_from=connected_person_uid,
                                  type=connection_type.questgen_type)

def fact_located_in(person):
    return facts.LocatedIn(object=uids.person(person.id), place=uids.place(person.place.id))

def fill_places_for_first_quest(kb, hero_info):
    best_distance = c.QUEST_AREA_MAXIMUM_RADIUS
    best_destination = None

    for place in places_storage.all():
        if place.id == hero_info.position_place_id:
            continue
        path_length = waymarks_storage.look_for_road(places_storage[hero_info.position_place_id], place).length
        if path_length < best_distance:
            best_distance = path_length
            best_destination = place

    kb += fact_place(best_destination)
    kb += fact_place(places_storage[hero_info.position_place_id])


def fill_places(kb, hero_info, max_distance):
    places = []

    for place in places_storage.all():
        path_length = waymarks_storage.look_for_road(places_storage[hero_info.position_place_id], place).length

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
        kb += fact_place(places_storage[hero_info.position_place_id])

    kb += facts.LocatedIn(object=uids.hero(hero_info.id), place=hero_position_uid)

    if len(list(kb.filter(facts.Place))) < 2:
        fill_places(kb, hero_info, max_distance=c.QUEST_AREA_MAXIMUM_RADIUS)


def setup_persons(kb, hero_info):
    for person in persons_storage.persons_storage.filter(state=PERSON_STATE.IN_GAME):
        place_uid = uids.place(person.place.id)

        if place_uid not in kb:
            continue

        f_person = fact_person(person)
        kb += f_person
        kb += facts.LocatedIn(object=f_person.uid, place=place_uid)


def setup_social_connections(kb):
    persons_in_kb = {f_person.externals['id']: f_person.uid for f_person in kb.filter(facts.Person)}

    for person_id, person_uid in persons_in_kb.iteritems():
        person = persons_storage.persons_storage[person_id]

        for connection_type, connected_person_id in persons_storage.social_connections.get_person_connections(person):
            if connected_person_id not in persons_in_kb:
                continue
            kb += fact_social_connection(connection_type, person_uid, persons_in_kb[connected_person_id])


def setup_preferences(kb, hero_info):
    hero_uid = uids.hero(hero_info.id)

    if hero_info.preferences_mob_id is not None:
        f_mob = fact_mob(mobs_storage.mobs_storage[hero_info.preferences_mob_id])
        if f_mob.uid not in kb:
            kb += f_mob
        kb += facts.PreferenceMob(object=hero_uid, mob=f_mob.uid)

    if hero_info.preferences_place_id is not None:
        f_place = fact_place(places_storage[hero_info.preferences_place_id])
        if f_place.uid not in kb:
            kb += f_place
        kb += facts.PreferenceHometown(object=hero_uid, place=f_place.uid)

    if hero_info.preferences_friend_id is not None:
        friend = persons_storage.persons_storage[hero_info.preferences_friend_id]

        f_place = fact_place(friend.place)
        f_person = fact_person(friend)

        if f_place.uid not in kb:
            kb += f_place

        if f_person.uid not in kb:
            kb += f_person

        kb += facts.PreferenceFriend(object=hero_uid, person=f_person.uid)
        kb += facts.ExceptBadBranches(object=f_person.uid)

    if hero_info.preferences_enemy_id:
        enemy = persons_storage.persons_storage[hero_info.preferences_enemy_id]

        f_place = fact_place(enemy.place)
        f_person = fact_person(enemy)

        if f_place.uid not in kb:
            kb += f_place

        if f_person.uid not in kb:
            kb += f_person

        kb += facts.PreferenceEnemy(object=hero_uid, person=f_person.uid)
        kb += facts.ExceptGoodBranches(object=f_person.uid)

    if hero_info.preferences_equipment_slot:
        kb += facts.PreferenceEquipmentSlot(object=hero_uid, equipment_slot=hero_info.preferences_equipment_slot.value)



def get_knowledge_base(hero_info, without_restrictions=False): # pylint: disable=R0912

    kb = KnowledgeBase()

    hero_uid = uids.hero(hero_info.id)

    kb += facts.Hero(uid=hero_uid, externals={'id': hero_info.id})

    setup_places(kb, hero_info)
    setup_persons(kb, hero_info)
    setup_preferences(kb, hero_info)
    setup_social_connections(kb)

    if not without_restrictions:

        for person in persons_storage.persons_storage.filter(state=PERSON_STATE.IN_GAME):
            if person.place.id == hero_info.position_place_id and person.id in hero_info.interfered_persons:
                kb += facts.NotFirstInitiator(person=uids.person(person.id))

    kb.validate_consistency(WORLD_RESTRICTIONS)

    kb += [facts.UpgradeEquipmentCost(money=QuestPrototype.upgrade_equipment_cost(hero_info))]

    return kb


def create_random_quest_for_hero(hero_info, logger):

    start_time = time.time()

    normal_mode = True

    quests = shuffle_values_by_priority(hero_info.quests_priorities)

    excluded_quests = hero_info.excluded_quests

    quest_type, knowledge_base = try_to_create_random_quest_for_hero(hero_info, quests, excluded_quests, without_restrictions=False, logger=logger)

    if knowledge_base is None:
        normal_mode = False
        quest_type, knowledge_base = try_to_create_random_quest_for_hero(hero_info, quests, excluded_quests=[], without_restrictions=True, logger=logger)

    spent_time = time.time() - start_time

    logger.info(u'hero[%(hero_id).6d]: %(spent_time)s %(is_normal)s %(quest_type)20s (allowed: %(allowed)s) (excluded: %(excluded)s)' %
                {'hero_id': hero_info.id,
                 'spent_time': spent_time,
                 'is_normal': normal_mode,
                 'quest_type': quest_type,
                 'allowed': ', '.join(quest.quest_class.TYPE for quest in quests),
                 'excluded': ', '.join(excluded_quests)})

    return knowledge_base


def try_to_create_random_quest_for_hero(hero_info, quests, excluded_quests, without_restrictions, logger):

    for quest_type in quests:
        if quest_type.quest_class.TYPE in excluded_quests:
            continue

        try:
            return quest_type, _create_random_quest_for_hero(hero_info, start_quests=[quest_type.quest_class.TYPE], without_restrictions=without_restrictions)
        except questgen_exceptions.RollBackError, e:
            logger.info(u'hero[%(hero_id).6d]: can not create quest <%(quest_type)s>: %(exception)s' %
                        {'hero_id': hero_info.id,
                         'quest_type': quest_type,
                         'exception': e})
            continue

    return None, None


@retry_on_exception(max_retries=quests_settings.MAX_QUEST_GENERATION_RETRIES, exceptions=[questgen_exceptions.RollBackError])
def _create_random_quest_for_hero(hero_info, start_quests, without_restrictions=False):
    knowledge_base = get_knowledge_base(hero_info, without_restrictions=without_restrictions)

    selector = Selector(knowledge_base, QUESTS_BASE, social_connection_probability=c.QUESTS_SOCIAL_CONNECTIONS_FRACTION)

    hero_uid = uids.hero(hero_info.id)

    quests_facts = selector.create_quest_from_place(nesting=0,
                                                    initiator_position=selector.place_for(objects=(hero_uid,)),
                                                    allowed=start_quests,
                                                    excluded=[],
                                                    tags=('can_start', ))

    knowledge_base += quests_facts

    transformators.activate_events(knowledge_base) # TODO: after remove restricted states
    transformators.remove_restricted_states(knowledge_base)
    transformators.remove_broken_states(knowledge_base) # MUST be called after all graph changes
    transformators.determine_default_choices(knowledge_base, preferred_markers=hero_info.prefered_quest_markers) # MUST be called after all graph changes and on valid graph
    transformators.remove_unused_actors(knowledge_base)

    knowledge_base.validate_consistency(WORLD_RESTRICTIONS)
    knowledge_base.validate_consistency(QUEST_RESTRICTIONS)

    return knowledge_base


def create_hero_info(hero):
    quests_priorities = hero.get_quests_priorities()
    return HeroQuestInfo(id=hero.id,
                         level=hero.level,
                         position_place_id=hero.position.place.id,
                         is_first_quest_path_required=hero.is_first_quest_path_required,
                         is_short_quest_path_required=hero.is_short_quest_path_required,
                         preferences_mob_id=hero.preferences.mob.id if hero.preferences.mob else None,
                         preferences_place_id=hero.preferences.place.id if hero.preferences.place else None,
                         preferences_friend_id=hero.preferences.friend.id if hero.preferences.friend else None,
                         preferences_enemy_id=hero.preferences.enemy.id if hero.preferences.enemy else None,
                         preferences_equipment_slot=hero.preferences.equipment_slot,
                         interfered_persons=hero.quests.get_interfered_persons(),
                         quests_priorities=quests_priorities,
                         excluded_quests=hero.quests.excluded_quests(len(quests_priorities) / 2),
                         prefered_quest_markers=hero.prefered_quest_markers())

def request_quest_for_hero(hero):
    hero_info = create_hero_info(hero)
    amqp_environment.environment.workers.quests_generator.cmd_request_quest(hero.account_id, hero_info.serialize())


def setup_quest_for_hero(hero, knowledge_base_data):

    knowledge_base = KnowledgeBase.deserialize(knowledge_base_data, fact_classes=facts.FACTS)

    states_to_percents = analysers.percents_collector(knowledge_base)

    quest = QuestPrototype(hero=hero, knowledge_base=knowledge_base, states_to_percents=states_to_percents)

    if quest.machine.can_do_step():
        quest.machine.step() # do first step to setup pointer

    hero.actions.current_action.setup_quest(quest)
