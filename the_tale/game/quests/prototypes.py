# coding: utf-8
import datetime
import random

from questgen.machine import Machine
from questgen import facts
from questgen.knowledge_base import KnowledgeBase

from game.prototypes import TimePrototype

from game.balance import constants as c, formulas as f

from game.mobs.storage import mobs_storage

from game.map.places.storage import places_storage
from game.map.roads.storage import waymarks_storage

from game.heroes.statistics import MONEY_SOURCE
from game.heroes.relations import EQUIPMENT_SLOT, ITEMS_OF_EXPENDITURE

from game.quests import exceptions


class QuestPrototype(object):

    def __init__(self, knowledge_base, rewards=None, quests_start_turn=None):
        self.rewards = {} if rewards is None else rewards
        self.quests_start_turn = {} if quests_start_turn is None else quests_start_turn

        # TODO:
        # quest.quests_start_turn[quest.env.root_quest.id] = model.created_at_turn
        # hero.quests_history[env.root_quest.type()] = TimePrototype.get_current_turn_number()

        self.knowledge_base = knowledge_base
        self.machine = Machine(knowledge_base=knowledge_base)

    def serialize(self):
        return {'rewards': self.rewards,
                'quests_start_turn': self.quests_start_turn,
                'knowledge_base': self.knowledge_base.serialize()}

    @classmethod
    def deserialize(cls, data):
        from game.quests.logic import RESTRICTIONS
        return cls(rewards=data['rewards'],
                   quests_start_turn=data['quests_start_turn'],
                   knowledge_base=KnowledgeBase.deserialize(data['knowledge_base'], restrictions=RESTRICTIONS, fact_classes=facts.FACTS))


    @property
    def percents(self): return 0.5 # TODO: implement

    @property
    def is_processed(self): return self.machine.is_processed

    def get_choices(self):
        # made choices
        # MUST be always actual
        return {} # TODO: implement

    def is_choice_available(self, choice): return False # TODO: implement


    def make_choice(self, choice_point, choice): return False # TODO: implement

    @classmethod
    def get_minimum_created_time_of_active_quests(cls): return datetime.datetime.fromtimestamp(0) # TODO: implement

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

        self.sync_knowledge_base(cur_action)

        if self.machine.can_do_step():
            self.do_state_actions(cur_action)
            self.machine.step()
            return True

        if self.is_processed:
            cur_action.hero.statistics.change_quests_done(1)
            return False

        self.satisfy_requirements(cur_action, self.machine.next_state)

        return True

    def sync_knowledge_base(self, cur_action):

        hero_uid = 'hero_%d' % cur_action.hero.id

        self.knowledge_base -= [location
                                for location in self.knowledge_base.filter(facts.LocatedIn)
                                if location.object == hero_uid]

        if cur_action.hero.position.place:
            self.knowledge_base += facts.LocatedIn(object=hero_uid, place='place_%d' % cur_action.hero.position.place.id)


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

    def satisfy_requirement(self, cur_action, requirement):
        if isinstance(requirement, facts.LocatedIn):
            # self.push_message(writer, cur_action.hero, cmd.event) # TODO: writer
            destination = places_storage[self.knowledge_base[requirement.place].externals['id']]
            self._move_hero_to(cur_action, destination)
        else:
            raise exceptions.UnknownRequirement(requirement=requirement)

    def do_state_actions(self, cur_action):
        pass # TODO: implement

    def push_message(self, writer, messanger, event, **kwargs):
        from game.heroes.messages import MessagesContainer

        if event is None:
            return

        diary_msg = writer.get_diary_msg(event, **kwargs)
        if diary_msg:
            messanger.messages.push_message(MessagesContainer._prepair_message(diary_msg))
            messanger.diary.push_message(MessagesContainer._prepair_message(diary_msg))
            return

        journal_msg = writer.get_journal_msg(event, **kwargs)
        if journal_msg:
            messanger.messages.push_message(MessagesContainer._prepair_message(journal_msg))


    def process_current_command(self, cur_action):

        cmd = self.env.get_command(self.pointer)

        writer = self.env.get_writer(cur_action.hero, self.pointer)

        {'message': self.cmd_message,
         'upgradeequipment': self.cmd_upgrade_equipment,
         'move': self.cmd_move,
         'movenear': self.cmd_move_near,
         'getitem': self.cmd_get_item,
         'giveitem': self.cmd_give_item,
         'getreward': self.cmd_get_reward,
         'quest': self.cmd_quest,
         'choose': self.cmd_choose,
         'switch': self.cmd_switch,
         'givepower': self.cmd_give_power,
         'battle': self.cmd_battle,
         'donothing': self.cmd_donothing,
         'questresult': self.cmd_questresult,
         }[cmd.type()](cmd, cur_action, writer)


    def cmd_message(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)


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


    def cmd_move(self, cmd, cur_action, writer):
        from game.actions.prototypes import ActionMoveToPrototype

        self.push_message(writer, cur_action.hero, cmd.event)

        destination = self.env.get_game_place(cmd.place)
        ActionMoveToPrototype.create(hero=cur_action.hero, destination=destination, break_at=cmd.break_at)

    def cmd_move_near(self, cmd, cur_action, writer):
        from game.actions.prototypes import ActionMoveNearPlacePrototype

        self.push_message(writer, cur_action.hero, cmd.event)

        destination = self.env.get_game_place(cmd.place)
        ActionMoveNearPlacePrototype.create(hero=cur_action.hero, place=destination, back=cmd.back)

    def cmd_get_item(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)
        item = self.env.get_game_item(cmd.item)
        cur_action.hero.put_loot(item)

    def cmd_give_item(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)
        item = self.env.get_game_item(cmd.item)
        cur_action.hero.pop_quest_loot(item)

    def cmd_get_reward(self, cmd, cur_action, writer):

        if cur_action.hero.can_get_artifact_for_quest():
            artifact, unequipped, sell_price = cur_action.hero.buy_artifact(better=False, with_prefered_slot=False, equip=False)# pylint: disable=W0612

            if artifact is not None:
                self.push_message(writer, cur_action.hero, '%s_artifact' % cmd.event, hero=cur_action.hero, artifact=artifact)
                return

        multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
        money = 1 + int(f.sell_artifact_price(cur_action.hero.level) * multiplier)
        money = cur_action.hero.abilities.update_quest_reward(cur_action.hero, money)
        cur_action.hero.change_money(MONEY_SOURCE.EARNED_FROM_QUESTS, money)
        self.push_message(writer, cur_action.hero, '%s_money' % cmd.event, hero=cur_action.hero, coins=money)

    def cmd_quest(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)
        self.quests_start_turn[cmd.quest] = TimePrototype.get_current_turn_number()

    def modify_experience(self, experience):
        from game.persons.storage import persons_storage

        experience_modifiers = {}
        # TODO:
        # here we go by all persons in quest chain
        # but MUST go only by persons in current_quest
        for person_data in self.env.persons.values():
            person = persons_storage.get(person_data['external_data']['id'])
            experience_modifiers[person.place.id] = person.place.get_experience_modifier()

        experience += experience * sum(experience_modifiers.values())
        return experience

    def cmd_questresult(self, cmd, cur_action, writer):

        self.push_message(writer, cur_action.hero, cmd.event)
        current_quest = self.env.get_quest(self.pointer)

        if current_quest.id not in self.env.quests_results:
            self.env.quests_results[current_quest.id] = {}

        self.env.quests_results[current_quest.id][cmd.result] = True

        if current_quest.id in self.rewards:
            experience = self.rewards[current_quest.id]['experience']
            experience = self.modify_experience(experience)
            cur_action.hero.add_experience(experience)


    def cmd_choose(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)

    def cmd_switch(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)

    @classmethod
    def modify_person_power(cls, person, quest_power, hero_modifier, base_power):
        return quest_power * hero_modifier * base_power * person.place.freedom

    def cmd_give_power(self, cmd, cur_action, writer):
        from game.persons.storage import persons_storage

        self.push_message(writer, cur_action.hero, cmd.event)

        current_quest = self.env.get_quest(self.pointer)
        if current_quest.id not in self.rewards:
            return # temporary code for old quests (without rewards dict)

        base_power = self.rewards[current_quest.id]['power']

        person_data = self.env.persons[cmd.person]
        person = persons_storage.get(person_data['external_data']['id'])

        power = self.modify_person_power(person, cmd.power, cur_action.hero.person_power_modifier, base_power)

        if power > 0:
            cur_action.hero.places_history.add_place(person.place_id)

        if not cur_action.hero.can_change_persons_power:
            return

        power = cur_action.hero.modify_person_power(person, power)

        person.cmd_change_power(power)


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
        choices = self.get_choices()

        cmd = self.env.get_nearest_quest_choice(self.last_pointer)
        writer = self.env.get_writer(hero, self.last_pointer)

        cmd_id = None
        choice_variants = []
        future_choice = None

        if cmd:
            cmd_id = cmd.id
            if cmd.id not in choices:
                for variant, line_id in cmd.choices.items():
                    line = self.env.lines[line_id]
                    choice_variants.append((variant if line.available else None,
                                            writer.get_choice_variant_msg(cmd.choice, variant)))
            else:
                future_choice = writer.get_choice_result_msg(cmd.choice, choices[cmd.id])

        return {'line': self.env.get_writers_text_chain(hero, self.last_pointer, self.rewards),
                'choice_id': cmd_id,
                'choice_variants': choice_variants,
                'future_choice': future_choice,
                'id': self._model.id}
