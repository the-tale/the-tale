# coding: utf-8

import random

import mock

from dext.common.utils import s11n

from questgen import facts
from questgen import actions as questgen_actions
from questgen.quests.search_smith import SearchSmith
from questgen.quests.quests_base import QuestsBase
from questgen import logic

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.linguistics.lexicon.keys import LEXICON_KEY

from the_tale.game.heroes.relations import EQUIPMENT_SLOT
from the_tale.game.heroes.relations import ITEMS_OF_EXPENDITURE
from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.persons.relations import PERSON_TYPE
from the_tale.game.persons import logic as persons_logic

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype

from the_tale.game.actions.prototypes import ActionQuestPrototype, ActionIdlenessPrototype

from the_tale.game.map.places.modifiers import HolyCity

from the_tale.game.quests.writers import Writer
from the_tale.game.quests.prototypes import QuestPrototype
from the_tale.game.quests.relations import DONOTHING_TYPE, QUESTS



class QuestsTestBase(testcase.TestCase):

    def setUp(self):
        super(QuestsTestBase, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()

        # add more persons, to lower conflicts
        self.p1.add_person()
        self.p1.add_person()
        self.p2.add_person()
        self.p2.add_person()
        self.p3.add_person()
        self.p3.add_person()

        persons_logic.sync_social_connections()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.hero.money += 1
        self.hero.preferences.set_mob(mobs_storage.all()[0])
        self.hero.preferences.set_place(self.p1)
        self.hero.preferences.set_friend(self.p1.persons[0])
        self.hero.preferences.set_enemy(self.p2.persons[0])
        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)
        self.hero.position.set_place(self.p3)
        heroes_logic.save_hero(self.hero)

        self.p2.modifier = HolyCity(self.p2)
        self.p2.save()

        self.p1.persons[0]._model.type = PERSON_TYPE.BLACKSMITH
        self.p1.persons[0].save()


class QuestsTest(QuestsTestBase):

    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()

            self.hero.ui_info(actual_guaranteed=True) # test if ui info formed correctly


def create_test_method(quest, quests):

    internal_quests = {q.quest_class.TYPE: q.quest_class for q in quests }

    @mock.patch('the_tale.game.heroes.objects.Hero.is_short_quest_path_required', False)
    @mock.patch('the_tale.game.heroes.objects.Hero.is_first_quest_path_required', False)
    @mock.patch('the_tale.game.quests.logic.QUESTS_BASE._quests', internal_quests)
    @mock.patch('the_tale.game.heroes.objects.Hero.get_quests_priorities', lambda hero: [(quest, 10000000)] + [(q, 0) for q in quests if q != quest])
    def quest_test_method(self):

        # defends from first quest rule
        self.hero.statistics.change_quests_done(1)
        heroes_logic.save_hero(self.hero)

        current_time = TimePrototype.get_current_time()

        test_upgrade_equipment = random.randint(0, 1) # test child quest or upgrade equipment for SearchSmith

        while self.hero.actions.current_action.TYPE != ActionQuestPrototype.TYPE or not self.hero.quests.has_quests:
            if quest == SearchSmith and test_upgrade_equipment:
                self.hero.money = QuestPrototype.upgrade_equipment_cost(self.hero) * 2
                self.hero.next_spending = ITEMS_OF_EXPENDITURE.INSTANT_HEAL

            self.storage.process_turn()
            current_time.increment_turn()

        # test if quest is serializable
        s11n.to_json(self.hero.quests.current_quest.serialize())

        self.complete_quest()

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionIdlenessPrototype.TYPE)

        if quest == SearchSmith and test_upgrade_equipment:
            self.assertTrue(self.hero.statistics.money_spend_for_artifacts > 0 or
                            self.hero.statistics.money_spend_for_sharpening > 0)

    return quest_test_method


