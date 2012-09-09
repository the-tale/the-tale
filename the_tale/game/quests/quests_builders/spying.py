# coding: utf-8
from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE
from game.quests.quests_generator import commands as cmd

class EVENTS:
    INTRO = 'intro'

    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    SPYING = 'spying'
    RETURN = 'return'
    GET_REWARD = 'get_reward'

    GOOD_GIVE_POWER = 'good_give_power'
    BAD_GIVE_POWER = 'bad_give_power'

    OPEN_UP_CHOICE = 'openup_choice'

    CHOICE_OPEN_UP = 'choice_open_up'
    CHOICE_CONTINUE_SPYING = 'choice_continue_spying'


class Spying(Quest):

    ACTORS = [(u'заказчик', 'person_start', ACTOR_TYPE.PERSON),
              (u'цель', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(Spying, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('choose_point_1', env.new_choice_point())

    def create_line(self, env):

        bad_line_1 = Line(sequence=[ cmd.Message(event=EVENTS.CHOICE_OPEN_UP),
                                     cmd.MoveNear(place=self.env_local.place_end, back=True, event=EVENTS.RETURN),
                                     cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                     cmd.GivePower(person=self.env_local.person_start, power=-1, event=EVENTS.BAD_GIVE_POWER),
                                     cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.BAD_GIVE_POWER)])

        good_line_2 = Line(sequence=[cmd.Message(event=EVENTS.CHOICE_CONTINUE_SPYING),
                                     cmd.MoveNear(place=self.env_local.place_end, back=True, event=EVENTS.RETURN),
                                     cmd.GetReward(person=self.env_local.person_end, event=EVENTS.GET_REWARD),
                                     cmd.GivePower(person=self.env_local.person_start, power=1, event=EVENTS.GOOD_GIVE_POWER),
                                     cmd.GivePower(person=self.env_local.person_end, power=-1, event=EVENTS.GOOD_GIVE_POWER)])

        main_line = Line(sequence=[cmd.Message(event=EVENTS.INTRO),
                                   cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST),
                                   cmd.MoveNear(place=self.env_local.place_end, back=False, event=EVENTS.SPYING),
                                   cmd.Choose(id=self.env_local.choose_point_1,
                                              choices={'spy': env.new_line(good_line_2),
                                                       'open_up': env.new_line(bad_line_1)},
                                              event=EVENTS.OPEN_UP_CHOICE,
                                              choice='openup') ])
        self.line = env.new_line(main_line)
