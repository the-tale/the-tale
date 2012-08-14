# -*- coding: utf-8 -*-
import random

from dext.utils import s11n

from game.prototypes import TimePrototype

from game.balance import constants as c, formulas as f

from game.mobs.storage import MobsDatabase

from game.heroes.prototypes import HeroPrototype
from game.heroes.statistics import MONEY_SOURCE

from game.quests.models import Quest, QuestsHeroes
from game.quests.exceptions import QuestException

def get_quest_by_id(id):
    try:
        return QuestPrototype(model=Quest.objects.get(id=id))
    except Quest.DoesNotExist:
        return None

def get_quest_by_model(model):
    return QuestPrototype(model=model)


class QuestPrototype(object):

    def __init__(self, model, *argv, **kwargs):
        super(QuestPrototype, self).__init__(*argv, **kwargs)
        self.model = model

    @classmethod
    def get_for_hero(cls, hero_id):
        quests_models = list(QuestsHeroes.objects.filter(hero_id=hero_id))
        if len(quests_models) > 1:
            raise QuestException(u'more then one quest found fo hero: %d (quests: %r)' % (hero_id, [quest.id for quest in quests_models]))
        if quests_models:
            return cls(model=quests_models[0].quest)
        return None

    @property
    def id(self): return self.model.id

    @property
    def percents(self):
        return self.env.percents(self.pointer)

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
        return self._data

    @property
    def env(self):
        from .logic import get_knowlege_base
        from .environment import Environment
        from .quests_generator.lines import BaseQuestsSource
        from .writer import Writer

        if not hasattr(self, '_env'):
            self._env = Environment(quests_source=BaseQuestsSource(),
                                    writers_constructor=Writer,
                                    # TODO: REWRITE TO remove database requests and heroes data duplication
                                    knowlege_base=get_knowlege_base(hero=HeroPrototype.get_by_id(list(self.heroes_ids())[0])))
            self._env.deserialize(s11n.from_json(self.model.env))
        return self._env

    def get_pointer(self): return self.data['pointer']
    def set_pointer(self, value):  self.data['pointer'] = value
    pointer = property(get_pointer, set_pointer)

    def get_last_pointer(self): return self.data.get('last_pointer', self.pointer)
    def set_last_pointer(self, value):  self.data['last_pointer'] = value
    last_pointer = property(get_last_pointer, set_last_pointer)

    @property
    def line(self): return self.data['line']

    @property
    def is_processed(self):
        return len(self.pos) == 0

    def heroes_ids(self):
        return set(self.model.heroes.values_list('id', flat=True))

    def angels_ids(self):
        return set(self.model.heroes.values_list('angel_id', flat=True))


    def get_choices(self):
        # MUST be always actual
        choices = {}
        choices_list = list(self.model.choices.all())
        for choice in choices_list:
            choices[choice.choice_point] = choice.choice
        return choices

    def make_choice(self, choice_point, choice):
        from .models import QuestChoice

        if QuestChoice.objects.filter(quest=self.model, choice_point=choice_point).exists():
            return False

        QuestChoice.objects.create(quest=self.model,
                                   choice_point=choice_point,
                                   choice=choice)

        return True

    ###########################################
    # Object operations
    ###########################################

    def remove(self):
        self.model.delete()

    def save(self):
        self.model.data = s11n.to_json(self.data)
        self.model.env = s11n.to_json(self.env.serialize())
        self.model.save(force_update=True)

    @classmethod
    def create(cls, hero, env):

        data = { 'pointer': env.get_start_pointer(),
                 'last_pointer': env.get_start_pointer()}

        if QuestsHeroes.objects.filter(hero=hero.model).exists():
            raise Exception('Hero %s has already had quest' % hero.id)

        model = Quest.objects.create(env=s11n.to_json(env.serialize()),
                                     created_at_turn=TimePrototype.get_current_turn_number(),
                                     data=s11n.to_json(data))

        QuestsHeroes.objects.create(quest=model, hero=hero.model)

        quest = QuestPrototype(model=model)

        quest.save()

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

        if not cur_action.hero.can_change_persons_power:
            return

        for person_id, power in self.env.persons_power_points.items():
            person_data = self.env.persons[person_id]
            from ..workers.environment import workers_environment
            workers_environment.highlevel.cmd_change_person_power(person_data['external_data']['id'], power * 100)

    def process_current_command(self, cur_action):

        cmd = self.env.get_command(self.pointer)

        writer = self.env.get_writer(cur_action.hero, self.pointer)

        log_msg = writer.get_journal_msg(cmd.event)

        if log_msg:
            cur_action.hero.push_message(HeroPrototype._prepair_message(log_msg))

        {'description': self.cmd_description,
         'move': self.cmd_move,
         'movenear': self.cmd_move_near,
         'getitem': self.cmd_get_item,
         'giveitem': self.cmd_give_item,
         'getreward': self.cmd_get_reward,
         'quest': self.cmd_quest,
         'choose': self.cmd_choose,
         'givepower': self.cmd_give_power,
         'battle': self.cmd_battle
         }[cmd.type()](cmd, cur_action)

    def cmd_description(self, cmd, cur_action):
        cur_action.hero.push_message(HeroPrototype._prepair_message(cmd.msg))

    def cmd_move(self, cmd, cur_action):
        from ..actions.prototypes import ActionMoveToPrototype
        destination = self.env.get_game_place(cmd.place)
        ActionMoveToPrototype.create(parent=cur_action, destination=destination, break_at=cmd.break_at)

    def cmd_move_near(self, cmd, cur_action):
        from ..actions.prototypes import ActionMoveNearPlacePrototype
        destination = self.env.get_game_place(cmd.place)
        ActionMoveNearPlacePrototype.create(parent=cur_action, place=destination, back=cmd.back)

    def cmd_get_item(self, cmd, cur_action):
        item = self.env.get_game_item(cmd.item)
        cur_action.hero.put_loot(item)

    def cmd_give_item(self, cmd, cur_action):
        item = self.env.get_game_item(cmd.item)
        cur_action.hero.pop_quest_loot(item)

    def cmd_get_reward(self, cmd, cur_action):

        multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
        money = 1 + int(f.sell_artifact_price(cur_action.hero.level) * multiplier)
        money = cur_action.hero.abilities.update_quest_reward(cur_action.hero, money)
        cur_action.hero.change_money(MONEY_SOURCE.EARNED_FROM_QUESTS, money)
        cur_action.hero.add_message('action_quest_reward_money', important=True, hero=cur_action.hero, coins=money)

    def cmd_quest(self, cmd, cur_action):
        # TODO: move to quest generator environment
        pass

    def cmd_choose(self, cmd, cur_action):
        # TODO: move to quest generator environment
        pass

    def cmd_give_power(self, cmd, cur_action):
        # TODO: move to quest generator environment
        if cmd.depends_on:
            self.env.persons_power_points[cmd.person] = self.env.persons_power_points[cmd.depends_on] * cmd.multiply
        else:
            self.env.persons_power_points[cmd.person] = cmd.power

    def cmd_battle(self, cmd, cur_action):
        from ..actions.prototypes import ActionBattlePvE1x1Prototype

        mob = None
        if cmd.mob_id:
            mob = MobsDatabase.storage().get_mob(cur_action.hero, cmd.mob_id)
        if mob is None:
            mob = MobsDatabase.storage().get_random_mob(cur_action.hero)

        ActionBattlePvE1x1Prototype.create(parent=cur_action, mob=mob)

    def ui_info(self, hero):
        choices = self.get_choices()

        cmd = self.env.get_nearest_quest_choice(self.pointer)
        quest = self.env.get_quest(self.pointer)
        writer = self.env.get_writer(hero, self.pointer)

        cmd_id = None
        choice_variants = []
        future_choice = None

        if cmd:
            cmd_id = cmd.id
            if cmd.id not in choices:
                for variant in cmd.get_variants():
                    choice_variants.append((variant, writer.get_choice_variant_msg(cmd.choice, variant)))
            else:
                future_choice = writer.get_choice_result_msg(cmd.choice, choices[cmd.id])

        return {'line': self.env.get_writers_text_chain(hero, self.last_pointer),
                'choice_id': cmd_id,
                'choice_variants': choice_variants,
                'future_choice': future_choice,
                'id': self.model.id,
                'subquest_id': quest.id}
