# coding: utf-8
import mock

from questgen import facts

from common.utils import testcase

from game.heroes.relations import EQUIPMENT_SLOT
from game.persons.relations import PERSON_TYPE
from game.persons.storage import persons_storage

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.mobs.storage import mobs_storage

from game.logic import create_test_map
from game.text_generation import get_vocabulary

from game.prototypes import TimePrototype
from game.quests.logic import QUESTS_BASE
from game.quests.writer import Writer

from game.actions.prototypes import ActionQuestPrototype, ActionIdlenessPrototype
# from game.quests.quests_builders.delivery import Delivery
# from game.quests.quests_builders.not_my_work import NotMyWork
# from game.quests.quests_builders.help import Help
# from game.quests.quests_builders.help_friend import HelpFriend
# from game.quests.quests_builders.interfere_enemy import InterfereEnemy
# from game.quests.quests_builders.search_smith import SearchSmith


class QuestsTestBase(testcase.TestCase):

    def setUp(self):
        super(QuestsTestBase, self).setUp()
        p1, p2, p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

        self.hero._model.money += 1
        self.hero.preferences.set_mob(mobs_storage.all()[0])
        self.hero.preferences.set_place(p1)
        self.hero.preferences.set_friend(p1.persons[0])
        self.hero.preferences.set_enemy(p2.persons[0])
        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.PLATE)
        self.hero.save()

        persons_storage.all()[0]._model.type = PERSON_TYPE.BLACKSMITH
        persons_storage.save_all()


class QuestsTest(QuestsTestBase):

    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()


def create_test_method(quest, quests):

    @mock.patch('questgen.quests.quests_base.QuestsBase._available_quests', lambda *argv, **kwargs: quests)
    @mock.patch('game.balance.constants.QUESTS_SPECIAL_FRACTION', 1.1)
    @mock.patch('game.map.roads.storage.WaymarksStorage.average_path_length', 9999)
    def quest_test_method(self):

        # defends from first quest rule
        self.hero.statistics.change_quests_done(1)
        self.hero.save()

        current_time = TimePrototype.get_current_time()

        while self.hero.actions.current_action.TYPE != ActionQuestPrototype.TYPE:
            self.storage.process_turn()
            current_time.increment_turn()

        self.complete_quest()

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionIdlenessPrototype.TYPE)

        # if quest == SearchSmith:
        #     self.assertTrue(self.hero.statistics.money_spend_for_artifacts > 0 or
        #                     self.hero.statistics.money_spend_for_sharpening > 0)

    return quest_test_method


for QuestClass in QUESTS_BASE.quests():

    quests = [QuestClass]

    # if QuestClass in (Help, HelpFriend, NotMyWork, InterfereEnemy):
    #     quests.append(Delivery)

    setattr(QuestsTest, 'test_%s' % QuestClass.TYPE, create_test_method(QuestClass, quests))




class RawQuestsTest(QuestsTestBase):

    def setUp(self):
        super(RawQuestsTest, self).setUp()
        self.vocabruary = get_vocabulary()

    def check_messages(self, knowledge_base):
        start_uid = knowledge_base.filter(facts.Start).next().uid

        table = {}
        for jump in knowledge_base.filter(facts.Jump):
            if jump.state_from not in table:
                table[jump.state_from] = []
            table[jump.state_from].append(jump)

        self._bruteforce(knowledge_base, [start_uid], table, [start_uid], processed=set())

    def _bruteforce(self, knowledge_base, path, table, starts, processed):
        current_state = knowledge_base[path[-1]]

        if current_state.uid in processed:
            return

        if not table.get(current_state.uid):
            return

        if isinstance(current_state, facts.Start):
            starts.append(current_state.type)

            writer = Writer(type=starts[-1], message=None, substitution={})
            self.assertTrue(writer.name_id() in self.vocabruary)
            self.assertTrue(writer.actor_id('initiator') in self.vocabruary)
            # self.assertTrue(writer.actor_id('initiator_position') in self.vocabruary)
            self.assertTrue(writer.actor_id('receiver') in self.vocabruary)
            # self.assertTrue(writer.actor_id('receiver_position') in self.vocabruary)

        # print current_state.uid
        for action in current_state.actions:
            if not isinstance(action, facts.Message):
                continue
            writer = Writer(type=starts[-1], message=action.id, substitution={})

            # print '--------'
            # print writer.journal_id()
            # print writer.diary_id()
            # print writer.action_id()

            self.assertTrue(writer.journal_id() in self.vocabruary or
                            writer.diary_id() in self.vocabruary or
                            writer.action_id() in self.vocabruary)

        for next_jump in table[current_state.uid]:
            if isinstance(next_jump, facts.Option):
                writer = Writer(type=starts[-1], message='choice', substitution={})
                self.assertTrue(writer.choice_variant_id(next_jump.type) in self.vocabruary)
                self.assertTrue(writer.current_choice_id(next_jump.type) in self.vocabruary)

            path.append(next_jump.state_to)
            self._bruteforce(knowledge_base, path, table,starts, processed )
            path.pop()

        if isinstance(current_state, facts.Start):
            starts.pop()

        processed.add(current_state.uid)


def create_test_messages_method(quest, quests):

    @mock.patch('game.heroes.prototypes.HeroPrototype.is_short_quest_path_required', False)
    @mock.patch('game.heroes.prototypes.HeroPrototype.is_first_quest_path_required', False)
    def quest_test_method(self):
        from questgen.selectors import Selector

        from game.quests.logic import get_knowledge_base
        from game.quests import uids

        knowledge_base = get_knowledge_base(self.hero)

        selector = Selector(knowledge_base)

        hero_uid = uids.hero(self.hero)

        start_place = selector.place_for(objects=(hero_uid,))

        quests_facts = QUESTS_BASE.create_start_quest(knowledge_base,
                                                      selector,
                                                      start_place=start_place,
                                                      excluded=[],
                                                      tags=('can_start', 'normal'))

        knowledge_base += quests_facts

        self.check_messages(knowledge_base)

    return quest_test_method


for QuestClass in QUESTS_BASE.quests():

    quests = [QuestClass]

    # if QuestClass in (Help, HelpFriend, NotMyWork, InterfereEnemy):
    #     quests.append(Delivery)

    setattr(RawQuestsTest, 'test_messages__%s' % QuestClass.TYPE, create_test_messages_method(QuestClass, quests))
