# coding: utf-8

import random

from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE
from game.quests.quests_generator import commands as cmd


class EVENTS:
    INTRO = 'intro'
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    DRUNK_SONG = 'drunk_song'
    STAGGER_STREETS = 'stagger_streets'
    CHATTING = 'chatting'
    SEARCH_OLD_FRIENDS = 'search_old_friends'
    REMEMBER_NAMES = 'remember_names'
    GET_REWARD = 'get_reward'


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

        home_actions = [ cmd.DoNothing(event=EVENTS.DRUNK_SONG, duration=6, messages_prefix='quest_hometown_donothing_drunk_song', messages_probability=0.3),
                         cmd.DoNothing(event=EVENTS.STAGGER_STREETS, duration=10, messages_prefix='quest_hometown_donothing_stagger_streets', messages_probability=0.3),
                         cmd.DoNothing(event=EVENTS.CHATTING, duration=5, messages_prefix='quest_hometown_donothing_chatting', messages_probability=0.3),
                         cmd.DoNothing(event=EVENTS.SEARCH_OLD_FRIENDS, duration=7, messages_prefix='quest_hometown_donothing_search_old_friends', messages_probability=0.3),
                         cmd.DoNothing(event=EVENTS.REMEMBER_NAMES, duration=3, messages_prefix='quest_hometown_donothing_remember_names', messages_probability=0.3) ]

        sequence = [cmd.Message(event=EVENTS.INTRO)]

        if self.env_local.place_start != self.env_local.place_end:
            sequence.append(cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST))

        sequence += random.sample(home_actions, 3)

        sequence += [cmd.GetReward(person=None, event=EVENTS.GET_REWARD) ]

        main_line = Line(sequence=sequence)

        self.line = env.new_line(main_line)
