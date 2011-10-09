# -*- coding: utf-8 -*-
from django_next.utils import s11n

from django_next.utils.decorators import nested_commit_on_success

from . import writers
from .models import Quest

def get_quest_by_model(model):
    return QuestPrototype(model=model)

class QuestPrototype(object):

    def __init__(self, model, *argv, **kwargs):
        super(QuestPrototype, self).__init__(*argv, **kwargs)
        self.model = model
        self.cmd_number = 0

    @property
    def id(self): return self.model.id

    def get_cmd_number(self): return self.model.cmd_number
    def set_cmd_number(self, value): self.model.cmd_number = value
    cmd_number = property(get_cmd_number, set_cmd_number)

    @property
    def percents(self):
        return float(self.cmd_number) / self.data['line']['sequence_len']

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

    @property
    def ui_line(self): 
        if not 'ui_line' in self.data:
            self.data['ui_line'] = []
        return self.data['ui_line']

    def get_current_cmd(self):
        try:
            cmd = self.line['line'][self.pos[0]]
            
            for pos in self.pos[1:]:
                cmd = cmd['quest']['line'][pos]

            return cmd
        except IndexError:
            return None

    def get_current_writer(self):

        try:
            cmd = self.line['line'][self.pos[0]]

            writer = writers.WRITERS[self.line['writer']](self.env, self.line['env'])
            
            for pos in self.pos[1:]:
                writer = writers.WRITERS[cmd['quest']['writer']](self.env, cmd['quest']['env'])
                cmd = cmd['quest']['line'][pos]

            return writer
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

    @classmethod
    @nested_commit_on_success
    def create(cls, hero, env, quest_line):

        env.sync()

        line_dict = quest_line.get_json()

        data = { 'pos': [0],
                 'ui_line': [None],
                 'line':  line_dict}

        model = Quest.objects.create(hero=hero.model,
                                     env=s11n.to_json(env.save_to_dict()),
                                     data=s11n.to_json(data))

        quest = QuestPrototype(model=model)

        #TODO: move to creation fase (remove save operation)
        writer = quest.get_current_writer()
        quest_msg = writer.get_action_msg('quest_description')

        quest.ui_line[-1] = {'quest_msg': quest_msg,
                             'quest_type': writer.QUEST_TYPE,
                             'action_msg': '',
                             'action_type': ''}
        quest.save()
        return quest


    def process(self, cur_action):
        
        if self.do_step(cur_action):
            return False, self.percents

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

            while self.pos and self.get_current_cmd() is None:
                self.pos.pop()

                if len(self.pos):
                    self.pos[-1] = self.pos[-1] + 1

            if self.get_current_cmd() is not None:
                self.cmd_number += 1
                return True


    def process_current_command(self, cur_action):

        cmd = self.get_current_cmd()

        writer = self.get_current_writer()
        log_msg = writer.get_log_msg(cmd['event'])
        action_msg = writer.get_action_msg(cmd['event'])
        quest_msg = writer.get_action_msg('quest_description')

        if log_msg:
            cur_action.hero.create_tmp_log_message(log_msg)

        if len(self.pos) > len(self.ui_line):
            self.ui_line.append({})

        self.ui_line[-1] = {'quest_msg': quest_msg,
                            'quest_type': writer.QUEST_TYPE,
                            'action_msg': action_msg,
                            'action_type': cmd['event']}

        while len(self.pos) < len(self.ui_line):
            self.ui_line.pop()

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
        cur_action.bundle.add_action(ActionMoveToPrototype.create(parent=cur_action, destination=destination))

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
        pass

    def ui_info(self):
        return {'percents': self.percents,
                'line': self.ui_line}
