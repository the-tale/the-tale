# coding: utf-8

from questgen.quests.base_quest import BaseQuest
from questgen import facts

from game.prototypes import TimePrototype

from game.actions.prototypes import ActionQuestPrototype

class QuestTestsMixin(object):

    def turn_to_quest(self, storage, hero_id):

        current_time = TimePrototype.get_current_time()

        hero = storage.heroes[hero_id]

        while hero.actions.current_action.TYPE != ActionQuestPrototype.TYPE:
            storage.process_turn()
            current_time.increment_turn()

        storage.save_changed_data()

        return hero.quests.current_quest


class QuestWith2ChoicePoints(BaseQuest):
    TYPE = 'quest_with_2_choice_points'
    TAGS = ('normal', 'can_start', 'can_continue')

    @classmethod
    def construct_from_place(cls, knowledge_base, selector, start_place):

        ns = knowledge_base.get_next_ns()

        start = facts.Start(uid=ns+'start', type=cls.TYPE)

        choice_1 = facts.Choice(uid=ns+'choice_1')

        choice_2 = facts.Choice(uid=ns+'choice_2')

        finish_1_1 = facts.Finish(uid=ns+'finish_1_1')
        finish_1_2 = facts.Finish(uid=ns+'finish_1_2')
        finish_2 = facts.Finish(uid=ns+'finish_2')

        return [ start,
                 choice_1,
                 choice_2,
                 finish_1_1,
                 finish_1_2,
                 finish_2,

                 facts.Jump(state_from=start.uid, state_to=choice_1.uid),

                 facts.Option(state_from=choice_1.uid, state_to=finish_2.uid, type='opt_1'),
                 facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2'),
                 facts.Option(state_from=choice_2.uid, state_to=finish_1_1.uid, type='opt_2_1'),
                 facts.Option(state_from=choice_2.uid, state_to=finish_1_2.uid, type='opt_2_2')
                ]
