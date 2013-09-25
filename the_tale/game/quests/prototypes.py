# coding: utf-8
import time
import datetime
import random

from questgen.machine import Machine
from questgen import facts
from questgen.knowledge_base import KnowledgeBase
from questgen import transformators

from game.prototypes import TimePrototype

from game.balance import constants as c, formulas as f

from game.mobs.storage import mobs_storage

from game.map.places.storage import places_storage
from game.map.roads.storage import waymarks_storage
from game.persons.storage import persons_storage

from game.heroes.statistics import MONEY_SOURCE
from game.heroes.relations import EQUIPMENT_SLOT, ITEMS_OF_EXPENDITURE

from game.quests import exceptions
from game.quests import uids
from game.quests.writer import Writer


class QuestInfo(object):

    def __init__(self, type, uid, name, action, choice, choice_alternatives):
        self.type = type
        self.uid = uid
        self.name = name
        self.action = action
        self.choice = choice
        self.choice_alternatives = choice_alternatives

    def serialize(self):
        return {'type': self.type,
                'uid': self.uid,
                'name': self.name,
                'action': self.action,
                'choice': self.choice,
                'choice_alternatives': self.choice_alternatives}

    def ui_info(self):
        return {'type': self.type,
                'uid': self.uid,
                'name': self.name,
                'action': self.action,
                'choice': self.choice,
                'choice_alternatives': self.choice_alternatives}

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @classmethod
    def construct(cls, type, uid, knowledge_base, hero):

        writer = Writer(type=type, message=None, substitution=cls.substitution(uid, knowledge_base, hero))

        return cls(type=type,
                   uid=uid,
                   name=writer.name(),
                   action=u'',
                   choice=None,
                   choice_alternatives=[])

    @classmethod
    def prepair_participant(cls, actor):
        if isinstance(actor, facts.Person):
            return persons_storage[actor.externals['id']]
        elif isinstance(actor, facts.Place):
            return places_storage[actor.externals['id']]

    @classmethod
    def substitution(cls, uid, knowledge_base, hero):
        data = { participant.role: cls.prepair_participant(knowledge_base[participant.participant])
                 for participant in knowledge_base.filter(facts.QuestParticipant)
                 if participant.start == uid }
        data['hero'] = hero
        return data

    def process_message(self, knowledge_base, hero, message):
        from game.heroes.messages import MessagesContainer

        substitution = self.substitution(self.uid, knowledge_base, hero)
        writer = Writer(type=self.type, message=message, substitution=substitution)

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
        writer = Writer(type=self.type, message='choice', substitution=substitution)

        choosen_option = knowledge_base[defaults[0].option]

        self.choice = writer.current_choice(choosen_option.type)
        self.choice_alternatives = [(option.type, writer.choice_variant(option.type))
                                    for option in options
                                    if option.type != choosen_option.type]



