# coding: utf-8

from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE, DEFAULT_RESULTS
from game.quests.quests_generator import commands as cmd


class HelpFriend(Quest):

    ACTORS = [(u'соратник', 'person_end', ACTOR_TYPE.PERSON)]

    @classmethod
    def can_be_used(cls, env):
        return env.knowlege_base.get_special('hero_pref_friend') is not None


    def initialize(self, identifier, env, place_start=None):
        super(HelpFriend, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())

        friend_uuid = env.knowlege_base.get_special('hero_pref_friend')['uuid']

        self.env_local.register('person_end', env.new_person(person_uuid=friend_uuid))
        self.env_local.register('place_end', env.new_place(person_uuid=friend_uuid))

        self.env_local.register('quest_help', env.new_quest(from_list=['delivery', 'caravan', 'spying', 'not_my_work'],
                                                            place_start=self.env_local.place_end,
                                                            person_start=self.env_local.person_end) )

    def create_line(self, env):

        sequence = [ cmd.Message(event='intro') ]

        if self.env_local.place_start != self.env_local.place_end:
            sequence += [ cmd.Move(place=self.env_local.place_end, event='move_to_quest') ]

        positive_line = Line(sequence = [cmd.QuestResult(result=DEFAULT_RESULTS.POSITIVE),
                                         cmd.GetReward(person=self.env_local.person_end, event='get_reward'),
                                         cmd.GivePower(person=self.env_local.person_end, power=1)])

        negative_line = Line(sequence = [cmd.QuestResult(result=DEFAULT_RESULTS.NEGATIVE),
                                         cmd.GetReward(person=self.env_local.person_end, event='get_reward'),
                                         cmd.GivePower(person=self.env_local.person_end, power=-1)])

        sequence += [ cmd.Quest(quest=self.env_local.quest_help),
                      cmd.Switch(choices=[((self.env_local.quest_help, DEFAULT_RESULTS.POSITIVE), env.new_line(positive_line)),
                                          ((self.env_local.quest_help, DEFAULT_RESULTS.NEGATIVE), env.new_line(negative_line))]) ]

        main_line =  Line(sequence=sequence)

        self.line = env.new_line(main_line)

        env.quests[self.env_local.quest_help].create_line(env)
