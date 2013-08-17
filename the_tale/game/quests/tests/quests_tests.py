# coding: utf-8
import mock

from common.utils import testcase

from game.heroes.relations import EQUIPMENT_SLOT
from game.persons.relations import PERSON_TYPE
from game.persons.storage import persons_storage

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.mobs.storage import mobs_storage

from game.logic import create_test_map
from game.prototypes import TimePrototype
from game.quests.quests_builders import QUESTS
from game.actions.prototypes import ActionQuestPrototype, ActionIdlenessPrototype
from game.quests.quests_generator.tests.helpers import patch_quests_list
from game.quests.quests_builders.delivery import Delivery
from game.quests.quests_builders.not_my_work import NotMyWork
from game.quests.quests_builders.help import Help
from game.quests.quests_builders.help_friend import HelpFriend
from game.quests.quests_builders.interfere_enemy import InterfereEnemy
from game.quests.quests_builders.search_smith import SearchSmith


class QuestsTest(testcase.TestCase):

    def setUp(self):
        super(QuestsTest, self).setUp()
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


    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()


def create_test_method(quest, quests):

    @patch_quests_list('game.quests.logic.QuestsSource', quests)
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

        if quest == SearchSmith:
            self.assertTrue(self.hero.statistics.money_spend_for_artifacts > 0 or
                            self.hero.statistics.money_spend_for_sharpening > 0)

    return quest_test_method


for QuestClass in QUESTS:

    quests = [QuestClass]

    if QuestClass in (Help, HelpFriend, NotMyWork, InterfereEnemy):
        quests.append(Delivery)

    setattr(QuestsTest, 'test_%s' % QuestClass.type(), create_test_method(QuestClass, quests))
