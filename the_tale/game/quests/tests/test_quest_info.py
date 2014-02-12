# coding: utf-8

import mock

from questgen import facts
from questgen.relations import OPTION_MARKERS as QUEST_OPTION_MARKERS

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.quests.prototypes import QuestInfo
from the_tale.game.quests.tests.helpers import QuestTestsMixin, QuestWith2ChoicePoints, FakeWriter


class QuestInfoTests(testcase.TestCase, QuestTestsMixin):

    def setUp(self):
        super(QuestInfoTests, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action
        self.action_idl.state = self.action_idl.STATE.QUEST

        self.quest = self.create_quest()

        self.start = self.quest.knowledge_base.filter(facts.Start).next()

        with mock.patch('the_tale.game.quests.writers.get_writer', lambda **kwargs: FakeWriter(fake_uid='q', **kwargs)):
            self.quest_info = QuestInfo.construct(type=self.start.type,
                                                  uid=self.start.uid,
                                                  knowledge_base=self.quest.knowledge_base,
                                                  hero=self.hero)

    @mock.patch('questgen.quests.quests_base.QuestsBase._available_quests', lambda *argv, **kwargs: [QuestWith2ChoicePoints])
    def create_quest(self):
        return self.turn_to_quest(self.storage, self.hero.id)

    def test_construct(self):
        self.assertEqual(self.quest_info.type, self.start.type)
        self.assertEqual(self.quest_info.uid, self.start.uid)
        self.assertEqual(self.quest_info.name, 'q_quest_quest_with_2_choice_points_name_5')
        self.assertEqual(self.quest_info.action, '')
        self.assertEqual(self.quest_info.choice, None)
        self.assertEqual(self.quest_info.choice_alternatives, [])
        self.assertTrue(self.quest_info.experience > 0 )
        self.assertTrue(self.quest_info.power > 0)
        self.assertEqual(set(self.quest_info.actors.keys()), set(['initiator', 'receiver', 'initiator_position', 'receiver_position']))


    def test_serialization(self):
        self.assertEqual(self.quest_info.serialize(), QuestInfo.deserialize(self.quest_info.serialize()).serialize())

    def get_choices(self, default=True):
        choice = self.quest.knowledge_base['[ns-0]choice_1']
        options = sorted((o for o in self.quest.knowledge_base.filter(facts.Option) if o.state_from == choice.uid),
                         key=lambda o: o.uid)
        defaults = [facts.ChoicePath(choice=choice.uid, option=options[-1].uid, default=default)]

        return choice, options, defaults


    @mock.patch('the_tale.game.quests.writers.get_writer', lambda **kwargs: FakeWriter(fake_uid='q', **kwargs))
    def test_sync_choices(self):

        self.quest_info.sync_choices(self.quest.knowledge_base,
                                     self.quest.hero,
                                     *self.get_choices())

        self.assertEqual(self.quest_info.choice, 'q_quest_quest_with_2_choice_points_choice_current_opt_1_1')
        self.assertEqual(self.quest_info.choice_alternatives,  [('#option([ns-0]choice_1, [ns-0]choice_2, opt_2)',
                                                                 u'q_quest_quest_with_2_choice_points_choice_variant_opt_2_2')])

    @mock.patch('the_tale.game.quests.writers.get_writer', lambda **kwargs: FakeWriter(fake_uid='q', **kwargs))
    def test_sync_choices__no_choice(self):
        self.quest_info.sync_choices(self.quest.knowledge_base,
                                     self.quest.hero,
                                     *self.get_choices())

        self.quest_info.sync_choices(knowledge_base=self.quest.knowledge_base,
                                     hero=self.quest.hero,
                                     choice=None,
                                     options=(),
                                     defaults=())

        self.assertEqual(self.quest_info.choice, None)
        self.assertEqual(self.quest_info.choice_alternatives, ())

    @mock.patch('the_tale.game.quests.writers.get_writer', lambda **kwargs: FakeWriter(fake_uid='q', **kwargs))
    def test_sync_choices__no_choice_made(self):
        self.quest_info.sync_choices(self.quest.knowledge_base,
                                     self.quest.hero,
                                     *self.get_choices(default=False))

        self.assertEqual(self.quest_info.choice, 'q_quest_quest_with_2_choice_points_choice_current_opt_1_1')
        self.assertEqual(self.quest_info.choice_alternatives,  ())


    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.reward_modifier', 1.0)
    @mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.quest_markers_rewards_bonus', lambda self: {QUEST_OPTION_MARKERS.HONORABLE: 0.2,
                                                                                                           QUEST_OPTION_MARKERS.DISHONORABLE: 0.3,
                                                                                                           QUEST_OPTION_MARKERS.AGGRESSIVE: 0.4,
                                                                                                           QUEST_OPTION_MARKERS.UNAGGRESSIVE: 0.5})
    def test_get_real_reward_scale(self):

        self.assertEqual(self.quest_info.get_real_reward_scale(self.hero, 1.0), 1.0)

        self.quest_info.used_markers[QUEST_OPTION_MARKERS.DISHONORABLE] = True
        self.assertEqual(self.quest_info.get_real_reward_scale(self.hero, 1.0), 1.3)

        self.quest_info.used_markers[QUEST_OPTION_MARKERS.AGGRESSIVE] = False
        self.assertEqual(self.quest_info.get_real_reward_scale(self.hero, 1.0), 1.3*1.4)

        self.quest_info.used_markers[QUEST_OPTION_MARKERS.HONORABLE] = False
        self.assertEqual(self.quest_info.get_real_reward_scale(self.hero, 1.0), 1.3*1.4*1.2)

        self.quest_info.used_markers[QUEST_OPTION_MARKERS.UNAGGRESSIVE] =  True
        self.assertEqual(self.quest_info.get_real_reward_scale(self.hero, 1.0), 1.3*1.4*1.2*1.5)