class QuestPrototype(object):

    def __init__(self, knowledge_base, rewards=None, quests_stack=None, created_at=None, replane_required=False, states_to_percents=None):
        self.rewards = {} if rewards is None else rewards
        self.quests_stack = [] if quests_stack is None else quests_stack
        self.knowledge_base = knowledge_base
        self.machine = Machine(knowledge_base=knowledge_base)
        self.created_at =datetime.datetime.now() if created_at is None else created_at
        self.replane_required = replane_required
        self.states_to_percents = states_to_percents if states_to_percents is not None else {}

    def serialize(self):
        return {'rewards': self.rewards,
                'quests_stack': [info.serialize() for info in self.quests_stack],
                'knowledge_base': self.knowledge_base.serialize(),
                'created_at': time.mktime(self.created_at.timetuple()),
                'replane_required': self.replane_required,
                'states_to_percents': self.states_to_percents}

    @classmethod
    def deserialize(cls, data):
        return cls(rewards=data['rewards'],
                   knowledge_base=KnowledgeBase.deserialize(data['knowledge_base'], fact_classes=facts.FACTS),
                   quests_stack=[QuestInfo.deserialize(info_data) for info_data in data['quests_stack']],
                   created_at=datetime.datetime.fromtimestamp(data['created_at']),
                   replane_required=data['replane_required'],
                   states_to_percents=data['states_to_percents'])

    @property
    def percents(self): return self.states_to_percents.get(self.machine.pointer.state, 0.0)

    @property
    def is_processed(self): return self.machine.is_processed

    def get_nearest_choice(self): return self.machine.get_nearest_choice()

    def make_choice(self, choice_uid, option_uid):
        choice, options, defaults = self.get_nearest_choice()

        if choice_uid != choice.uid:
            return False

        if not any(option.uid == option_uid for option in options):
            return False

        if not defaults[0].default:
            return False

        if not transformators.change_choice(knowledge_base=self.knowledge_base, choice_uid=choice_uid, new_option_uid=option_uid, default=False):
            return False

        self.machine.sync_pointer()

        self.replane_required = True
        return True

    ###########################################
    # Object operations
    ###########################################

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

    def process(self, cur_action):
        if self.do_step(cur_action):
            return self.percents

        return 1

    def do_step(self, cur_action):
        self.replane_required = False

        cur_action.hero.quests.updated = True

        if self.quests_stack:
            self.quests_stack[-1].sync_choices(self.knowledge_base, cur_action.hero, *self.get_nearest_choice())

        self.sync_knowledge_base(cur_action)

        if self.machine.can_do_step():
            self.machine.step()
            self.do_state_actions(cur_action)
            return True

        if self.is_processed:
            cur_action.hero.statistics.change_quests_done(1)
            return False

        self.satisfy_requirements(cur_action, self.machine.next_state)

        return True

    def sync_knowledge_base(self, cur_action):

        hero_uid = uids.hero(cur_action.hero)

        self.knowledge_base -= [location
                                for location in self.knowledge_base.filter(facts.LocatedIn)
                                if location.object == hero_uid]

        if cur_action.hero.position.place:
            self.knowledge_base += facts.LocatedIn(object=hero_uid, place=uids.place(cur_action.hero.position.place))


    def satisfy_requirements(self, cur_action, state):
        for requirement in state.require:
            if not requirement.check(self.knowledge_base):
                self.satisfy_requirement(cur_action, requirement)

    def _move_hero_to(self, cur_action, destination):
        from game.actions.prototypes import ActionMoveToPrototype, ActionMoveNearPlacePrototype

        if cur_action.hero.position.place or cur_action.hero.position.road:
            ActionMoveToPrototype.create(hero=cur_action.hero, destination=destination)
        else:
            ActionMoveNearPlacePrototype.create(hero=cur_action.hero, place=cur_action.hero.get_dominant_place(), back=True)

    def _give_power(self, hero, person_id, power):
        from game.persons.storage import persons_storage

        # self.push_message(writer, cur_action.hero, cmd.event)
        current_quest_uid = self.quests_stack[-1].uid

        base_power = self.rewards[current_quest_uid]['power']

        person = persons_storage[person_id]

        power = self.modify_person_power(person, power, hero.person_power_modifier, base_power)

        if power > 0:
            hero.places_history.add_place(person.place_id)

        if not hero.can_change_persons_power:
            return

        power = hero.modify_person_power(person, power)

        person.cmd_change_power(power)

    def _finish_quest(self, hero):
        # self.push_message(writer, cur_action.hero, cmd.event)

        current_quest_uid = self.quests_stack[-1].uid

        experience = self.rewards[current_quest_uid]['experience']
        experience = self.modify_experience(experience)
        hero.add_experience(experience)

        self._give_reward(hero)

        self.quests_stack.pop()

    def _give_reward(self, hero): # TODO: test

        if hero.can_get_artifact_for_quest():
            artifact, unequipped, sell_price = hero.buy_artifact(better=False, with_prefered_slot=False, equip=False)# pylint: disable=W0612

            if artifact is not None:
                # self.push_message(writer, cur_action.hero, '%s_artifact' % cmd.event, hero=cur_action.hero, artifact=artifact)
                return

        multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
        money = 1 + int(f.sell_artifact_price(hero.level) * multiplier)
        money = hero.abilities.update_quest_reward(hero, money)
        hero.change_money(MONEY_SOURCE.EARNED_FROM_QUESTS, money)
        # self.push_message(writer, cur_action.hero, '%s_money' % cmd.event, hero=cur_action.hero, coins=money)


    def _start_quest(self, hero):
        start = self.machine.current_state
        hero.quests_history[start.type] = TimePrototype.get_current_turn_number()
        self.quests_stack.append(QuestInfo.construct(type=start.type,
                                                     uid=start.uid,
                                                     knowledge_base=self.machine.knowledge_base,
                                                     hero=hero))

    def satisfy_requirement(self, cur_action, requirement):
        if isinstance(requirement, facts.LocatedIn):
            destination = places_storage[self.knowledge_base[requirement.place].externals['id']]
            self._move_hero_to(cur_action, destination)
        else:
            raise exceptions.UnknownRequirement(requirement=requirement)

    def do_state_actions(self, cur_action):
        current_state = self.machine.current_state

        if isinstance(current_state, facts.Start):
            self._start_quest(hero=cur_action.hero)

        for action in current_state.actions:
            if isinstance(action, facts.Message):
                self.quests_stack[-1].process_message(self.knowledge_base, cur_action.hero, action.id)
            elif isinstance(action, facts.GivePower):
                self._give_power(cur_action.hero, self.knowledge_base[action.person].externals['id'], action.power)

        if isinstance(current_state, facts.Finish):
            self._finish_quest(hero=cur_action.hero)

    def cmd_upgrade_equipment(self, cmd, cur_action, writer):

        choices = ['buy']

        if cmd.equipment_slot in EQUIPMENT_SLOT._index_value: # this check is for old equipment ids, we should skip them
            if cur_action.hero.equipment.get(EQUIPMENT_SLOT(cmd.equipment_slot)) is not None:
                choices.append('sharp')

        # limit money spend
        money_spend = min(cur_action.hero.money,
                          f.normal_action_price(cur_action.hero.level) * ITEMS_OF_EXPENDITURE.get_quest_upgrade_equipment_fraction())

        if random.choice(choices) == 'buy':
            cur_action.hero.change_money(MONEY_SOURCE.SPEND_FOR_ARTIFACTS, -money_spend)
            artifact, unequipped, sell_price = cur_action.hero.buy_artifact(better=True, with_prefered_slot=True, equip=True)

            if artifact is None:
                self.push_message(writer, cur_action.hero, '%s_fail' % cmd.event,
                                  coins=money_spend)
            elif unequipped:
                self.push_message(writer, cur_action.hero, '%s_buy_and_change' % cmd.event,
                                  coins=money_spend, artifact=artifact, unequipped=unequipped, sell_price=sell_price)
            else:
                self.push_message(writer, cur_action.hero, '%s_buy' % cmd.event,
                                  coins=money_spend, artifact=artifact)
        else:
            cur_action.hero.change_money(MONEY_SOURCE.SPEND_FOR_SHARPENING, -money_spend)
            artifact = cur_action.hero.sharp_artifact()
            self.push_message(writer, cur_action.hero, '%s_sharp' % cmd.event,
                              coins=money_spend, artifact=artifact)

    def modify_experience(self, experience):
        from game.persons.storage import persons_storage

        experience_modifiers = {}
        # TODO:
        # here we go by all persons in quest chain
        # but MUST go only by persons in current_quest
        for person in self.knowledge_base.filter(facts.Person):
            person = persons_storage.get(person.externals['id'])
            experience_modifiers[person.place.id] = person.place.get_experience_modifier()

        experience += experience * sum(experience_modifiers.values())
        return experience

    def cmd_switch(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)

    @classmethod
    def modify_person_power(cls, person, quest_power, hero_modifier, base_power):
        return quest_power * hero_modifier * base_power * person.place.freedom

    def cmd_battle(self, cmd, cur_action, writer):
        from game.actions.prototypes import ActionBattlePvE1x1Prototype

        self.push_message(writer, cur_action.hero, cmd.event)

        mob = None
        if cmd.mob_id:
            mob = mobs_storage.get_by_uuid(cmd.mob_id).create_mob(cur_action.hero)
        if mob is None:
            mob = mobs_storage.get_random_mob(cur_action.hero)

        ActionBattlePvE1x1Prototype.create(hero=cur_action.hero, mob=mob)

    def cmd_donothing(self, cmd, cur_action, writer):
        from ..actions.prototypes import ActionDoNothingPrototype
        self.push_message(writer, cur_action.hero, cmd.event)
        ActionDoNothingPrototype.create(hero=cur_action.hero,
                                        duration=cmd.duration,
                                        messages_prefix=writer.get_msg_journal_id(cmd.event),
                                        messages_probability=cmd.messages_probability)

    def ui_info(self, hero):
        return {'line': [info.ui_info() for info in self.quests_stack]}
