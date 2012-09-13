# coding: utf-8

from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE
from game.quests.quests_generator import commands as cmd

from game.persons.models import PERSON_TYPE

class EVENTS:
    INTRO = 'intro'
    QUEST_DESCRIPTION = 'quest_description'
    MOVE_TO_QUEST = 'move_to_quest'
    START_QUEST = 'start_quest'
    GIVE_POWER = 'give_power'
    UPGRADE_EQUIPMENT = 'upgrade_equipment'

class SearchSmith(Quest):

    ACTORS = [(u'кузнец', 'person_end', ACTOR_TYPE.PERSON)]

    @classmethod
    def can_be_used(cls, env):
        return env.knowlege_base.get_special('hero_pref_equipment_slot') is not None

    def initialize(self, identifier, env, place_start=None):
        super(SearchSmith, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())

        self.env_local.register('person_end', env.new_person(profession=PERSON_TYPE.BLACKSMITH))
        self.env_local.register('place_end', env.new_place(person_uuid=self.env_local.person_end))

    def create_line(self, env):

        sequence = [ cmd.Message(event=EVENTS.INTRO) ]

        if self.env_local.place_start != self.env_local.place_end:
            sequence += [ cmd.Move(place=self.env_local.place_end, event=EVENTS.MOVE_TO_QUEST) ]

        sequence += [ cmd.UpgradeEquipment(equipment_slot=env.knowlege_base.get_special('hero_pref_equipment_slot'),
                                           messages_prefix='upgrade_equipment', # this prefix used by writer
                                           event=EVENTS.UPGRADE_EQUIPMENT),
                      cmd.GivePower(person=self.env_local.person_end, power=1, event=EVENTS.GIVE_POWER)]

        main_line =  Line(sequence=sequence)

        self.line = env.new_line(main_line)
