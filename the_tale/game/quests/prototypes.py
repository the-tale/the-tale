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

    def get_percents(self): return self.base_model.percents
    def set_percents(self, value): self.base_model.percents = value
    percents = property(get_percents, set_percents)

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)
        return self._data

    @property
    def story(self):
        if not hasattr(self, '_story'):
            self._story = s11n.from_json(self.model.story)
        return self._story

    @property
    def env(self):
        from .environment import Environment
        if not hasattr(self, '_env'):
            self._env = Environment(data=s11n.from_json(self.model.env))
        return self._env

    @property
    def pos(self): return self.data['pos']

    @property
    def line(self): return self.data['line']

    def get_current_cmd(self):
        try:
            cmd = self.line['line'][self.pos[0]]
            
            for pos in self.pos[1:]:
                cmd = cmd['quest']['line'][pos]

            return cmd
        except IndexError:
            return None

    @property
    def is_processed(self):
        return len(self.pos) == 0

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self.model.delete()
    def save(self): 
        self.model.data = s11n.to_json(self.data)
        self.model.story = s11n.to_json(self.story)
        self.model.env = s11n.to_json(self.env.save_to_dict())
        self.model.save(force_update=True)

    def ui_info(self):
        return {'id': self.id}

    @classmethod
    @nested_commit_on_success
    def create(cls, hero, env, quest_line):

        env.sync()

        data = { 'pos': [0],
                 'line': quest_line.get_json() }

        model = Quest.objects.create(hero=hero.model,
                                     env=s11n.to_json(env.save_to_dict()),
                                     data=s11n.to_json(data))

        return QuestPrototype(model=model)

    def process(self, cur_action):
        
        if self.do_step(cur_action):
            return False, 0

        return True, 1

    def do_step(self, cur_action):
        
        self.process_current_command(cur_action)

        if self.increment_pos():
            return True

        return False
         

    def increment_pos(self):
        while self.pos:

            cmd = self.get_current_cmd()

            if cmd['type'] == 'quest': 
                self.pos.append(0)
            else:
                self.pos[-1] = self.pos[-1] + 1

            if self.get_current_cmd() is not None:
                return True

            self.pos.pop()


    def process_current_command(self, cur_action):

        cmd = self.get_current_cmd()

        {'description': self.cmd_description,
         'move': self.cmd_move,
         'getitem': self.cmd_get_item,
         'giveitem': self.cmd_give_item,
         'getreward': self.cmd_get_reward,
         'quest': self.cmd_quest
         }[cmd['type']](cmd, cur_action)

    def cmd_description(self, cmd, cur_action):
        cur_action.hero.create_tmp_log_message(cmd['msg'])

    def cmd_move(self, cmd, cur_action):
        from ..actions.prototypes import ActionMoveToPrototype
        destination = self.env.get_game_place(cmd['place'])
        ActionMoveToPrototype.create(parent=cur_action, destination=destination)

    def cmd_get_item(self, cmd, cur_action):
        item = self.env.get_game_item(cmd['item'])
        cur_action.hero.put_loot(item)

    def cmd_give_item(self, cmd, cur_action):
        item = self.env.get_game_item(cmd['item'])
        cur_action.hero.pop_quest_loot(item)

    def cmd_get_reward(self, cmd, cur_action):
        #TODO: implement
        cur_action.hero.create_tmp_log_message('hero get some reward [TODO: IMPLEMENT]')

    def cmd_quest(self, cmd, cur_action):
        cur_action.hero.create_tmp_log_message('do subquest')
