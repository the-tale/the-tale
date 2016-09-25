# coding: utf-8
import mock

from questgen.quests.base_quest import BaseQuest, RESULTS
from questgen import facts

from the_tale.game.prototypes import TimePrototype

from the_tale.game.actions.prototypes import ActionQuestPrototype

from the_tale.game.quests.writers import Writer
from the_tale.game.quests import logic


def setup_quest(hero):
    hero_info = logic.create_hero_info(hero)
    knowledge_base = logic.create_random_quest_for_hero(hero_info, mock.Mock())
    logic.setup_quest_for_hero(hero, knowledge_base.serialize())



class QuestTestsMixin(object):

    def turn_to_quest(self, storage, hero_id):

        current_time = TimePrototype.get_current_time()

        hero = storage.heroes[hero_id]

        while hero.actions.current_action.TYPE != ActionQuestPrototype.TYPE or not self.hero.quests.has_quests:
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

        initiator = selector.new_person(first_initiator=(nesting==0), restrict_places=False, places=(start_place.uid, ))
        receiver = selector.new_person(first_initiator=False)

        initiator_position = selector.place_for(objects=(initiator.uid,))
        receiver_position = selector.place_for(objects=(receiver.uid,))

        ns = selector._kb.get_next_ns()

        start = facts.Start(uid=ns+'start', type=cls.TYPE, nesting=nesting)

        choice_1 = facts.Choice(uid=ns+'choice_1')

        choice_2 = facts.Choice(uid=ns+'choice_2')

        finish_1_1 = facts.Finish(uid=ns+'finish_1_1',
                                  start=start.uid,
                                  results={initiator.uid: RESULTS.SUCCESSED,
                                           initiator_position.uid: RESULTS.FAILED,
                                           receiver.uid: RESULTS.SUCCESSED,
                                           receiver_position.uid: RESULTS.SUCCESSED},
                                  nesting=nesting)
        finish_1_2 = facts.Finish(uid=ns+'finish_1_2',
                                  start=start.uid,
                                  results={initiator.uid: RESULTS.FAILED,
                                           initiator_position.uid: RESULTS.FAILED,
                                           receiver.uid: RESULTS.FAILED,
                                           receiver_position.uid: RESULTS.FAILED},
                                  nesting=nesting)
        finish_2 = facts.Finish(uid=ns+'finish_2',
                                start=start.uid,
                                results={initiator.uid: RESULTS.SUCCESSED,
                                         initiator_position.uid: RESULTS.SUCCESSED,
                                         receiver.uid: RESULTS.FAILED,
                                         receiver_position.uid: RESULTS.FAILED},
                                nesting=nesting)

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

                         facts.Option(state_from=choice_1.uid, state_to=finish_2.uid, type='opt_1', markers=()),
                         facts.Option(state_from=choice_1.uid, state_to=choice_2.uid, type='opt_2', markers=()),
                         facts.Option(state_from=choice_2.uid, state_to=finish_1_1.uid, type='opt_2_1', markers=()),
                         facts.Option(state_from=choice_2.uid, state_to=finish_1_2.uid, type='opt_2_2', markers=())
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
