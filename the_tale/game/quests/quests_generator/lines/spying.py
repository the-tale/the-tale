# coding: utf-8
from ..quest_line import Quest, Line
from ..writer import Writer
from .. import commands as cmd

class EVENTS:
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    MOVE_NEAR = 'move_near'
    GET_REWARD = 'get_reward'

    GOOD_GIVE_POWER = 'good_give_power'
    BAD_GIVE_POWER = 'bad_give_power'

    OPEN_UP_CHOICE = 'open_up_choice'

class CHOICES:
    OPEN_UP = 'open_up'

class SpyingLine(Quest):

    def initialize(self, identifier, env, **kwargs):
        super(SpyingLine, self).initialize(identifier, env, **kwargs)
        self.env_local.register('choose_point_1', env.new_choice_point())
        self.env_local.register('choose_point_2', env.new_choice_point())

    def create_line(self, env):

        bad_line_1 = Line(sequence=[ cmd.MoveNear(place=self.env_local.place_end, back=True, event=EVENTS.MOVE_NEAR),
                                     cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                     cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                     cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.BAD_GIVE_POWER)])

        bad_line_2 = Line(sequence=[cmd.MoveNear(place=self.env_local.place_end, back=True, event=EVENTS.MOVE_NEAR),
                                    cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.BAD_GIVE_POWER)])

        good_line_2 = Line(sequence=[cmd.MoveNear(place=self.env_local.place_end, back=True, event=EVENTS.MOVE_NEAR),
                                     cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                     cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GOOD_GIVE_POWER),
                                     cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.GOOD_GIVE_POWER)])

        good_line_1 = Line(sequence=[cmd.MoveNear(place=self.env_local.place_end, event=EVENTS.MOVE_NEAR),
                                     cmd.Choose(id=self.env_local.choose_point_2,
                                                default='spy',
                                                choices={'spy': env.new_line(good_line_2),
                                                         'open_up': env.new_line(bad_line_2)},
                                                event=EVENTS.OPEN_UP_CHOICE,
                                                choice=CHOICES.OPEN_UP) ])
       
        main_line = Line(sequence=[cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST),
                                   cmd.Choose(id=self.env_local.choose_point_1,
                                              default='spy',
                                              choices={'spy': env.new_line(good_line_1),
                                                       'open_up': env.new_line(bad_line_1)},
                                              event=EVENTS.OPEN_UP_CHOICE,
                                              choice=CHOICES.OPEN_UP) ])
        self.line = main_line


class SpyingWriter(Writer):

    QUEST_TYPE = SpyingLine.type()

    ACTIONS = { EVENTS.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to spy for %(person_end)s in %(place_end)s',
                EVENTS.MOVE_TO_QUEST: 'QUEST: hero move to %(place_end)s',
                EVENTS.MOVE_NEAR: 'QUEST: hero is spying for %(person_end)s'}

    LOG = { EVENTS.QUEST_DESCRIPTION:'QUEST:%(person_start)s ask hero to spy for %(person_end)s in %(place_end)s',
            EVENTS.MOVE_NEAR: 'QUEST: hero is spying for %(person_end)s',
            EVENTS.GET_REWARD: 'QUEST: %(person_end)s give hero a reward',
            EVENTS.OPEN_UP_CHOICE: 'QUEST: hero desided to open uop'}

    CHOICES = { CHOICES.OPEN_UP: {'question': 'should hero <a href="#" class="pgf-choice" data-choice="spy">spying</a> or <a href="#" class="pgf-choice" data-choice="open_up">open up</a>?',
                                  'results': {'spy': 'hero desided to continue spying',
                                              'open_up': 'hero desided to open up'} 
                                  } 
                }
