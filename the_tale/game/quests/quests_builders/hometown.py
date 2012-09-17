# coding: utf-8

import random

from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE, DEFAULT_RESULTS
from game.quests.quests_generator import commands as cmd

class Hometown(Quest):

    SPECIAL = True

    ACTORS = [(u'родной город', 'place_end', ACTOR_TYPE.PLACE)]

    @classmethod
    def can_be_used(cls, env):
        return env.knowlege_base.get_special('hero_pref_hometown') is not None

    def initialize(self, identifier, env, place_start=None, place_end=None):
        super(Hometown, self).initialize(identifier, env)

        hometown_uuid = env.knowlege_base.get_special('hero_pref_hometown')['uuid']

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('place_end', env.new_place(place_uuid=hometown_uuid))


    def create_line(self, env):

        home_actions = [ cmd.DoNothing(event='drunk_song', duration=6, messages_prefix='drunk_song', messages_probability=0.3),
                         cmd.DoNothing(event='stagger_streets', duration=10, messages_prefix='stagger_streets', messages_probability=0.3),
                         cmd.DoNothing(event='chatting', duration=5, messages_prefix='chatting', messages_probability=0.3),
                         cmd.DoNothing(event='search_old_friends', duration=7, messages_prefix='search_old_friends', messages_probability=0.3),
                         cmd.DoNothing(event='remember_names', duration=3, messages_prefix='remember_names', messages_probability=0.3) ]

        sequence = [cmd.Message(event='intro')]

        if self.env_local.place_start != self.env_local.place_end:
            sequence.append(cmd.Move(place=self.env_local.place_end, event='move_to_quest'))

        sequence += random.sample(home_actions, 3)

        sequence += [ cmd.QuestResult(result=DEFAULT_RESULTS.POSITIVE),
                      cmd.GetReward(person=None, event='get_reward') ]

        main_line = Line(sequence=sequence)

        self.line = env.new_line(main_line)
