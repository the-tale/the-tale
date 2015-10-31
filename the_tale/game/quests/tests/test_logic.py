# coding: utf-8
import contextlib
import random

import mock

from questgen.knowledge_base import KnowledgeBase
from questgen import facts
from questgen import relations as questgen_relations

from dext.common.utils import s11n

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import logic as persons_logic

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.map.roads.storage import waymarks_storage

from the_tale.game.heroes.relations import EQUIPMENT_SLOT

from the_tale.game.quests import uids
from the_tale.game.quests import logic
from the_tale.game.quests import relations


class LogicTestsBase(testcase.TestCase):

    def setUp(self):
        super(LogicTestsBase, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        self.hero_uid = uids.hero(self.hero.id)

        self.knowledge_base = KnowledgeBase()


    def get_hero_info(self):
        return logic.create_hero_info(self.hero)


    def check_uids(self, left, right):
        self.assertEqual(set(f.uid for f in left), set(f.uid for f in right))

    def check_facts(self,
                    places=[],
                    persons=[],
                    locations=[],
                    mobs=[],
                    prefered_mobs=[],
                    hometowns=[],
                    friends=[],
                    bad_branches=[],
                    enemies=[],
                    good_branches=[],
                    equipment_slots=[],
                    social_connections=[]):
        self.check_uids(self.knowledge_base.filter(facts.Place), places)
        self.check_uids(self.knowledge_base.filter(facts.Person), persons)
        self.check_uids(self.knowledge_base.filter(facts.LocatedIn), locations)
        self.check_uids(self.knowledge_base.filter(facts.Mob), mobs)
        self.check_uids(self.knowledge_base.filter(facts.PreferenceMob), prefered_mobs)
        self.check_uids(self.knowledge_base.filter(facts.PreferenceHometown), hometowns)
        self.check_uids(self.knowledge_base.filter(facts.PreferenceFriend), friends)
        self.check_uids(self.knowledge_base.filter(facts.ExceptBadBranches), bad_branches)
        self.check_uids(self.knowledge_base.filter(facts.PreferenceEnemy), enemies)
        self.check_uids(self.knowledge_base.filter(facts.ExceptGoodBranches), good_branches)
        self.check_uids(self.knowledge_base.filter(facts.PreferenceEquipmentSlot), equipment_slots)
        self.check_uids(self.knowledge_base.filter(facts.SocialConnection), social_connections)


class HeroQuestInfoTests(LogicTestsBase):

    def test_create_hero_info__all_properties(self):
        self.hero.level = 11

        self.hero.position.set_place(self.place_1)

        mob = mobs_storage.all()[0]
        self.hero.preferences.set_mob(mob)

        place = self.place_1
        self.hero.preferences.set_place(place)

        friend = self.place_2.persons[0]
        self.hero.preferences.set_friend(friend)

        enemy = self.place_2.persons[1]
        self.hero.preferences.set_enemy(enemy)

        self.hero.preferences.set_equipment_slot(EQUIPMENT_SLOT.HELMET)

        interfered_person = self.place_3.persons[0]

        self.hero.quests.add_interfered_person(interfered_person.id)

        is_first_quest_path_required = random.choice((True, False))
        is_short_quest_path_required = random.choice((True, False))
        prefered_quest_markers = set((questgen_relations.OPTION_MARKERS.HONORABLE, questgen_relations.OPTION_MARKERS.AGGRESSIVE))

        self.hero.quests.update_history(quest_type='spying', turn_number=0)
        self.hero.quests.update_history(quest_type='hunt', turn_number=0)

        with contextlib.nested(
                mock.patch('the_tale.game.heroes.objects.Hero.is_first_quest_path_required', is_first_quest_path_required),
                mock.patch('the_tale.game.heroes.objects.Hero.is_short_quest_path_required', is_short_quest_path_required),
                mock.patch('the_tale.game.heroes.objects.Hero.prefered_quest_markers', lambda hero: prefered_quest_markers) ):
            hero_info = logic.create_hero_info(self.hero)

        self.assertEqual(hero_info.id, self.hero.id)
        self.assertEqual(hero_info.level, self.hero.level)
        self.assertEqual(hero_info.position_place_id, self.hero.position.place.id)
        self.assertEqual(hero_info.preferences_mob_id, self.hero.preferences.mob.id)
        self.assertEqual(hero_info.preferences_place_id, self.hero.preferences.place.id)
        self.assertEqual(hero_info.preferences_friend_id, self.hero.preferences.friend.id)
        self.assertEqual(hero_info.preferences_enemy_id, self.hero.preferences.enemy.id)
        self.assertEqual(hero_info.preferences_equipment_slot, self.hero.preferences.equipment_slot)
        self.assertEqual(hero_info.interfered_persons, [interfered_person.id])
        self.assertEqual(hero_info.is_first_quest_path_required, is_first_quest_path_required)
        self.assertEqual(hero_info.is_short_quest_path_required, is_short_quest_path_required)
        self.assertItemsEqual(hero_info.excluded_quests, self.hero.quests.history.keys())
        self.assertEqual(hero_info.prefered_quest_markers, prefered_quest_markers)
        self.assertEqual(hero_info.quests_priorities, self.hero.get_quests_priorities())

        self.check_serialization(hero_info)

    def test_create_hero_info__no_properties(self):
        hero_info = logic.create_hero_info(self.hero)

        self.assertEqual(hero_info.id, self.hero.id)
        self.assertEqual(hero_info.level, self.hero.level)
        self.assertEqual(hero_info.position_place_id, self.hero.position.place.id)
        self.assertEqual(hero_info.preferences_mob_id, None)
        self.assertEqual(hero_info.preferences_place_id, None)
        self.assertEqual(hero_info.preferences_friend_id, None)
        self.assertEqual(hero_info.preferences_enemy_id, None)
        self.assertEqual(hero_info.preferences_equipment_slot, None)
        self.assertEqual(hero_info.interfered_persons, [])
        self.assertEqual(hero_info.is_first_quest_path_required, self.hero.is_first_quest_path_required)
        self.assertEqual(hero_info.is_short_quest_path_required, self.hero.is_short_quest_path_required)
        self.assertItemsEqual(hero_info.excluded_quests, self.hero.quests.history.keys())
        self.assertEqual(hero_info.prefered_quest_markers, set())
        self.assertEqual(hero_info.quests_priorities, self.hero.get_quests_priorities())

        self.check_serialization(hero_info)




class FillPlacesTest(LogicTestsBase):

    def test_prerequiries(self):
        w_1_2 = waymarks_storage.look_for_road(self.place_1, self.place_2).length
        w_1_3 = waymarks_storage.look_for_road(self.place_1, self.place_3).length
        w_2_3 = waymarks_storage.look_for_road(self.place_2, self.place_3).length

        self.assertTrue(w_1_3 > w_1_2 > w_2_3)

    def test_radius(self):
        self.hero.position.set_place(self.place_1)

        logic.fill_places(self.knowledge_base, self.get_hero_info(), waymarks_storage.look_for_road(self.place_1, self.place_2).length)

        self.check_facts(places=[logic.fact_place(self.place_1), logic.fact_place(self.place_2)])


    def test_maximum_radius(self):
        self.hero.position.set_place(self.place_1)

        logic.fill_places(self.knowledge_base, self.get_hero_info(), waymarks_storage.look_for_road(self.place_1, self.place_3).length)

        self.check_facts(places=[logic.fact_place(self.place_1), logic.fact_place(self.place_2), logic.fact_place(self.place_3)])

    def test_second_fill(self):
        self.hero.position.set_place(self.place_1)

        f_place_1 = logic.fact_place(self.place_1)
        f_place_2 = logic.fact_place(self.place_2)

        logic.fill_places(self.knowledge_base, self.get_hero_info(), waymarks_storage.look_for_road(self.place_1, self.place_2).length)

        self.check_facts(places=[f_place_1, f_place_2])

    def test_diameter(self):
        self.hero.position.set_place(self.place_2)

        f_place_2 = logic.fact_place(self.place_2)
        f_place_3 = logic.fact_place(self.place_3)

        logic.fill_places(self.knowledge_base, self.get_hero_info(), waymarks_storage.look_for_road(self.place_1, self.place_3).length - 1)

        self.check_facts(places=[f_place_2, f_place_3])

    def test_diameter__full(self):
        self.hero.position.set_place(self.place_2)

        f_place_1 = logic.fact_place(self.place_1)
        f_place_2 = logic.fact_place(self.place_2)
        f_place_3 = logic.fact_place(self.place_3)

        logic.fill_places(self.knowledge_base, self.get_hero_info(), waymarks_storage.look_for_road(self.place_1, self.place_3).length + 1)

        self.check_facts(places=[f_place_2, f_place_3, f_place_1])


class SetupPreferencesTest(LogicTestsBase):

    def test_no_preferences(self):
        logic.setup_preferences(self.knowledge_base, self.get_hero_info())
        self.check_facts()

    def test_mob(self):
        mob = mobs_storage.all()[0]
        self.hero.preferences.set_mob(mob)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        f_mob = logic.fact_mob(mob)
        self.check_facts(mobs=[f_mob],
                         prefered_mobs=[facts.PreferenceMob(object=self.hero_uid, mob=f_mob.uid)])

    def test_place(self):
        place = self.place_1
        self.hero.preferences.set_place(place)

        f_place = logic.fact_place(place)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         hometowns=[facts.PreferenceHometown(object=self.hero_uid, place=f_place.uid)])

    def test_place__second_setup(self):
        place = self.place_1
        self.hero.preferences.set_place(place)

        f_place = logic.fact_place(place)
        self.knowledge_base += f_place

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         hometowns=[facts.PreferenceHometown(object=self.hero_uid, place=f_place.uid)])

    def test_friend(self):
        place = self.place_2
        person = place.persons[0]

        self.hero.preferences.set_friend(person)

        f_place = logic.fact_place(place)
        f_person = logic.fact_person(person)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         persons=[f_person],
                         friends=[facts.PreferenceFriend(object=self.hero_uid, person=f_person.uid)],
                         bad_branches=[facts.ExceptBadBranches(object=f_person.uid)])

    def test_friend__second_setup(self):
        place = self.place_2
        person = place.persons[0]

        self.hero.preferences.set_friend(person)

        f_place = logic.fact_place(place)
        f_person = logic.fact_person(person)

        self.knowledge_base += f_place
        self.knowledge_base += f_person

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         persons=[f_person],
                         friends=[facts.PreferenceFriend(object=self.hero_uid, person=f_person.uid)],
                         bad_branches=[facts.ExceptBadBranches(object=f_person.uid)])

    def test_enemy(self):
        place = self.place_2
        person = place.persons[0]

        self.hero.preferences.set_enemy(person)

        f_place = logic.fact_place(place)
        f_person = logic.fact_person(person)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         persons=[f_person],
                         enemies=[facts.PreferenceEnemy(object=self.hero_uid, person=f_person.uid)],
                         good_branches=[facts.ExceptGoodBranches(object=f_person.uid)])

    def test_enemy__second_setup(self):
        place = self.place_2
        person = place.persons[0]

        self.hero.preferences.set_enemy(person)

        f_place = logic.fact_place(place)
        f_person = logic.fact_person(person)

        self.knowledge_base += f_place
        self.knowledge_base += f_person

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         persons=[f_person],
                         enemies=[facts.PreferenceEnemy(object=self.hero_uid, person=f_person.uid)],
                         good_branches=[facts.ExceptGoodBranches(object=f_person.uid)])

    def test_equipment_slot(self):
        slot = EQUIPMENT_SLOT.HELMET

        self.hero.preferences.set_equipment_slot(slot)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(equipment_slots=[facts.PreferenceEquipmentSlot(object=self.hero_uid, equipment_slot=slot.value)])



