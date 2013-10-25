# coding: utf-8

import random

import mock

from questgen import facts
from questgen.quests.search_smith import SearchSmith
from questgen.quests.quests_base import QuestsBase
from questgen.quests.spying import Spying
from questgen import logic

from common.utils import testcase

from game.heroes.relations import EQUIPMENT_SLOT
from game.persons.relations import PERSON_TYPE

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.mobs.storage import mobs_storage

from game.logic import create_test_map
from game.text_generation import get_vocabulary
from game.prototypes import TimePrototype

from game.actions.prototypes import ActionQuestPrototype, ActionIdlenessPrototype

from game.heroes.relations import ITEMS_OF_EXPENDITURE

from game.quests.logic import QUESTS_BASE
from game.quests.writers import Writer
from game.quests.prototypes import QuestPrototype



class QuestsTestBase(testcase.TestCase):

    def setUp(self):
        super(QuestsTestBase, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

        self.hero._model.money += 1
        self.hero.preferences.set_mob(mobs_storage.all()[0])
        self.hero.preferences.set_place(self.p1)
        self.hero.preferences.set_friend(self.p1.persons[0])
        self.hero.preferences.set_enemy(self.p2.persons[0])
        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)
        self.hero.position.set_place(self.p3)
        self.hero.save()

        self.p1.persons[0]._model.type = PERSON_TYPE.BLACKSMITH
        self.p1.persons[0].save()


class QuestsTest(QuestsTestBase):

    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()

            self.hero.ui_info() # test if ui info formed correctly


def create_test_method(quest, quests):

    internal_quests = {q.TYPE: q for q in quests }

    @mock.patch('game.heroes.prototypes.HeroPrototype.is_short_quest_path_required', False)
    @mock.patch('game.heroes.prototypes.HeroPrototype.is_first_quest_path_required', False)
    @mock.patch('game.balance.constants.QUESTS_SPECIAL_FRACTION', 1.1)
    @mock.patch('game.quests.logic.QUESTS_BASE._quests', internal_quests)
    @mock.patch('game.quests.logic._get_first_quests', lambda hero, special: [quest.TYPE])
    @mock.patch('game.map.roads.storage.WaymarksStorage.average_path_length', 9999)
    def quest_test_method(self):

        # defends from first quest rule
        self.hero.statistics.change_quests_done(1)
        self.hero.save()

        current_time = TimePrototype.get_current_time()

        test_upgrade_equipment = random.randint(0, 1) # test child quest or upgrade equipment for SearchSmith

        while self.hero.actions.current_action.TYPE != ActionQuestPrototype.TYPE:
            self.storage.process_turn()
            if quest == SearchSmith and test_upgrade_equipment:
                self.hero._model.money = QuestPrototype.upgrade_equipment_cost(self.hero)
                self.hero._model.next_spending = ITEMS_OF_EXPENDITURE.INSTANT_HEAL
            current_time.increment_turn()

        self.complete_quest()

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionIdlenessPrototype.TYPE)

        if quest == SearchSmith and test_upgrade_equipment:
            self.assertTrue(self.hero.statistics.money_spend_for_artifacts > 0 or
                            self.hero.statistics.money_spend_for_sharpening > 0)

    return quest_test_method


for QuestClass in QUESTS_BASE.quests():

    quests = [QuestClass]

    if 'has_subquests' in QuestClass.TAGS:
        quests.append(Spying)

    setattr(QuestsTest, 'test_%s' % QuestClass.TYPE, create_test_method(QuestClass, list(quests)))




