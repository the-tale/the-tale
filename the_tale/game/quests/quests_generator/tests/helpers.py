# coding: utf-8

from game.quests.quests_generator.quest_line import Quest, Line
from game.quests.quests_generator import commands as cmd

class FakeWriter(object):

    def __init__(self, hero, quest_type, env, env_local):
        self.hero = hero
        self.quest_type = quest_type
        self.env = env
        self.env_local = env_local

    def get_description_msg(self):
        return '%s_%s' % (self.hero, self.quest_type)

    def get_action_msg(self, event):
        return '%s_%s_%s' % (self.hero, self.quest_type, event)


class FakeCmd(cmd.Command): pass


class FakeLine(Line):

    def get_quest_command(self, env, pointer):
        return FakeCmd('fake_event'), []

class FakeQuest(Quest):

    def __init__(self, commands_number):
        super(FakeQuest, self).__init__()
        self.commands_number = commands_number

    def initialize(self, identifier, env, **kwargs):
        pass

    def create_line(self, env):
        self.line = env.new_line(FakeLine())

    def get_commands_number(self, env, pointer=None):
        if pointer:
            return pointer[0]
        return self.commands_number

    def increment_pointer(self, env, pointer, choices):
        next_poiner = list(pointer)
        if pointer[-1] < self.commands_number - 1:
            next_poiner[-1] += 1
            return next_poiner

        return None


class JustQuest(Quest):

    def initialize(self, identifier, env, **kwargs):
        super(JustQuest, self).initialize(identifier, env, **kwargs)
        self.env_local.register('quest_1', 'quest_1')

    def create_line(self, env):
        linear_line = Line(sequence=[cmd.Move(event='event_1_1', place='place_1'),
                                     cmd.MoveNear(event='event_1_2', place='place_1', back=False),
                                     cmd.MoveNear(event='event_1_3', place='place_1', back=True),
                                     cmd.GetItem(event='event_1_4', item='item_1'),
                                     cmd.GiveItem(event='event_1_5', item='item_1'),
                                     cmd.Battle(event='event_1_6', number=13),
                                     cmd.GetReward(event='event_1_7', person='person_1'),
                                     cmd.GivePower(event='event_1_8', person='person_1', power=2, multiply=3, depends_on='person_2')  ])

        quest_line = Line(sequence=[cmd.Move(event='event_2_1', place='place_2'),
                                    cmd.Quest(event='event_2_2', quest=self.env_local.quest_1),
                                    cmd.GetReward(event='event_2_3', person='person_2')  ])

        main_line = Line(sequence=[cmd.Move(event='event_3_1', place='place_3'),
                                   cmd.Choose(id='choose_1',
                                              default='choice_1',
                                              choices={'choice_1': env.new_line(linear_line),
                                                       'choice_2': env.new_line(quest_line) },
                                              event='event_3_2',
                                              choice='choice_id_1'),
                                   cmd.Battle(event='event_3_3', number=13) ])
        self.line = env.new_line(main_line)
