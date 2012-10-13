# coding: utf-8
from game.quests.quests_generator.quest_line import Quest, Line, ACTOR_TYPE, DEFAULT_RESULTS
from game.quests.quests_generator import commands as cmd

class Delivery(Quest):

    ACTORS = [(u'отправитель', 'person_start', ACTOR_TYPE.PERSON),
              (u'получатель', 'person_end', ACTOR_TYPE.PERSON)]

    def initialize(self, identifier, env, place_start=None, person_start=None, place_end=None, person_end=None):
        super(Delivery, self).initialize(identifier, env)

        self.env_local.register('place_start', place_start or env.new_place())
        self.env_local.register('person_start', person_start or env.new_person(from_place=self.env_local.place_start))
        self.env_local.register('place_end', place_end or env.new_place())
        self.env_local.register('person_end', person_end or env.new_person(from_place=self.env_local.place_end))

        self.env_local.register('item_to_deliver', env.new_item())
        self.env_local.register('steal_point', env.new_choice_point())

    def create_line(self, env):
        delivery_line = Line(sequence=[cmd.Message(event='choice_delivery'),
                                       cmd.GiveItem(self.env_local.item_to_deliver, event='give_item'),
                                       cmd.QuestResult(result=DEFAULT_RESULTS.POSITIVE),
                                       cmd.GetReward(person=self.env_local.person_end, event='delivery_get_reward'),
                                       cmd.GivePower(person=self.env_local.person_start, power=1),
                                       cmd.GivePower(person=self.env_local.person_end, power=1)])
        steal_line = Line(sequence=[cmd.Message(event='choice_steal'),
                                    cmd.GiveItem(self.env_local.item_to_deliver, event='steal_item'),
                                    cmd.GetReward(event='steal_get_reward'),
                                    cmd.QuestResult(result=DEFAULT_RESULTS.NEGATIVE),
                                    cmd.GivePower(person=self.env_local.person_start, power=-1),
                                    cmd.GivePower(person=self.env_local.person_end, power=-1)])

        main_line = Line(sequence=[ cmd.Message(event='intro'),
                                    cmd.GetItem(self.env_local.item_to_deliver, event='get_item'),
                                    cmd.Move(place=self.env_local.place_end, event='move_to_destination'),
                                    cmd.Choose(id=self.env_local.steal_point,
                                               choices={'delivery': env.new_line(delivery_line),
                                                        'steal': env.new_line(steal_line)},
                                                        choice='steal') ])

        self.line = env.new_line(main_line)