class RawQuestsTest(QuestsTestBase):

    def setUp(self):
        super(RawQuestsTest, self).setUp()
        self.vocabruary = get_vocabulary()

    def check_quest(self, knowledge_base):
        start = logic.get_absolute_start(knowledge_base)

        table = {}
        for jump in knowledge_base.filter(facts.Jump):
            if jump.state_from not in table:
                table[jump.state_from] = []
            table[jump.state_from].append(jump)

        powers = set()

        self._bruteforce(knowledge_base, [start.uid], table, [], processed=set(), powers=powers)

        self.check_participants(knowledge_base, powers)

    def check_participants(self, knowledge_base, powers):
        for participant in knowledge_base.filter(facts.QuestParticipant):
            self.assertTrue((participant.start, participant.participant) in powers)

    def _check_messages(self, quest_type, message):
        writer = Writer(type=quest_type, message=message, substitution={})

        # print '--------'
        # print writer.journal_id()
        # print writer.diary_id()
        # print writer.action_id()

        self.assertTrue(writer.journal_id() in self.vocabruary or
                        writer.diary_id() in self.vocabruary or
                        writer.action_id() in self.vocabruary)

    def _check_action_messages(self, quest_type, actions):
        for action in actions:
            if isinstance(action, facts.DoNothing):
                self._check_messages(quest_type, '%s_start' % action.type)
                self._check_messages(quest_type, '%s_donothing' % action.type)

            elif isinstance(action, facts.UpgradeEquipment):
                self._check_messages(quest_type, 'upgrade__fail')
                self._check_messages(quest_type, 'upgrade__buy_and_change')
                self._check_messages(quest_type, 'upgrade__buy')
                self._check_messages(quest_type, 'upgrade__sharp')
                self._check_messages(quest_type, 'upgrade_free__fail')
                self._check_messages(quest_type, 'upgrade_free__buy_and_change')
                self._check_messages(quest_type, 'upgrade_free__buy')
                self._check_messages(quest_type, 'upgrade_free__sharp')

            elif isinstance(action, facts.Message):
                self._check_messages(quest_type, action.type)

            elif isinstance(action, facts.GiveReward):
                self._check_messages(quest_type, '%s_money' % action.type)
                self._check_messages(quest_type, '%s_artifact' % action.type)


    def _get_powers(self, start, actions):
        powers = set()

        for action in actions:
            if isinstance(action, facts.GivePower):
                powers.add((start, action.object))

        return powers


    def _bruteforce(self, knowledge_base, path, table, starts, processed, powers):
        current_state = knowledge_base[path[-1]]

        if current_state.uid in processed:
            return

        if isinstance(current_state, facts.Start):
            starts.append((current_state.uid, current_state.type))

            writer = Writer(type=starts[-1][1], message=None, substitution={})
            self.assertTrue(writer.name_id() in self.vocabruary)

            for participant in knowledge_base.filter(facts.QuestParticipant):
                if knowledge_base[participant.start].type != starts[-1][1]:
                    continue

                self.assertTrue(writer.actor_id(participant.role) in self.vocabruary)

        self._check_action_messages(starts[-1][1], current_state.actions)

        powers |= self._get_powers(starts[-1][0], current_state.actions)

        if isinstance(current_state, facts.Finish):
            starts.pop()

        if not table.get(current_state.uid):
            return

        for next_jump in table[current_state.uid]:

            self._check_action_messages(starts[-1][1], next_jump.start_actions)
            self._check_action_messages(starts[-1][1], next_jump.end_actions)

            powers |= self._get_powers(starts[-1][0], next_jump.start_actions)
            powers |= self._get_powers(starts[-1][0], next_jump.end_actions)

            if isinstance(next_jump, facts.Option):
                writer = Writer(type=starts[-1][1], message='choice', substitution={})
                self.assertTrue(writer.choice_variant_id(next_jump.type) in self.vocabruary)
                self.assertTrue(writer.current_choice_id(next_jump.type) in self.vocabruary)

            path.append(next_jump.state_to)
            self._bruteforce(knowledge_base, path, table, list(starts), processed, powers )
            path.pop()

        processed.add(current_state.uid)


def create_test_messages_method(quest, quests):

    @mock.patch('game.heroes.prototypes.HeroPrototype.is_short_quest_path_required', False)
    @mock.patch('game.heroes.prototypes.HeroPrototype.is_first_quest_path_required', False)
    def quest_test_method(self):
        from questgen.selectors import Selector

        from game.quests.logic import get_knowledge_base
        from game.quests import uids

        knowledge_base = get_knowledge_base(self.hero)

        qb = QuestsBase()
        qb += quests

        selector = Selector(knowledge_base, qb)

        hero_uid = uids.hero(self.hero)

        quests_facts = selector.create_quest_from_place(nesting=0,
                                                        initiator_position=selector.place_for(objects=(hero_uid,)),
                                                        allowed=[quest.TYPE],
                                                        excluded=[],
                                                        tags=('can_start',))

        knowledge_base += quests_facts

        self.check_quest(knowledge_base)

    return quest_test_method


for QuestClass in QUESTS_BASE.quests():

    quests = [QuestClass]

    if 'has_subquests' in QuestClass.TAGS:
        quests.append(Spying)

    setattr(RawQuestsTest, 'test_%s' % QuestClass.TYPE, create_test_messages_method(QuestClass, list(quests)))
