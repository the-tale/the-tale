# coding: utf-8
from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE, DEFAULT_RESULTS
from game.quests.quests_generator import commands as cmd


class Caravan(Quest):

    ACTORS = [(u'отправил', 'person_start', ACTOR_TYPE.PERSON),
              (u'место назначения', 'place_end', ACTOR_TYPE.PLACE),
              (u'ожидает прибытия', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(Caravan, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('choose_point_1', env.new_choice_point())

    def create_line(self, env):

        bad_line_1 = Line(sequence=[cmd.Message(event='choice_attack'),
                                    cmd.Battle(number=1, event='caravan_attack'),
                                    cmd.Move(place=self.env_local.place_start, event='run_away'),
                                    cmd.QuestResult(result=DEFAULT_RESULTS.NEGATIVE),
                                    cmd.GetReward(person=self.env_local.person_end, event='bad_get_reward'),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1)])

        good_line_2 = Line(sequence=[cmd.Message(event='choice_defend'),
                                     cmd.Battle(number=2, event='bandits_attack'),
                                     cmd.Move(place=self.env_local.place_end, event='move_to_point'),
                                     cmd.QuestResult(result=DEFAULT_RESULTS.POSITIVE),
                                     cmd.GetReward(person=self.env_local.person_end, event='good_get_reward'),
                                     cmd.GivePower(person=self.env_local.person_start, power=1),
                                     cmd.GivePower(person=self.env_local.person_end, power=1)])

        main_line = Line(sequence=[cmd.Message(event='intro'),
                                   cmd.Move(place=self.env_local.place_end, break_at=0.5, event='move_to_point'),
                                   cmd.Choose(id=self.env_local.choose_point_1,
                                              choices={'caravan': env.new_line(good_line_2),
                                                       'bandits': env.new_line(bad_line_1)},
                                              choice='bring') ])
        self.line = env.new_line(main_line)
