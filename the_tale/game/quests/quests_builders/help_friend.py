# coding: utf-8

from game.quests.quests_builders.help import Help

class HelpFriend(Help):

    @classmethod
    def can_be_used(cls, env):
        return env.knowlege_base.get_special('hero_pref_friend') is not None

    def initialize(self, identifier, env, place_start=None, place_end=None):
        friend_uuid = env.knowlege_base.get_special('hero_pref_friend')

        self.env_local.register('person_end', env.new_place(friend_uuid))

        super(HelpFriend, self).initialize(identifier, env, place_start=place_start, place_end=place_end, person_end=self.env_local.person_end)
