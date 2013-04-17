# coding: utf-8
import datetime
import random

from dext.utils import s11n

from common.utils.prototypes import BasePrototype

from game.prototypes import TimePrototype

from game.balance import constants as c, formulas as f

from game.mobs.storage import mobs_storage

from game.heroes.prototypes import HeroPrototype
from game.heroes.statistics import MONEY_SOURCE

from game.quests.models import Quest, QuestsHeroes
from game.quests.exceptions import QuestException


class QuestPrototype(BasePrototype):
    _model_class = Quest
    _readonly = ('id',)
    _bidirectional = ()
    _get_by = ('id',)

    @classmethod
    def get_for_hero(cls, hero_id):
        # use select_related to get quest_hero & quest model in one request
        # since can be situation, when we get QuestsHeroes model just before quest removing
        quests_models = list(QuestsHeroes.objects.select_related().filter(hero_id=hero_id))
        if len(quests_models) > 1:
            raise QuestException(u'more then one quest found fo hero: %d (quests: %r)' % (hero_id, [quest.id for quest in quests_models]))
        if quests_models:
            return cls(model=quests_models[0].quest)
        return None

    @property
    def percents(self):
        return self.env.percents(self.pointer)

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self._model.data)
        return self._data

    @property
    def env(self):
        from .environment import Environment
        from .logic import QuestsSource
        from .writer import Writer

        if not hasattr(self, '_env'):

            self._env = Environment(writers_constructor=Writer,
                                    quests_source=QuestsSource() )
            self._env.deserialize(s11n.from_json(self._model.env))
        return self._env

    def get_pointer(self): return self.data['pointer']
    def set_pointer(self, value):  self.data['pointer'] = value
    pointer = property(get_pointer, set_pointer)

    def get_last_pointer(self): return self.data.get('last_pointer', self.pointer)
    def set_last_pointer(self, value):  self.data['last_pointer'] = value
    last_pointer = property(get_last_pointer, set_last_pointer)

    def get_quests_start_turn(self):
        if 'quests_start_turn'not in self.data:
            self.data['quests_start_turn'] = {}
        return self.data['quests_start_turn']
    def set_quests_start_turn(self, value):  self.data['quests_start_turn'] = value
    quests_start_turn = property(get_quests_start_turn, set_quests_start_turn)

    @property
    def line(self): return self.data['line']

    @property
    def is_processed(self):
        return len(self.pos) == 0

    def get_choices(self):
        # MUST be always actual
        choices = {}
        choices_list = list(self._model.choices.all())
        for choice in choices_list:
            choices[choice.choice_point] = choice.choice
        return choices

    def is_choice_available(self, choice):
        return self.env.lines[choice].available

    def make_choice(self, choice_point, choice):
        from game.quests.models import QuestChoice

        if QuestChoice.objects.filter(quest=self._model, choice_point=choice_point).exists():
            return False

        QuestChoice.objects.create(quest=self._model,
                                   choice_point=choice_point,
                                   choice=choice)

        return True

    @classmethod
    def get_minimum_created_time_of_active_quests(self):
        from django.db.models import Min
        created_at = Quest.objects.all().aggregate(Min('created_at'))['created_at__min']

        return created_at if created_at is not None else datetime.datetime.now()

    ###########################################
    # Object operations
    ###########################################

    def remove(self):
        self._model.delete()

    def save(self):
        self._model.data = s11n.to_json(self.data)
        self._model.env = s11n.to_json(self.env.serialize())
        self._model.save(force_update=True)

    @classmethod
    def create(cls, hero, env):

        data = { 'pointer': env.get_start_pointer(),
                 'last_pointer': env.get_start_pointer()}

        if QuestsHeroes.objects.filter(hero=hero._model).exists():
            raise Exception('Hero %s has already had quest' % hero.id)

        model = Quest.objects.create(env=s11n.to_json(env.serialize()),
                                     created_at_turn=TimePrototype.get_current_turn_number(),
                                     data=s11n.to_json(data))

        QuestsHeroes.objects.create(quest=model, hero=hero._model)

        quest = QuestPrototype(model=model)

        quest.quests_start_turn[quest.env.root_quest.id] = model.created_at_turn

        quest.save()

        hero.quests_history[env.root_quest.type()] = TimePrototype.get_current_turn_number()

        return quest


    def process(self, cur_action):

        if self.do_step(cur_action):
            percents = self.percents
            if percents >= 1:
                raise QuestException('completed percents > 1 for not ended quest')
            return percents

        return 1

    def do_step(self, cur_action):

        self.process_current_command(cur_action)

        self.last_pointer = self.pointer
        self.pointer = self.env.increment_pointer(self.pointer, self.get_choices())

        if self.pointer is not None:
            return True

        self.end_quest(cur_action)
        cur_action.hero.statistics.change_quests_done(1)

        return False

    def end_quest(self, cur_action):
        from game.persons.storage import persons_storage

        if not cur_action.hero.can_change_persons_power:
            return

        for person_id, power in self.env.persons_power_points.items():
            person_data = self.env.persons[person_id]
            person = persons_storage.get(person_data['external_data']['id'])
            power = cur_action.hero.modify_person_power(person, power)
            person.cmd_change_power(power)

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

        if cur_action.hero.equipment.get(cmd.equipment_slot) is not None:
            choices.append('sharp')

        money_spend = cur_action.hero.money

        if random.choice(choices) == 'buy':
            cur_action.hero.change_money(MONEY_SOURCE.SPEND_FOR_ARTIFACTS, -money_spend)
            artifact, unequipped, sell_price = cur_action.hero.buy_artifact(better=True)

            if artifact is None:
                self.push_message(writer, cur_action.hero, '%_fail' % cmd.event,
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
        from ..actions.prototypes import ActionMoveToPrototype

        self.push_message(writer, cur_action.hero, cmd.event)

        destination = self.env.get_game_place(cmd.place)
        ActionMoveToPrototype.create(parent=cur_action, destination=destination, break_at=cmd.break_at)

    def cmd_move_near(self, cmd, cur_action, writer):
        from ..actions.prototypes import ActionMoveNearPlacePrototype

        self.push_message(writer, cur_action.hero, cmd.event)

        destination = self.env.get_game_place(cmd.place)
        ActionMoveNearPlacePrototype.create(parent=cur_action, place=destination, back=cmd.back)

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
            artifact, unequipped, sell_price = cur_action.hero.buy_artifact(equip=False)

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

    def cmd_questresult(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)
        current_quest = self.env.get_quest(self.pointer)

        if current_quest.id not in self.env.quests_results:
            self.env.quests_results[current_quest.id] = {}

        self.env.quests_results[current_quest.id][cmd.result] = True

    def cmd_choose(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)

    def cmd_switch(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)

    def cmd_give_power(self, cmd, cur_action, writer):
        self.push_message(writer, cur_action.hero, cmd.event)
        current_quest_id = self.env.get_quest(self.pointer).id
        quest_start_turn = self.quests_start_turn.get(current_quest_id)
        if quest_start_turn is None:
            return # temporary code for old quests (without all quests start turns)
        real_power = f.person_power_from_quest(cmd.power, cur_action.hero.level, TimePrototype.get_current_turn_number() - quest_start_turn)

        self.env.persons_power_points[cmd.person] = self.env.persons_power_points.get(cmd.person, 0) + real_power

    def cmd_battle(self, cmd, cur_action, writer):
        from ..actions.prototypes import ActionBattlePvE1x1Prototype

        self.push_message(writer, cur_action.hero, cmd.event)

        mob = None
        if cmd.mob_id:
            mob = mobs_storage.get_by_uuid(cmd.mob_id).create_mob(cur_action.hero)
        if mob is None:
            mob = mobs_storage.get_random_mob(cur_action.hero)

        ActionBattlePvE1x1Prototype.create(parent=cur_action, mob=mob)

    def cmd_donothing(self, cmd, cur_action, writer):
        from ..actions.prototypes import ActionDoNothingPrototype
        self.push_message(writer, cur_action.hero, cmd.event)
        ActionDoNothingPrototype.create(parent=cur_action,
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

        return {'line': self.env.get_writers_text_chain(hero, self.last_pointer),
                'choice_id': cmd_id,
                'choice_variants': choice_variants,
                'future_choice': future_choice,
                'id': self._model.id}
