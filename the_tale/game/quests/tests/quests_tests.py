# coding: utf-8

from common.utils.testcase import TestCase

from game.heroes.bag import SLOTS
from game.persons.models import PERSON_TYPE
from game.persons.storage import persons_storage

from game.logic import create_test_bundle, create_test_map
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


class QuestsTest(TestCase):

    def setUp(self):
        p1, p2, p3 = create_test_map()

        self.bundle = create_test_bundle('QuestActionTest')
        self.hero = self.bundle.tests_get_hero()
        self.action_idl = self.bundle.tests_get_last_action()

        self.hero.model.money += 1
        self.hero.preferences.set_mob_id('rat')
        self.hero.preferences.set_place_id(p1.id)
        self.hero.preferences.set_friend_id(p1.persons[0].id)
        self.hero.preferences.set_enemy_id(p2.persons[0].id)
        self.hero.preferences.set_equipment_slot(SLOTS.PLATE)
        self.hero.save()

        persons_storage.all()[0].model.type = PERSON_TYPE.BLACKSMITH
        persons_storage.save_all()


    def tearDown(self):
        pass

    def complete_quest(self):
        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.bundle.process_turn()
            current_time.increment_turn()


def create_test_method(quest, quests):

    @patch_quests_list('game.quests.logic.QuestsSource', quests)
    def quest_test_method(self):

        current_time = TimePrototype.get_current_time()

        while self.bundle.tests_get_last_action().TYPE != ActionQuestPrototype.TYPE:
            self.bundle.process_turn()
            current_time.increment_turn()

        self.complete_quest()

        self.assertEqual(self.bundle.tests_get_last_action().TYPE, ActionIdlenessPrototype.TYPE)

        if quest == SearchSmith:
            hero = self.bundle.tests_get_hero()
            self.assertTrue(hero.statistics.money_spend_for_artifacts > 0 or
                            hero.statistics.money_spend_for_sharpening > 0)

    return quest_test_method


for QuestClass in QUESTS:

    quests = [QuestClass]

    if QuestClass in (Help, HelpFriend, NotMyWork, InterfereEnemy):
        quests.append(Delivery)

    setattr(QuestsTest, 'test_%s' % QuestClass.type(), create_test_method(QuestClass, quests))
