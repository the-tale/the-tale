# coding: utf-8
import math
import time
import random
import datetime
import itertools

from questgen.machine import Machine
from questgen import facts
from questgen.knowledge_base import KnowledgeBase
from questgen import transformators
from questgen.quests.base_quest import ROLES, RESULTS as QUEST_RESULTS
from questgen import relations as questgen_relations

from the_tale.game.prototypes import TimePrototype

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.map.places.storage import places_storage

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons.relations import PERSON_TYPE

from the_tale.game.heroes.relations import ITEMS_OF_EXPENDITURE, MONEY_SOURCE, HABIT_CHANGE_SOURCE

from the_tale.game.quests import exceptions
from the_tale.game.quests import writers
from the_tale.game.quests import relations
from the_tale.game.quests import uids

E = 0.001

class QuestInfo(object):
    __slots__ = ('type', 'uid', 'name', 'action', 'choice', 'choice_alternatives', 'experience', 'power', 'experience_bonus', 'power_bonus', 'actors', 'used_markers')

    def __init__(self, type, uid, name, action, choice, choice_alternatives, experience, power, actors, used_markers, experience_bonus=0, power_bonus=0,):
        self.type = type
        self.uid = uid
        self.name = name
        self.action = action
        self.choice = choice
        self.choice_alternatives = choice_alternatives
        self.experience = experience
        self.power = power
        self.experience_bonus = experience_bonus
        self.power_bonus = power_bonus
        self.actors = actors
        self.used_markers = used_markers

    @property
    def total_power(self):
        return self.power + self.power_bonus

    @property
    def total_experience(self):
        return self.experience + self.experience_bonus

    def serialize(self):
        return {'type': self.type,
                'uid': self.uid,
                'name': self.name,
                'action': self.action,
                'choice': self.choice,
                'choice_alternatives': self.choice_alternatives,
                'experience': self.experience,
                'power': self.power,
                'experience_bonus': self.experience_bonus,
                'power_bonus': self.power_bonus,
                'actors': self.actors,
                'used_markers': self.used_markers}

    def ui_info(self, hero):
        experience = int(self.experience * hero.experience_modifier) if hero is not None else self.experience # show experience modified by hero level and abilities
        power = int(self.power * hero.politics_power_multiplier()) if hero is not None else self.power # show power modified by hero level and abilities
        return {'type': self.type,
                'uid': self.uid,
                'name': self.name,
                'action': self.action,
                'choice': self.choice,
                'choice_alternatives': self.choice_alternatives,
                'experience': experience + self.experience_bonus,
                'power': power + self.power_bonus,
                'actors': self.actors_ui_info()}


    def prepair_actor_ui_info(self, role, actor_type):
        if role not in self.actors:
            return None

        actor_id, actor_name = self.actors[role]
        if actor_type.is_PLACE:
            return (actor_name, actor_type.value, {'id': actor_id,
                                                   'name': places_storage[actor_id].name})
        if actor_type.is_PERSON:
            return (actor_name, actor_type.value, persons_storage.persons_storage[actor_id].ui_info())
        if actor_type.is_MONEY_SPENDING:
            return (actor_name, actor_type.value, {'goal': actor_id.text,
                                                   'description': actor_id.description})

    def actors_ui_info(self):
        if self.type == 'no-quest':
            return []

        if self.type == 'next-spending':
            return [ self.prepair_actor_ui_info('goal', relations.ACTOR_TYPE.MONEY_SPENDING)  ]

        return filter(None, [ self.prepair_actor_ui_info(ROLES.INITIATOR, relations.ACTOR_TYPE.PERSON),
                              self.prepair_actor_ui_info(ROLES.INITIATOR_POSITION, relations.ACTOR_TYPE.PLACE),
                              self.prepair_actor_ui_info(ROLES.RECEIVER, relations.ACTOR_TYPE.PERSON),
                              self.prepair_actor_ui_info(ROLES.RECEIVER_POSITION, relations.ACTOR_TYPE.PLACE),
                              self.prepair_actor_ui_info(ROLES.ANTAGONIST, relations.ACTOR_TYPE.PERSON),
                              self.prepair_actor_ui_info(ROLES.ANTAGONIST_POSITION, relations.ACTOR_TYPE.PLACE)])

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @classmethod
    def construct(cls, type, uid, knowledge_base, hero):

        writer = writers.get_writer(hero=hero, type=type, message=None, substitution=cls.substitution(uid, knowledge_base, hero))

        actors = { participant.role: (knowledge_base[participant.participant].externals['id'], writer.actor(participant.role))
                   for participant in knowledge_base.filter(facts.QuestParticipant)
                   if participant.start == uid }

        return cls(type=type,
                   uid=uid,
                   name=writer.name(),
                   action=u'',
                   choice=None,
                   choice_alternatives=[],
                   experience=cls.get_expirience_for_quest(hero),
                   power=cls.get_person_power_for_quest(hero),
                   experience_bonus=0,
                   power_bonus=0,
                   actors=actors,
                   used_markers={})

    @classmethod
    def substitution(cls, uid, knowledge_base, hero):
        data = {'hero': hero}
        for participant in knowledge_base.filter(facts.QuestParticipant):
            if participant.start != uid:
                continue

            actor = knowledge_base[participant.participant]

            if isinstance(actor, facts.Person):
                person = persons_storage.persons_storage[actor.externals['id']]
                data[participant.role] = person
                data[participant.role + '_position'] = person.place
            elif isinstance(actor, facts.Place):
                data[participant.role] = places_storage[actor.externals['id']]

        return data

    def process_message(self, knowledge_base, hero, message, ext_substitution={}):

        substitution = self.substitution(self.uid, knowledge_base, hero)
        substitution.update(ext_substitution)

        writer = writers.get_writer(hero=hero, type=self.type, message=message, substitution=substitution)

        action_msg = writer.action()
        if action_msg:
            self.action = action_msg

        diary_msg = writer.diary()
        if diary_msg:
            hero.push_message(diary_msg, diary=True, journal=True)
            return

        journal_msg = writer.journal()
        if journal_msg:
            hero.push_message(journal_msg, diary=False, journal=True)

    def sync_choices(self, knowledge_base, hero, choice, options, defaults):

        if choice is None:
            self.choice = None
            self.choice_alternatives = ()
            return

        substitution = self.substitution(self.uid, knowledge_base, hero)
        writer = writers.get_writer(hero=hero, type=self.type, message='choice', substitution=substitution)

        choosen_option = knowledge_base[defaults[0].option]

        self.choice = writer.current_choice(choosen_option.type)

        if defaults[0].default:
            self.choice_alternatives = [(option.uid, writer.choice_variant(option.type))
                                        for option in options
                                        if option.uid != choosen_option.uid]
        else:
            self.choice_alternatives = ()

    @classmethod
    def get_expirience_for_quest(cls, hero):
        experience = f.experience_for_quest(c.QUEST_AREA_RADIUS)
        if hero.statistics.quests_done == 0:
            # since we get shortest path for first quest
            # and want to give exp as fast as can
            # and do not want to give more exp than level up required
            experience = int(experience/2)
        return experience

    @classmethod
    def get_person_power_for_quest(cls, hero):# pylint: disable=W0613
        return f.person_power_for_quest(c.QUEST_AREA_RADIUS)

    def get_real_reward_scale(self, hero, scale):

        scale *= hero.quest_money_reward_multiplier()

        markers_bonuses = hero.quest_markers_rewards_bonus()
        for marker in self.used_markers:
            scale += markers_bonuses.get(marker, 0)

        return scale



