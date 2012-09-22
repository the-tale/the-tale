# coding: utf-8
from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE, DEFAULT_RESULTS
from game.quests.quests_generator import commands as cmd


class Help(Quest):

    ACTORS = [(u'попросил', 'person_start', ACTOR_TYPE.PERSON),
              (u'нуждающийся', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(Help, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('quest_help', env.new_quest(from_list=['delivery', 'caravan', 'spying', 'not_my_work'],
                                                            place_start=self.env_local.place_end,
                                                            person_start=self.env_local.person_end) )

    def create_line(self, env):

        positive_line = Line(sequence = [cmd.QuestResult(result=DEFAULT_RESULTS.POSITIVE),
                                         cmd.GivePower(person=self.env_local.person_start, power=1),
                                         cmd.GetReward(person=self.env_local.person_end, event='get_reward')])

        negative_line = Line(sequence = [cmd.QuestResult(result=DEFAULT_RESULTS.NEGATIVE),
                                         cmd.GivePower(person=self.env_local.person_start, power=-1),
                                         cmd.GetReward(person=self.env_local.person_end, event='get_reward')])

        main_line =  Line(sequence = [ cmd.Message(event='intro'),
                                       cmd.Move(place=self.env_local.place_end, event='move_to_quest'),
                                       cmd.Quest(quest=self.env_local.quest_help),
                                       cmd.Switch(choices=[((self.env_local.quest_help, DEFAULT_RESULTS.POSITIVE), env.new_line(positive_line)),
                                                           ((self.env_local.quest_help, DEFAULT_RESULTS.NEGATIVE), env.new_line(negative_line))]) ])

        self.line = env.new_line(main_line)
        env.quests[self.env_local.quest_help].create_line(env)
