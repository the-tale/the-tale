# coding: utf-8

from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE, DEFAULT_RESULTS
from game.quests.quests_generator import commands as cmd

class InterfereEnemy(Quest):

    ACTORS = [(u'противник', 'person_end', ACTOR_TYPE.PERSON)]

    @classmethod
    def can_be_used(cls, env):
        return env.knowlege_base.get_special('hero_pref_enemy') is not None


    def initialize(self, identifier, env, place_start=None):
        super(InterfereEnemy, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())

        enemy_uuid = env.knowlege_base.get_special('hero_pref_enemy')['uuid']

        self.env_local.register('person_end', env.new_person(person_uuid=enemy_uuid))
        self.env_local.register('place_end', env.new_place(person_uuid=enemy_uuid))

        self.env_local.register('quest_interfer', env.new_quest(from_list=['delivery', 'caravan', 'spying', 'not_my_work'],
                                                                place_start=self.env_local.place_start,
                                                                place_end=self.env_local.place_end,
                                                                person_end=self.env_local.person_end) )

    def create_line(self, env):

        sequence = [ cmd.Message(event='intro') ]

        # if self.env_local.place_start != self.env_local.place_end:
        #     sequence += [ cmd.Move(place=self.env_local.place_end, event='move_to_quest') ]

        positive_line = Line(sequence = [cmd.QuestResult(result=DEFAULT_RESULTS.POSITIVE),
                                         cmd.GetReward(person=self.env_local.person_end, event='get_reward'),
                                         cmd.GivePower(person=self.env_local.person_end, power=-1)])

        negative_line = Line(sequence = [cmd.QuestResult(result=DEFAULT_RESULTS.NEGATIVE),
                                         cmd.GetReward(person=self.env_local.person_end, event='get_reward'),
                                         cmd.GivePower(person=self.env_local.person_end, power=+1)])

        sequence += [ cmd.Quest(quest=self.env_local.quest_interfer),
                      cmd.Switch(choices=[((self.env_local.quest_interfer, DEFAULT_RESULTS.POSITIVE), env.new_line(negative_line)),
                                          ((self.env_local.quest_interfer, DEFAULT_RESULTS.NEGATIVE), env.new_line(positive_line))]) ]

        main_line =  Line(sequence=sequence)

        self.line = env.new_line(main_line)

        env.quests[self.env_local.quest_interfer].create_line(env)