class SetupPersonsTest(LogicTestsBase):

    def test_no_social_connections(self):
        self.hero.position.set_place(self.place_1)

        logic.fill_places(self.knowledge_base, self.get_hero_info(), waymarks_storage.look_for_road(self.place_1, self.place_2).length)
        logic.setup_persons(self.knowledge_base, self.get_hero_info())
        logic.setup_social_connections(self.knowledge_base)

        self.check_facts(places=[logic.fact_place(self.place_1), logic.fact_place(self.place_2)],
                         persons=[logic.fact_person(person) for person in persons_storage.persons_storage.all() if person.place_id != self.place_3.id],
                         locations=[logic.fact_located_in(person) for person in persons_storage.persons_storage.all() if person.place_id != self.place_3.id],
                         social_connections=[])


    def test_social_connections(self):
        persons_logic.sync_social_connections()

        self.hero.position.set_place(self.place_1)

        logic.fill_places(self.knowledge_base, self.get_hero_info(), waymarks_storage.look_for_road(self.place_1, self.place_2).length)
        logic.setup_persons(self.knowledge_base, self.get_hero_info())
        logic.setup_social_connections(self.knowledge_base)

        expected_connections = []

        for person in persons_storage.persons_storage.all():
            if person.place_id == self.place_3.id:
                continue
            for connection_type, connected_person_id in persons_storage.social_connections.get_person_connections(person):
                connected_person = persons_storage.persons_storage[connected_person_id]
                if connected_person.place_id == self.place_3.id:
                    continue
                expected_connections.append(logic.fact_social_connection(connection_type, uids.person(person.id), uids.person(connected_person.id)))

        self.check_facts(places=[logic.fact_place(self.place_1), logic.fact_place(self.place_2)],
                         persons=[logic.fact_person(person) for person in persons_storage.persons_storage.all() if person.place_id != self.place_3.id],
                         locations=[logic.fact_located_in(person) for person in persons_storage.persons_storage.all() if person.place_id != self.place_3.id],
                         social_connections=expected_connections)
