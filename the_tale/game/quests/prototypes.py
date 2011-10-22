# -*- coding: utf-8 -*-
from django_next.utils import s11n

from django_next.utils.decorators import nested_commit_on_success

from .models import Quest

def get_quest_by_model(model):
    return QuestPrototype(model=model)


class QuestPrototype(object):

    def __init__(self, model, *argv, **kwargs):
        super(QuestPrototype, self).__init__(*argv, **kwargs)
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def percents(self): return self.env.percents

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
        return self._data

    @property
    def env(self):
        from .environment import Environment
        from .quests_generator.lines import BaseQuestsSource, BaseWritersSouece

        if not hasattr(self, '_env'):
            self._env = Environment(quests_source=BaseQuestsSource(),
                                    writers_source=BaseWritersSouece())
            self._env.deserialize(s11n.from_json(self.model.env))
        return self._env

    @property
    def pointer(self): return self.data['pointer']

    @property
    def line(self): return self.data['line']

    @property
    def ui_line(self): 
        if not 'ui_line' in self.data:
            self.data['ui_line'] = []
        return self.data['ui_line']

    @property
    def is_processed(self):
        return len(self.pos) == 0

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self.model.delete()
    def save(self): 
        self.model.data = s11n.to_json(self.data)
        self.model.env = s11n.to_json(self.env.serialize())
        self.model.save(force_update=True)

    @classmethod
    @nested_commit_on_success
    def create(cls, hero, env):

        env.sync()

        data = { 'pointer': env.get_start_pointer() }

        if Quest.objects.filter(hero=hero.model).exists():
            raise Exception('Hero %s has already had quest' % hero.id)

        model = Quest.objects.create(hero=hero.model,
                                     env=s11n.to_json(env.serialize()),
                                     data=s11n.to_json(data))

        quest = QuestPrototype(model=model)

        quest.save()

        return quest


    def process(self, cur_action):
        
        if self.do_step(cur_action):
            return False, self.percents

        return True, 1

    def do_step(self, cur_action):
        
        self.process_current_command(cur_action)

        self.pointer = self.env.increment_pointer(self.pointer)
        if self.pointer is not None:
            return True

        return False
         
    def process_current_command(self, cur_action):

        cmd = self.env.get_command(self.pointer)
        writer = self.env.get_writer(self.pointer)

        log_msg = writer.get_log_msg(cmd.event)

        if log_msg:
            cur_action.hero.create_tmp_log_message(log_msg)

        {'description': self.cmd_description,
         'move': self.cmd_move,
         'getitem': self.cmd_get_item,
         'giveitem': self.cmd_give_item,
         'getreward': self.cmd_get_reward,
         'quest': self.cmd_quest
         }[cmd.type()](cmd, cur_action)

    def cmd_description(self, cmd, cur_action):
        cur_action.hero.create_tmp_log_message(cmd.msg)

    def cmd_move(self, cmd, cur_action):
        from ..actions.prototypes import ActionMoveToPrototype
        destination = self.env.get_game_place(cmd.place)
        cur_action.bundle.add_action(ActionMoveToPrototype.create(parent=cur_action, destination=destination))

    def cmd_get_item(self, cmd, cur_action):
        item = self.env.get_game_item(cmd.item)
        cur_action.hero.put_loot(item)

    def cmd_give_item(self, cmd, cur_action):
        item = self.env.get_game_item(cmd.item)
        cur_action.hero.pop_quest_loot(item)

    def cmd_get_reward(self, cmd, cur_action):
        #TODO: implement
        cur_action.hero.create_tmp_log_message('hero get some reward [TODO: IMPLEMENT]')

    def cmd_quest(self, cmd, cur_action):
        pass

    def ui_info(self):
        return {'line': self.env.get_writers_text_chain(self.pointer)}
