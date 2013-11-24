# coding: utf-8
import time
import datetime
import random

from questgen.machine import Machine
from questgen import facts
from questgen.knowledge_base import KnowledgeBase
from questgen import transformators
from questgen.quests.base_quest import ROLES, RESULTS as QUEST_RESULTS

from the_tale.game.prototypes import TimePrototype

from the_tale.game.balance import constants as c, formulas as f

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import waymarks_storage
from the_tale.game.persons.storage import persons_storage

from the_tale.game.heroes.relations import ITEMS_OF_EXPENDITURE, MONEY_SOURCE

from the_tale.game.quests import exceptions
from the_tale.game.quests import uids
from the_tale.game.quests import writers
from the_tale.game.quests.relations import ACTOR_TYPE, DONOTHING_TYPE


# from django.utils.log import getLogger
# logger = getLogger('the-tale.workers.game_logic')


class QuestInfo(object):
    __slots__ = ('type', 'uid', 'name', 'action', 'choice', 'choice_alternatives', 'experience', 'power', 'actors')

    def __init__(self, type, uid, name, action, choice, choice_alternatives, experience, power, actors):
        self.type = type
        self.uid = uid
        self.name = name
        self.action = action
        self.choice = choice
        self.choice_alternatives = choice_alternatives
        self.experience = experience
        self.power = power
        self.actors = actors

    def serialize(self):
        return {'type': self.type,
                'uid': self.uid,
                'name': self.name,
                'action': self.action,
                'choice': self.choice,
                'choice_alternatives': self.choice_alternatives,
                'experience': self.experience,
                'power': self.power,
                'actors': self.actors}

    def ui_info(self, hero):
        return {'type': self.type,
                'uid': self.uid,
                'name': self.name,
                'action': self.action,
                'choice': self.choice,
                'choice_alternatives': self.choice_alternatives,
                'experience': int(self.experience * hero.experience_modifier) if hero is not None else self.experience,# show experience modified by hero level and abilities
                'power': int(self.power * hero.person_power_modifier) if hero is not None else self.power, # show power modified by hero level and abilities
                'actors': self.actors_ui_info()}


    def prepair_actor_ui_info(self, role, actor_type):
        if role not in self.actors:
            return None

        actor_id, actor_name = self.actors[role]
        if actor_type._is_PLACE:
            return (actor_name, actor_type.value, {'id': actor_id})
        if actor_type._is_PERSON:
            return (actor_name, actor_type.value, persons_storage[actor_id].ui_info())
        if actor_type._is_MONEY_SPENDING:
            return (actor_name, actor_type.value, {'goal': actor_id.text,
                                                   'description': actor_id.description})

    def actors_ui_info(self):
        if self.type == 'no-quest':
            return []

        if self.type == 'next-spending':
            return [ self.prepair_actor_ui_info('goal', ACTOR_TYPE.MONEY_SPENDING)  ]

        return filter(None, [ self.prepair_actor_ui_info(ROLES.INITIATOR, ACTOR_TYPE.PERSON),
                              self.prepair_actor_ui_info(ROLES.INITIATOR_POSITION, ACTOR_TYPE.PLACE),
                              self.prepair_actor_ui_info(ROLES.RECEIVER, ACTOR_TYPE.PERSON),
                              self.prepair_actor_ui_info(ROLES.RECEIVER_POSITION, ACTOR_TYPE.PLACE),
                              self.prepair_actor_ui_info(ROLES.ANTAGONIST, ACTOR_TYPE.PERSON),
                              self.prepair_actor_ui_info(ROLES.ANTAGONIST_POSITION, ACTOR_TYPE.PLACE)])

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @classmethod
    def construct(cls, type, uid, knowledge_base, hero):

        writer = writers.get_writer(type=type, message=None, substitution=cls.substitution(uid, knowledge_base, hero))

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
                   actors=actors)

    @classmethod
    def substitution(cls, uid, knowledge_base, hero):
        data = {'hero': hero}
        for participant in knowledge_base.filter(facts.QuestParticipant):
            if participant.start != uid:
                continue

            actor = knowledge_base[participant.participant]

            if isinstance(actor, facts.Person):
                person = persons_storage[actor.externals['id']]
                data[participant.role] = person
                data[participant.role + '_position'] = person.place
            elif isinstance(actor, facts.Place):
                data[participant.role] = places_storage[actor.externals['id']]

        return data

    def process_message(self, knowledge_base, hero, message, ext_substitution={}):
        from the_tale.game.heroes.messages import MessagesContainer

        substitution = self.substitution(self.uid, knowledge_base, hero)
        substitution.update(ext_substitution)

        writer = writers.get_writer(type=self.type, message=message, substitution=substitution)

        action_msg = writer.action()
        if action_msg:
            self.action = action_msg

        diary_msg = writer.diary()
        if diary_msg:
            hero.messages.push_message(MessagesContainer._prepair_message(diary_msg))
            hero.diary.push_message(MessagesContainer._prepair_message(diary_msg))
            return

        journal_msg = writer.journal()
        if journal_msg:
            hero.messages.push_message(MessagesContainer._prepair_message(journal_msg))

    def sync_choices(self, knowledge_base, hero, choice, options, defaults):

        if choice is None:
            self.choice = None
            self.choice_alternatives = ()
            return

        substitution = self.substitution(self.uid, knowledge_base, hero)
        writer = writers.get_writer(type=self.type, message='choice', substitution=substitution)

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
        experience = f.experience_for_quest(waymarks_storage.average_path_length)
        if hero.statistics.quests_done == 0:
            # since we get shortest path for first quest
            # and want to give exp as fast as can
            # and do not want to give more exp than level up required
            experience = int(experience/2)
        return experience

    @classmethod
    def get_person_power_for_quest(cls, hero):# pylint: disable=W0613
        return f.person_power_for_quest(waymarks_storage.average_path_length)