class RawQuestsTest(QuestsTestBase):

    def setUp(self):
        super(RawQuestsTest, self).setUp()

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
        writer = Writer(type=quest_type, message=message, substitution={}, hero=self.hero)

        # print '--------'
        # print writer.journal_id()
        # print writer.diary_id()
        # print writer.action_id()

        self.assertTrue(writer.journal_id().upper() in LEXICON_KEY.index_name or
                        writer.diary_id().upper() in LEXICON_KEY.index_name or
                        writer.action_id().upper() in LEXICON_KEY.index_name)

    def _check_action_messages(self, quest_type, actions):
        for action in actions:
            if isinstance(action, questgen_actions.DoNothing):
                self._check_messages(quest_type, '%s_start' % action.type)
                self._check_messages(quest_type, '%s_donothing' % action.type)

                # check donothing type in DONOTHING relation
                self.assertTrue(action.type in DONOTHING_TYPE.index_value)

            elif isinstance(action, questgen_actions.UpgradeEquipment):
                self._check_messages(quest_type, 'upgrade__fail')
                self._check_messages(quest_type, 'upgrade__buy_and_change')
                self._check_messages(quest_type, 'upgrade__buy')
                self._check_messages(quest_type, 'upgrade__sharp')
                self._check_messages(quest_type, 'upgrade_free__fail')
                self._check_messages(quest_type, 'upgrade_free__buy_and_change')
                self._check_messages(quest_type, 'upgrade_free__buy')
                self._check_messages(quest_type, 'upgrade_free__sharp')

            elif isinstance(action, questgen_actions.Message):
                self._check_messages(quest_type, action.type)

            elif isinstance(action, questgen_actions.GiveReward):
                self._check_messages(quest_type, '%s_money' % action.type)
                self._check_messages(quest_type, '%s_artifact' % action.type)


    def _get_powers(self, start, actions):
        powers = set()

        for action in actions:
            if isinstance(action, questgen_actions.GivePower):
                powers.add((start, action.object))

        return powers


    def _bruteforce(self, knowledge_base, path, table, starts, processed, powers):
        current_state = knowledge_base[path[-1]]

        if current_state.uid in processed:
            return

        if isinstance(current_state, facts.Start):
            starts.append((current_state.uid, current_state.type))

            writer = Writer(type=starts[-1][1], message=None, substitution={}, hero=self.hero)
            self.assertTrue(writer.name_id().upper() in LEXICON_KEY.index_name)

            for participant in knowledge_base.filter(facts.QuestParticipant):
                if knowledge_base[participant.start].type != starts[-1][1]:
                    continue

                self.assertTrue(writer.actor_id(participant.role).upper() in LEXICON_KEY.index_name)

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
                writer = Writer(type=starts[-1][1], message='choice', substitution={}, hero=self.hero)
                self.assertTrue(writer.choice_variant_id(next_jump.type).upper() in LEXICON_KEY.index_name)
                self.assertTrue(writer.current_choice_id(next_jump.type).upper() in LEXICON_KEY.index_name)

            path.append(next_jump.state_to)
            self._bruteforce(knowledge_base, path, table, list(starts), processed, powers )
            path.pop()

        processed.add(current_state.uid)


def create_test_messages_method(quest, quests):

    @mock.patch('the_tale.game.heroes.objects.Hero.is_short_quest_path_required', False)
    @mock.patch('the_tale.game.heroes.objects.Hero.is_first_quest_path_required', False)
    def quest_test_method(self):
        from questgen.selectors import Selector

        from the_tale.game.quests import logic
        from the_tale.game.quests import uids

        knowledge_base = logic.get_knowledge_base(logic.create_hero_info(self.hero))

        qb = QuestsBase()
        qb += [q.quest_class for q in quests]

        selector = Selector(knowledge_base, qb)

        hero_uid = uids.hero(self.hero.id)

        quests_facts = selector.create_quest_from_place(nesting=0,
                                                        initiator_position=selector.place_for(objects=(hero_uid,)),
                                                        allowed=[quest.quest_class.TYPE],
                                                        excluded=[],
                                                        tags=('can_start',))

        knowledge_base += quests_facts

        self.check_quest(knowledge_base)

    return quest_test_method


for quest in QUESTS.records:

    quests = [quest]

    if 'has_subquests' in quest.quest_class.TAGS:
        quests.append(QUESTS.SPYING)

    setattr(QuestsTest, 'test_%s' % quest.name, create_test_method(quest, list(quests)))
    setattr(RawQuestsTest, 'test_%s' % quest.name, create_test_messages_method(quest, list(quests)))