NO_QUEST_INFO__IN_PLACE = QuestInfo(type='no-quest',
                                    uid='no-quest',
                                    name=u'безделье',
                                    action=u'имитирует бурную деятельность',
                                    choice=None,
                                    choice_alternatives=(),
                                    experience=0,
                                    experience_bonus=0,
                                    power_bonus=0,
                                    power=0,
                                    actors={},
                                    used_markers=set())

NO_QUEST_INFO__OUT_PLACE = QuestInfo(type='no-quest',
                                     uid='no-quest',
                                     name=u'безделье',
                                     action=u'идёт в ближайший город',
                                     choice=None,
                                     choice_alternatives=(),
                                     experience=0,
                                     power=0,
                                     experience_bonus=0,
                                     power_bonus=0,
                                     actors={},
                                     used_markers=set())


class QuestPrototype(object):

    def __init__(self, knowledge_base, quests_stack=None, created_at=None, states_to_percents=None, hero=None):
        self.hero = hero
        self.quests_stack = [] if quests_stack is None else quests_stack
        self.knowledge_base = knowledge_base
        self.machine = Machine(knowledge_base=knowledge_base,
                               interpreter=self)
        self.created_at =datetime.datetime.now() if created_at is None else created_at
        self.states_to_percents = states_to_percents if states_to_percents is not None else {}

    @property
    def current_info(self):
        return self.quests_stack[-1]

    def serialize(self):
        return {'quests_stack': [info.serialize() for info in self.quests_stack],
                'knowledge_base': self.knowledge_base.serialize(short=True),
                'created_at': time.mktime(self.created_at.timetuple()),
                'states_to_percents': self.states_to_percents,}

    @classmethod
    def deserialize(cls, data):
        return cls(knowledge_base=KnowledgeBase.deserialize(data['knowledge_base'], fact_classes=facts.FACTS),
                   quests_stack=[QuestInfo.deserialize(info_data) for info_data in data['quests_stack']],
                   created_at=datetime.datetime.fromtimestamp(data['created_at']),
                   states_to_percents=data['states_to_percents'])

    @property
    def percents(self): return self.states_to_percents.get(self.machine.pointer.state, 0.0)

    @property
    def is_processed(self): return self.machine.is_processed

    def get_nearest_choice(self): return self.machine.get_nearest_choice()

    def make_choice(self, option_uid):
        choice, options, defaults = self.get_nearest_choice()

        if self.knowledge_base[option_uid].state_from != choice.uid:
            return False

        if not any(option.uid == option_uid for option in options):
            return False

        if not defaults[0].default:
            return False

        if not transformators.change_choice(knowledge_base=self.knowledge_base, new_option_uid=option_uid, default=False):
            return False

        self.machine.sync_pointer()

        if self.quests_stack:
            self.current_info.sync_choices(self.knowledge_base, self.hero, *self.get_nearest_choice())

        self.hero.actions.request_replane()
        return True

    ###########################################
    # Object operations
    ###########################################

    def process(self):
        self.hero.quests.mark_updated()

        step_result = self.machine.do_step()

        if self.quests_stack:
            self.current_info.sync_choices(self.knowledge_base, self.hero, *self.get_nearest_choice())

        if step_result:
            return self.percents

        return 1

    def _move_hero_to(self, destination, break_at=None):
        from the_tale.game.actions.prototypes import ActionMoveToPrototype

        if self.hero.position.is_walking:
            self._move_hero_near(destination=None, back=True)
            return

        ActionMoveToPrototype.create(hero=self.hero, destination=destination, break_at=break_at)


    def _move_hero_near(self, destination, terrains=None, back=False):
        from the_tale.game.actions.prototypes import ActionMoveNearPlacePrototype

        if destination is None:
            destination = self.hero.position.get_nearest_dominant_place()

        ActionMoveNearPlacePrototype.create(hero=self.hero, place=destination, back=back, terrains=terrains)


    def _move_hero_on_road(self, place_from, place_to, percents):

        if self.hero.position.is_walking:
            self._move_hero_near(destination=None, back=True)
            return

        path_to_position_length = self.hero.position.get_minumum_distance_to(place_from)
        path_from_position_length = self.hero.position.get_minumum_distance_to(place_to)

        full_path_length = path_to_position_length + path_from_position_length

        if path_to_position_length < E:
            current_percents = 0.0
        elif path_from_position_length < E:
            current_percents = 1.0
        else:
            current_percents = path_to_position_length / full_path_length

        if percents <= current_percents:
            return

        path_to_pass = (percents - current_percents) * full_path_length

        self._move_hero_to(destination=place_to, break_at=path_to_pass / path_from_position_length)


    def _give_power(self, hero, place, power):
        power = power * self.current_info.total_power

        if power > 0:
            hero.places_history.add_place(place.id)

        return power


    def _give_person_power(self, hero, person, power):

        power = self._give_power(hero, person.place, power)

        power, positive_bonus, negative_bonus = hero.modify_politics_power(power, person=person)

        person_uid = uids.person(person.id)
        has_profession_marker = [marker for marker in self.knowledge_base.filter(facts.ProfessionMarker) if marker.person == person_uid]
        if has_profession_marker:
            power /= len(PERSON_TYPE.records)
            positive_bonus /= len(PERSON_TYPE.records)
            negative_bonus /= len(PERSON_TYPE.records)

        if not hero.can_change_person_power(person):
            return 0

        person.cmd_change_power(power, positive_bonus, negative_bonus)

        return power


    def _give_place_power(self, hero, place, power):

        power = self._give_power(hero, place, power)

        power, positive_bonus, negative_bonus = hero.modify_politics_power(power, place=place)

        if not hero.can_change_place_power(place):
            return 0

        place.cmd_change_power(power, positive_bonus, negative_bonus)

        return power

    def _fight(self, action):
        from the_tale.game.actions.prototypes import ActionBattlePvE1x1Prototype

        if action.mob is not None:
            mob = mobs_storage[self.knowledge_base[action.mob].externals['id']].create_mob(self.hero, is_boss=True)
        else:
            mob = mobs_storage.get_random_mob(self.hero, mercenary=action.mercenary, is_boss=True)

            if mob is None:
                mobs_storage.get_random_mob(self.hero, is_boss=True)


        ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)

    def give_social_power(self, quest_results):
        results = {}

        for person_uid, result in quest_results.iteritems():
            person_id = self.knowledge_base[person_uid].externals['id']
            if person_id not in persons_storage.persons_storage:
                continue
            results[persons_storage.persons_storage[person_id]] = result

        VALUABLE_RESULTS = (QUEST_RESULTS.SUCCESSED, QUEST_RESULTS.FAILED)

        for (person_1, quest_1_result), (person_2, quest_2_result) in itertools.combinations(results.iteritems(), 2):

            if quest_1_result not in VALUABLE_RESULTS or quest_2_result not in VALUABLE_RESULTS:
                continue

            connection_type = persons_storage.social_connections.get_connection_type(person_1, person_2)

            if connection_type is None:
                continue

            if ( not ( (connection_type.is_PARTNER and quest_1_result == quest_2_result) or
                       (connection_type.is_CONCURRENT and quest_1_result != quest_2_result) ) ):
                continue

            self._give_person_power(hero=self.hero,
                                    person=person_1,
                                    power=1 if quest_1_result == QUEST_RESULTS.SUCCESSED else -1)

            self._give_person_power(hero=self.hero,
                                    person=person_2,
                                    power=1 if quest_2_result == QUEST_RESULTS.SUCCESSED else -1)



    def _finish_quest(self, finish, hero):

        experience = self.modify_experience(self.current_info.experience)
        experience_bonus = self.modify_experience(self.current_info.experience_bonus)

        hero.add_experience(experience)
        hero.add_experience(experience_bonus, without_modifications=True)

        hero.statistics.change_quests_done(1)

        if hero.companion:
            hero.companion.add_experience(c.COMPANIONS_COHERENCE_EXP_PER_QUEST)

        for person_uid, result in finish.results.iteritems():
            if result == QUEST_RESULTS.FAILED:
                hero.quests.add_interfered_person(self.knowledge_base[person_uid].externals['id'])

        for marker, default in self.current_info.used_markers.iteritems():
            for change_source in HABIT_CHANGE_SOURCE.records:
                if change_source.quest_marker == marker and change_source.quest_default == default:
                    self.hero.update_habits(change_source)

        self.give_social_power(finish.results)

        self.quests_stack.pop()


    def _give_reward(self, hero, reward_type, scale):

        quest_info = self.current_info

        scale = quest_info.get_real_reward_scale(hero, scale)

        if hero.can_get_artifact_for_quest():

            level_delta = int(math.ceil(abs(scale)))
            if scale < 0:
                level_delta = -level_delta

            artifact, unequipped, sell_price = self.hero.receive_artifact(equip=False, better=False, prefered_slot=False, prefered_item=False, archetype=False, level_delta=level_delta)

            if artifact is not None:
                quest_info.process_message(knowledge_base=self.knowledge_base,
                                           hero=self.hero,
                                           message='%s_artifact' % reward_type,
                                           ext_substitution={'artifact': artifact})
                return

        money = int(max(1, f.sell_artifact_price(hero.level) * scale))

        hero.change_money(MONEY_SOURCE.EARNED_FROM_QUESTS, money)

        quest_info.process_message(knowledge_base=self.knowledge_base,
                                   hero=self.hero,
                                   message='%s_money' % reward_type,
                                   ext_substitution={'coins': money})

    def _donothing(self, donothing_type):
        from the_tale.game.actions.prototypes import ActionDoNothingPrototype

        donothing = relations.DONOTHING_TYPE.index_value[donothing_type]

        writer = writers.get_writer(hero=self.hero, type=self.current_info.type, message=donothing_type, substitution={})

        ActionDoNothingPrototype.create(hero=self.hero,
                                        duration=donothing.duration,
                                        messages_prefix=writer.journal_id(),
                                        messages_probability=donothing.messages_probability)


    @classmethod
    def _get_upgrdade_choice(cls, hero):
        choices = [relations.UPGRADE_EQUIPMENT_VARIANTS.BUY]

        if hero.preferences.equipment_slot and hero.equipment.get(hero.preferences.equipment_slot) is not None:
            choices.append(relations.UPGRADE_EQUIPMENT_VARIANTS.SHARP)

            if hero.equipment.get(hero.preferences.equipment_slot).can_be_broken():
                choices.append(relations.UPGRADE_EQUIPMENT_VARIANTS.REPAIR)

        return random.choice(choices)

    @classmethod
    def upgrade_equipment_cost(cls, hero_info):
        return int(f.normal_action_price(hero_info.level) * ITEMS_OF_EXPENDITURE.get_quest_upgrade_equipment_fraction())

    @classmethod
    def _upgrade_equipment(cls, process_message, hero, knowledge_base, cost):

        if cost is not None:
            cost = min(cost, hero.money)

        upgrade_choice = cls._get_upgrdade_choice(hero)

        if upgrade_choice.is_BUY:
            artifact, unequipped, sell_price = hero.receive_artifact(equip=True, better=True, prefered_slot=True, prefered_item=True, archetype=True)

            if cost is not None:
                hero.change_money(MONEY_SOURCE.SPEND_FOR_ARTIFACTS, -cost)
                if artifact is None:
                    process_message(knowledge_base, hero, message='upgrade__fail', ext_substitution={'coins': cost})
                elif unequipped:
                    process_message(knowledge_base, hero, message='upgrade__buy_and_change', ext_substitution={'coins': cost,
                                                                                                               'artifact': artifact,
                                                                                                               'unequipped': unequipped,
                                                                                                               'sell_price': sell_price})
                else:
                    process_message(knowledge_base, hero, message='upgrade__buy', ext_substitution={'coins': cost,
                                                                                                    'artifact': artifact})
            else:
                if artifact is None:
                    process_message(knowledge_base, hero, message='upgrade_free__fail', ext_substitution={})
                elif unequipped:
                    process_message(knowledge_base, hero, message='upgrade_free__buy_and_change', ext_substitution={'artifact': artifact,
                                                                                                                    'unequipped': unequipped,
                                                                                                                    'sell_price': sell_price})
                else:
                    process_message(knowledge_base, hero, message='upgrade_free__buy', ext_substitution={'artifact': artifact})

        elif upgrade_choice.is_SHARP:
            artifact = hero.sharp_artifact()

            if cost is not None:
                hero.change_money(MONEY_SOURCE.SPEND_FOR_SHARPENING, -cost)
                process_message(knowledge_base, hero, message='upgrade__sharp', ext_substitution={'coins': cost,
                                                                                                  'artifact': artifact})
            else:
                process_message(knowledge_base, hero, message='upgrade_free__sharp', ext_substitution={'artifact': artifact})

        elif upgrade_choice.is_REPAIR:
            artifact = hero.repair_artifact()

            if cost is not None:
                hero.change_money(MONEY_SOURCE.SPEND_FOR_REPAIRING, -cost)
                process_message(knowledge_base, hero, message='upgrade__repair', ext_substitution={'coins': cost,
                                                                                                   'artifact': artifact})
            else:
                process_message(knowledge_base, hero, message='upgrade_free__repair', ext_substitution={'artifact': artifact})

        else:
            raise exceptions.UnknownUpgadeEquipmentTypeError(type=upgrade_choice)

    def _start_quest(self, start, hero):
        hero.quests.update_history(start.type, TimePrototype.get_current_turn_number())
        self.quests_stack.append(QuestInfo.construct(type=start.type,
                                                     uid=start.uid,
                                                     knowledge_base=self.machine.knowledge_base,
                                                     hero=hero))


    def modify_experience(self, experience):
        quest_uid = self.current_info.uid

        experience_modifiers = {}

        for participant in self.knowledge_base.filter(facts.QuestParticipant):
            if quest_uid != participant.start:
                continue
            fact = self.knowledge_base[participant.participant]
            if isinstance(fact, facts.Person):
                place = persons_storage.persons_storage.get(fact.externals['id']).place
            elif isinstance(fact, facts.Place):
                place = places_storage.get(fact.externals['id'])

            experience_modifiers[place.id] = place.get_experience_modifier()

        experience += experience * sum(experience_modifiers.values())
        return experience

    ################################
    # general callbacks
    ################################

    def on_state__before_actions(self, state):

        if isinstance(state, facts.Start):
            self._start_quest(state, hero=self.hero)

    def on_state__after_actions(self, state):
        if isinstance(state, facts.Finish):
            self._finish_quest(state, hero=self.hero)

    def on_jump_start__before_actions(self, jump):
        pass

    def on_jump_start__after_actions(self, jump):
        pass

    def on_jump_end__before_actions(self, jump):
        pass

    def on_jump_end__after_actions(self, jump):
        if not isinstance(jump, facts.Option):
            return

        path = (path for path in self.knowledge_base.filter(facts.ChoicePath) if path.option == jump.uid).next()

        used_markers = self.current_info.used_markers
        for marker in jump.markers:
            for markers_group in questgen_relations.OPTION_MARKERS_GROUPS:
                if marker not in markers_group:
                    continue

                for removed_marker in markers_group:
                    if removed_marker in used_markers:
                        del used_markers[removed_marker]

            used_markers[marker] = path.default


    ################################
    # do action callbacks
    ################################

    def do_message(self, action):
        self.current_info.process_message(self.knowledge_base, self.hero, action.type)

    def do_give_power(self, action):
        # every quest branch give equal power to its participants
        power = 0

        if action.power > 0:
            power = 1

        if action.power < 0:
            power = -1

        recipient = self.knowledge_base[action.object]
        if isinstance(recipient, facts.Person):
            self._give_person_power(self.hero, persons_storage.persons_storage[recipient.externals['id']], power)
        elif isinstance(recipient, facts.Place):
            self._give_place_power(self.hero, places_storage[recipient.externals['id']], power)
        else:
            raise exceptions.UnknownPowerRecipientError(recipient=recipient)

    def do_give_reward(self, action):
        self._give_reward(self.hero, action.type, action.scale)

    def do_fight(self, action):
        self._fight(action)

    def do_do_nothing(self, action):
        self._donothing(action.type)

    def do_upgrade_equipment(self, action):
        self._upgrade_equipment(self.current_info.process_message, self.hero, self.knowledge_base, cost=action.cost)

    def do_move_near(self, action):
        if action.place:
            self._move_hero_near(destination=places_storage.get(self.knowledge_base[action.place].externals['id']), terrains=action.terrains)
        else:
            self._move_hero_near(destination=None, terrains=action.terrains)

    ################################
    # check requirements callbacks
    ################################

    def check_located_in(self, requirement):
        object_fact = self.knowledge_base[requirement.object]
        place_fact = self.knowledge_base[requirement.place]

        place = places_storage[place_fact.externals['id']]

        if isinstance(object_fact, facts.Person):
            person = persons_storage.persons_storage[object_fact.externals['id']]
            return person.place.id == place.id

        if isinstance(object_fact, facts.Hero):
            return bool(self.hero.id == object_fact.externals['id'] and self.hero.position.place and self.hero.position.place.id == place.id)

        raise exceptions.UnknownRequirementError(requirement=requirement)


    def check_located_near(self, requirement):
        object_fact = self.knowledge_base[requirement.object]
        place_fact = self.knowledge_base[requirement.place]

        place = places_storage[place_fact.externals['id']]

        if isinstance(object_fact, facts.Person):
            return False

        if isinstance(object_fact, facts.Hero):
            if self.hero.id != object_fact.externals['id']:
                return False

            if self.hero.position.place:
                return False

            hero_place = self.hero.position.get_nearest_dominant_place()
            return place.id == hero_place.id

        raise exceptions.UnknownRequirementError(requirement=requirement)

    def check_located_on_road(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if isinstance(object_fact, facts.Person):
            return False

        if not isinstance(object_fact, facts.Hero):
            raise exceptions.UnknownRequirementError(requirement=requirement)

        if self.hero.id != object_fact.externals['id']:
            return False

        place_from = places_storage[self.knowledge_base[requirement.place_from].externals['id']]
        place_to = places_storage[self.knowledge_base[requirement.place_to].externals['id']]
        percents = requirement.percents

        path_to_position_length = self.hero.position.get_minumum_distance_to(place_from)
        path_from_position_length = self.hero.position.get_minumum_distance_to(place_to)

        full_path_length = path_to_position_length + path_from_position_length

        if path_to_position_length < E:
            current_percents = 0.0
        elif path_from_position_length < E:
            current_percents = 1.0
        else:
            current_percents = path_to_position_length / full_path_length

        return current_percents >= percents


    def check_has_money(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if isinstance(object_fact, facts.Person):
            return False

        if isinstance(object_fact, facts.Hero):
            if self.hero.id != object_fact.externals['id']:
                return False
            return self.hero.money >= requirement.money

        raise exceptions.UnknownRequirementError(requirement=requirement)

    def check_is_alive(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if isinstance(object_fact, facts.Person):
            return True

        if isinstance(object_fact, facts.Hero):
            if self.hero.id != object_fact.externals['id']:
                return False

            return self.hero.is_alive

        raise exceptions.UnknownRequirementError(requirement=requirement)

    ################################
    # satisfy requirements callbacks
    ################################

    def satisfy_located_in(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if not isinstance(object_fact, facts.Hero) or self.hero.id != object_fact.externals['id']:
            raise exceptions.UnknownRequirementError(requirement=requirement)

        self._move_hero_to(destination=places_storage[self.knowledge_base[requirement.place].externals['id']])

    def satisfy_located_near(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if not isinstance(object_fact, facts.Hero) or self.hero.id != object_fact.externals['id']:
            raise exceptions.UnknownRequirementError(requirement=requirement)

        if requirement.place is None:
            self._move_hero_near(destination=None, terrains=requirement.terrains)
        else:
            self._move_hero_near(destination=places_storage.get(self.knowledge_base[requirement.place].externals['id']), terrains=requirement.terrains)

    def satisfy_located_on_road(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if not isinstance(object_fact, facts.Hero) or self.hero.id != object_fact.externals['id']:
            raise exceptions.UnknownRequirementError(requirement=requirement)

        self._move_hero_on_road(place_from=places_storage[self.knowledge_base[requirement.place_from].externals['id']],
                                place_to=places_storage[self.knowledge_base[requirement.place_to].externals['id']],
                                percents=requirement.percents)

    def satisfy_has_money(self, requirement):
        raise exceptions.UnknownRequirementError(requirement=requirement)

    def satisfy_is_alive(self, requirement):
        raise exceptions.UnknownRequirementError(requirement=requirement)


    ################################
    # ui info
    ################################

    def ui_info(self):
        return {'line': [info.ui_info(self.hero) for info in self.quests_stack]}

    @classmethod
    def no_quests_ui_info(cls, in_place):
        if in_place:
            return {'line': [NO_QUEST_INFO__IN_PLACE.ui_info(None)]}
        else:
            return {'line': [NO_QUEST_INFO__OUT_PLACE.ui_info(None)]}

    @classmethod
    def next_spending_ui_info(cls, spending):
        NEXT_SPENDING_INFO = QuestInfo(type='next-spending',
                                       uid='next-spending',
                                       name=u'Накопить золото',
                                       action=u'копит',
                                       choice=None,
                                       choice_alternatives=(),
                                       experience=0,
                                       power=0,
                                       experience_bonus=0,
                                       power_bonus=0,
                                       actors={'goal': (spending, u'цель')},
                                       used_markers=set())
        return {'line': [NEXT_SPENDING_INFO.ui_info(None)]}
