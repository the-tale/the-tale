# coding: utf-8

from questgen.quests.base_quest import BaseQuest, RESULTS
from questgen import facts

from game.prototypes import TimePrototype

from game.actions.prototypes import ActionQuestPrototype

from game.quests.writers import Writer



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
    def construct_from_place(cls, nesting, selector, start_place):
        from questgen.quests.base_quest import ROLES

        initiator = selector.person_from(places=(start_place.uid, ))
        receiver = selector.new_person()

        initiator_position = selector.place_for(objects=(initiator.uid,))
        receiver_position = selector.place_for(objects=(receiver.uid,))

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start', type=cls.TYPE, nesting=nesting)

        choice_1 = facts.Choice(uid=ns+'choice_1')

        choice_2 = facts.Choice(uid=ns+'choice_2')

        finish_1_1 = facts.Finish(uid=ns+'finish_1_1', result=RESULTS.SUCCESSED, nesting=nesting)
        finish_1_2 = facts.Finish(uid=ns+'finish_1_2', result=RESULTS.FAILED, nesting=nesting)
        finish_2 = facts.Finish(uid=ns+'finish_2', result=RESULTS.SUCCESSED, nesting=nesting)

        participants = [facts.QuestParticipant(start=start.uid, participant=initiator.uid, role=ROLES.INITIATOR),
                        facts.QuestParticipant(start=start.uid, participant=initiator_position.uid, role=ROLES.INITIATOR_POSITION),
                        facts.QuestParticipant(start=start.uid, participant=receiver.uid, role=ROLES.RECEIVER),
                        facts.QuestParticipant(start=start.uid, participant=receiver_position.uid, role=ROLES.RECEIVER_POSITION) ]

        quest_facts =  [ start,
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

        return participants + quest_facts


class FakeWriter(Writer):

    def __init__(self, fake_uid, **kwargs):
        super(FakeWriter, self).__init__(**kwargs)
        self._counter = 0
        self._fake_uid = fake_uid

    def get_message(self, type_, **kwargs):
        self._counter += 1
        return u'%s_%s_%d' % (self._fake_uid, type_, self._counter)