NO_QUEST_INFO__IN_PLACE = QuestInfo(type='no-quest',
                                    uid='no-quest',
                                    name=u'безделие',
                                    action=u'имитирует бурную деятельность',
                                    choice=None,
                                    choice_alternatives=(),
                                    experience=None,
                                    power=None,
                                    actors={})

NO_QUEST_INFO__OUT_PLACE = QuestInfo(type='no-quest',
                                     uid='no-quest',
                                     name=u'безделие',
                                     action=u'идёт в ближайший город',
                                     choice=None,
                                     choice_alternatives=(),
                                     experience=None,
                                     power=None,
                                     actors={})


class QuestPrototype(object):

    def __init__(self, hero, knowledge_base, quests_stack=None, created_at=None, states_to_percents=None):
        self.hero = hero
        self.quests_stack = [] if quests_stack is None else quests_stack
        self.knowledge_base = knowledge_base
        self.machine = Machine(knowledge_base=knowledge_base,
                               on_state=self.on_state,
                               on_jump_start=self.on_jump_start,
                               on_jump_end=self.on_jump_end)
        self.created_at =datetime.datetime.now() if created_at is None else created_at
        self.states_to_percents = states_to_percents if states_to_percents is not None else {}

    def serialize(self):
        return {'quests_stack': [info.serialize() for info in self.quests_stack],
                'knowledge_base': self.knowledge_base.serialize(short=True),
                'created_at': time.mktime(self.created_at.timetuple()),
                'states_to_percents': self.states_to_percents,}

    @classmethod
    def deserialize(cls, hero, data):
        return cls(knowledge_base=KnowledgeBase.deserialize(data['knowledge_base'], fact_classes=facts.FACTS),
                   quests_stack=[QuestInfo.deserialize(info_data) for info_data in data['quests_stack']],
                   created_at=datetime.datetime.fromtimestamp(data['created_at']),
                   states_to_percents=data['states_to_percents'],
                   hero=hero)

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
            self.quests_stack[-1].sync_choices(self.knowledge_base, self.hero, *self.get_nearest_choice())

        self.hero.actions.request_replane()
        return True

    ###########################################
    # Object operations
    ###########################################

    def process(self):
        step_result = self.do_step()

        if self.quests_stack:
            self.quests_stack[-1].sync_choices(self.knowledge_base, self.hero, *self.get_nearest_choice())

        if step_result:
            return self.percents

        return 1

    def do_step(self):

        self.hero.quests.updated = True

        self.sync_knowledge_base()

        if self.machine.can_do_step():
            self.machine.step()
            return True

        if self.machine.next_state:
            self.satisfy_requirements(self.machine.next_state)

        return True

    def sync_knowledge_base(self):

        hero_uid = uids.hero(self.hero)

        self.knowledge_base -= [location
                                for location in self.knowledge_base.filter(facts.LocatedIn)
                                if location.object == hero_uid]

        self.knowledge_base -= [location
                                for location in self.knowledge_base.filter(facts.LocatedNear)
                                if location.object == hero_uid]

        self.knowledge_base -= [has_money
                                for has_money in self.knowledge_base.filter(facts.HasMoney)
                                if has_money.object == hero_uid]

        self.knowledge_base -= [is_alive
                                for is_alive in self.knowledge_base.filter(facts.IsAlive)
                                if is_alive.object == hero_uid]

        if self.hero.is_alive:
            self.knowledge_base += facts.IsAlive(object=hero_uid)

        if self.hero.position.place:
            self.knowledge_base += facts.LocatedIn(object=hero_uid, place=uids.place(self.hero.position.place))
        else:
            place = self.hero.position.get_nearest_dominant_place()
            self.knowledge_base += facts.LocatedNear(object=hero_uid, place=uids.place(place))

        self.knowledge_base += facts.HasMoney(object=hero_uid, money=self.hero.money)

        # logger.warn(u'%r' % self.machine.pointer)
        # logger.warn(u'%r' % ( [is_alive
        #                        for is_alive in self.knowledge_base.filter(facts.IsAlive)
        #                        if is_alive.object == hero_uid], ) )


    def satisfy_requirements(self, state):
        for requirement in state.require:
            if not requirement.check(self.knowledge_base):
                self.satisfy_requirement(requirement)


    def _move_hero_to(self, destination_uid, break_at=None):
        from the_tale.game.actions.prototypes import ActionMoveToPrototype, ActionMoveNearPlacePrototype

        if destination_uid:
            destination = places_storage[self.knowledge_base[destination_uid].externals['id']]
        else:
            destination = self.hero.position.get_nearest_dominant_place()

        if self.hero.position.place or self.hero.position.road:
            ActionMoveToPrototype.create(hero=self.hero, destination=destination, break_at=break_at)
        else:
            place = self.hero.position.get_nearest_dominant_place()
            ActionMoveNearPlacePrototype.create(hero=self.hero, place=place, back=True)


    def _move_hero_near(self, destination_uid, terrains=None):
        from the_tale.game.actions.prototypes import ActionMoveNearPlacePrototype

        if destination_uid:
            destination = places_storage[self.knowledge_base[destination_uid].externals['id']]
        else:
            destination = self.hero.position.get_nearest_dominant_place()

        ActionMoveNearPlacePrototype.create(hero=self.hero, place=destination, back=False, terrains=terrains)


    def _move_hero_on_road(self, place_1_uid, place_2_uid):
        pass


    def _give_power(self, hero, place, power):
        power = power * self.quests_stack[-1].power

        if power > 0:
            hero.places_history.add_place(place.id)

        return power


    def _give_person_power(self, hero, person, power):

        power = self._give_power(hero, person.place, power)

        power = hero.modify_power(power, person=person)

        if not hero.can_change_persons_power:
            return 0

        person.cmd_change_power(power)


    def _give_place_power(self, hero, place, power):

        power = self._give_power(hero, place, power)

        power = hero.modify_power(power, place=place)

        if not hero.can_change_persons_power:
            return 0

        place.cmd_change_power(power)


    def _fight(self, action):
        from the_tale.game.actions.prototypes import ActionBattlePvE1x1Prototype

        if action.mob is not None:
            mob = mobs_storage[self.knowledge_base[action.mob].externals['id']].create_mob(self.hero)
        else:
            mob = mobs_storage.get_random_mob(self.hero, mercenary=action.mercenary)

            if mob is None:
                mobs_storage.get_random_mob(self.hero)


        ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)


    def _finish_quest(self, finish, hero):

        experience = self.quests_stack[-1].experience
        experience = self.modify_experience(experience)

        hero.add_experience(experience)

        hero.statistics.change_quests_done(1)

        for person_uid, result in finish.results.iteritems():
            if result == QUEST_RESULTS.FAILED:
                hero.quests.add_interfered_person(self.knowledge_base[person_uid].externals['id'])

        self.quests_stack.pop()


    def _give_reward(self, hero, reward_type, scale):

        quest_info = self.quests_stack[-1]

        if hero.can_get_artifact_for_quest():
            artifact, unequipped, sell_price = hero.buy_artifact(better=False, with_prefered_slot=False, equip=False)# pylint: disable=W0612

            if artifact is not None:
                artifact.power += int((scale - 1.0) * c.POWER_TO_LVL)
                quest_info.process_message(knowledge_base=self.knowledge_base,
                                           hero=self.hero,
                                           message='%s_artifact' % reward_type,
                                           ext_substitution={'artifact': artifact})
                return

        multiplier = (1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)) * scale
        money = 1 + int(f.sell_artifact_price(hero.level) * multiplier)
        money = hero.abilities.update_quest_reward(hero, money)
        hero.change_money(MONEY_SOURCE.EARNED_FROM_QUESTS, money)

        quest_info.process_message(knowledge_base=self.knowledge_base,
                                   hero=self.hero,
                                   message='%s_money' % reward_type,
                                   ext_substitution={'coins': money})

    def _donothing(self, donothing_type):
        from the_tale.game.actions.prototypes import ActionDoNothingPrototype

        donothing = DONOTHING_TYPE._index_value[donothing_type]

        writer = writers.get_writer(type=self.quests_stack[-1].type, message=donothing_type, substitution={})

        ActionDoNothingPrototype.create(hero=self.hero,
                                        duration=donothing.duration,
                                        messages_prefix=writer.journal_id(),
                                        messages_probability=donothing.messages_probability)


    @classmethod
    def _get_upgrdade_choice(cls, hero):
        choices = ['buy']

        if hero.preferences.equipment_slot and hero.equipment.get(hero.preferences.equipment_slot) is not None:
            choices.append('sharp')

        return random.choice(choices)

    @classmethod
    def upgrade_equipment_cost(cls, hero):
        return int(f.normal_action_price(hero.level) * ITEMS_OF_EXPENDITURE.get_quest_upgrade_equipment_fraction())

    @classmethod
    def _upgrade_equipment(cls, process_message, hero, knowledge_base, cost):

        if cost is not None:
            cost = min(cost, hero.money)

        if cls._get_upgrdade_choice(hero) == 'buy':
            artifact, unequipped, sell_price = hero.buy_artifact(better=True, with_prefered_slot=True, equip=True)

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

        else:
            artifact = hero.sharp_artifact()

            if cost is not None:
                hero.change_money(MONEY_SOURCE.SPEND_FOR_SHARPENING, -cost)
                process_message(knowledge_base, hero, message='upgrade__sharp', ext_substitution={'coins': cost,
                                                                                                  'artifact': artifact})
            else:
                process_message(knowledge_base, hero, message='upgrade_free__sharp', ext_substitution={'artifact': artifact})

    def _start_quest(self, start, hero):
        hero.quests.update_history(start.type, TimePrototype.get_current_turn_number())
        self.quests_stack.append(QuestInfo.construct(type=start.type,
                                                     uid=start.uid,
                                                     knowledge_base=self.machine.knowledge_base,
                                                     hero=hero))

    def satisfy_requirement(self, requirement):
        if isinstance(requirement, facts.LocatedIn):
            self._move_hero_to(requirement.place)
        elif isinstance(requirement, facts.LocatedNear):
            self._move_hero_near(requirement.place, terrains=requirement.terrains)
        elif isinstance(requirement, facts.LocatedOnRoad):
            self._move_hero_on_road(requirement.place_1, requirement.place_2)
        else:
            raise exceptions.UnknownRequirement(requirement=requirement)

    def on_state(self, state):

        if isinstance(state, facts.Start):
            self._start_quest(state, hero=self.hero)

        self._do_actions(state.actions)

        if isinstance(state, facts.Finish):
            self._finish_quest(state, hero=self.hero)

    def on_jump_start(self, jump):
        self._do_actions(jump.start_actions)

    def on_jump_end(self, jump):
        self._do_actions(jump.end_actions)

    def _do_actions(self, actions):
        for action in actions:
            if isinstance(action, facts.Message):
                self.quests_stack[-1].process_message(self.knowledge_base, self.hero, action.type)
            elif isinstance(action, facts.GivePower):
                recipient = self.knowledge_base[action.object]
                if isinstance(recipient, facts.Person):
                    self._give_person_power(self.hero, persons_storage[recipient.externals['id']], action.power)
                elif isinstance(recipient, facts.Place):
                    self._give_place_power(self.hero, places_storage[recipient.externals['id']], action.power)
                else:
                    raise exceptions.UnknownPowerRecipient(recipient=recipient)
            elif isinstance(action, facts.GiveReward):
                self._give_reward(self.hero, action.type, action.scale)
            elif isinstance(action, facts.Fight):
                self._fight(action)
            elif isinstance(action, facts.MoveNear):
                self._move_hero_near(action.place, terrains=action.terrains)
            elif isinstance(action, facts.MoveIn):
                self._move_hero_to(action.place, break_at=action.percents)
            elif isinstance(action, facts.DoNothing):
                self._donothing(action.type)
            elif isinstance(action, facts.UpgradeEquipment):
                self._upgrade_equipment(self.quests_stack[-1].process_message, self.hero, self.knowledge_base, cost=action.cost)
            else:
                raise exceptions.UnknownAction(action=action)

    def modify_experience(self, experience):
        from the_tale.game.persons.storage import persons_storage

        quest_uid = self.quests_stack[-1].uid

        experience_modifiers = {}

        for participant in self.knowledge_base.filter(facts.QuestParticipant):
            if quest_uid != participant.start:
                continue
            fact = self.knowledge_base[participant.participant]
            if isinstance(fact, facts.Person):
                place = persons_storage.get(fact.externals['id']).place
            elif isinstance(fact, facts.Place):
                place = places_storage.get(fact.externals['id'])

            experience_modifiers[place.id] = place.get_experience_modifier()

        experience += experience * sum(experience_modifiers.values())
        return experience

    def cmd_switch(self, cmd, writer):
        self.push_message(writer, self.hero, cmd.event)

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
                                       experience=None,
                                       power=None,
                                       actors={'goal': (spending, u'цель')})
        return {'line': [NEXT_SPENDING_INFO.ui_info(None)]}
