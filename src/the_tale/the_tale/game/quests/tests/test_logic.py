
import smart_imports

smart_imports.all()


class LogicTestsBase(utils_testcase.TestCase):

    def setUp(self):
        super(LogicTestsBase, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

        self.hero_uid = uids.hero(self.hero.id)

        self.knowledge_base = questgen_knowledge_base.KnowledgeBase()

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
        self.check_uids(self.knowledge_base.filter(questgen_facts.Place), places)
        self.check_uids(self.knowledge_base.filter(questgen_facts.Person), persons)
        self.check_uids(self.knowledge_base.filter(questgen_facts.LocatedIn), locations)
        self.check_uids(self.knowledge_base.filter(questgen_facts.Mob), mobs)
        self.check_uids(self.knowledge_base.filter(questgen_facts.PreferenceMob), prefered_mobs)
        self.check_uids(self.knowledge_base.filter(questgen_facts.PreferenceHometown), hometowns)
        self.check_uids(self.knowledge_base.filter(questgen_facts.PreferenceFriend), friends)
        self.check_uids(self.knowledge_base.filter(questgen_facts.ExceptBadBranches), bad_branches)
        self.check_uids(self.knowledge_base.filter(questgen_facts.PreferenceEnemy), enemies)
        self.check_uids(self.knowledge_base.filter(questgen_facts.ExceptGoodBranches), good_branches)
        self.check_uids(self.knowledge_base.filter(questgen_facts.PreferenceEquipmentSlot), equipment_slots)
        self.check_uids(self.knowledge_base.filter(questgen_facts.SocialConnection), social_connections)


class HeroQuestInfoTests(LogicTestsBase):

    def test_create_hero_info__all_properties(self):
        self.hero.level = 11

        self.hero.position.set_place(self.place_1)

        mob = mobs_storage.mobs.all()[0]
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.MOB, mob)

        place = self.place_1
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, place)

        friend = self.place_2.persons[0]
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.FRIEND, friend)

        enemy = self.place_2.persons[1]
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.ENEMY, enemy)

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, heroes_relations.EQUIPMENT_SLOT.HELMET)

        quests_region_center = self.place_2
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION, quests_region_center)

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION_SIZE, 17)

        interfered_person = self.place_3.persons[0]

        self.hero.quests.add_interfered_person(interfered_person.id)

        is_first_quest_path_required = random.choice((True, False))
        prefered_quest_markers = set((questgen_relations.OPTION_MARKERS.HONORABLE, questgen_relations.OPTION_MARKERS.AGGRESSIVE))

        self.hero.quests.update_history(quest_type='spying', turn_number=0)
        self.hero.quests.update_history(quest_type='hunt', turn_number=0)

        with mock.patch('the_tale.game.heroes.objects.Hero.is_first_quest_path_required', is_first_quest_path_required), \
                mock.patch('the_tale.game.heroes.objects.Hero.prefered_quest_markers', lambda hero: prefered_quest_markers):
            hero_info = logic.create_hero_info(self.hero)

        self.assertEqual(hero_info.id, self.hero.id)
        self.assertEqual(hero_info.level, self.hero.level)
        self.assertEqual(hero_info.position_place_id, self.hero.position.place.id)
        self.assertEqual(hero_info.preferences_mob_id, self.hero.preferences.mob.id)
        self.assertEqual(hero_info.preferences_place_id, self.hero.preferences.place.id)
        self.assertEqual(hero_info.preferences_friend_id, self.hero.preferences.friend.id)
        self.assertEqual(hero_info.preferences_enemy_id, self.hero.preferences.enemy.id)
        self.assertEqual(hero_info.preferences_equipment_slot, self.hero.preferences.equipment_slot)
        self.assertEqual(hero_info.preferences_quests_region_id, quests_region_center.id)
        self.assertEqual(hero_info.preferences_quests_region_size, 17)
        self.assertEqual(hero_info.interfered_persons, [interfered_person.id])
        self.assertEqual(hero_info.is_first_quest_path_required, is_first_quest_path_required)
        self.assertCountEqual(hero_info.excluded_quests, list(self.hero.quests.history.keys()))
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
        self.assertEqual(hero_info.preferences_quests_region_id, None)
        self.assertEqual(hero_info.preferences_quests_region_size, c.DEFAULT_QUESTS_REGION_SIZE)
        self.assertEqual(hero_info.interfered_persons, [])
        self.assertEqual(hero_info.is_first_quest_path_required, self.hero.is_first_quest_path_required)
        self.assertCountEqual(hero_info.excluded_quests, list(self.hero.quests.history.keys()))
        self.assertEqual(hero_info.prefered_quest_markers, set())
        self.assertEqual(hero_info.quests_priorities, self.hero.get_quests_priorities())

        self.check_serialization(hero_info)


class FactPlaceTests(LogicTestsBase):

    def test_no_midifier(self):
        self.assertTrue(self.place_1.modifier.is_NONE)

        fact = logic.fact_place(self.place_1)

        self.assertEqual(fact.type, questgen_relations.PLACE_TYPE.NONE)

    def test_active_midifier(self):
        self.place_1.set_modifier(places_modifiers.CITY_MODIFIERS.HOLY_CITY)
        self.place_1.attrs.modifier_holy_city = c.PLACE_TYPE_ENOUGH_BORDER

        self.assertTrue(self.place_1.is_modifier_active())

        fact = logic.fact_place(self.place_1)

        self.assertEqual(fact.type, questgen_relations.PLACE_TYPE.HOLY_CITY)

    def test_not_active_midifier(self):
        self.place_1.set_modifier(places_modifiers.CITY_MODIFIERS.HOLY_CITY)
        self.place_1.attrs.modifier_holy_city = 0

        self.assertFalse(self.place_1.is_modifier_active())

        fact = logic.fact_place(self.place_1)

        self.assertEqual(fact.type, questgen_relations.PLACE_TYPE.NONE)


class FillPlacesTest(LogicTestsBase):

    def test(self):

        f_place_2 = logic.fact_place(self.place_2)
        f_place_3 = logic.fact_place(self.place_3)

        logic.fill_places(self.knowledge_base,
                          [self.place_2, self.place_3])

        self.check_facts(places=[f_place_2, f_place_3])


class SetupPlacesTest(LogicTestsBase):

    def setUp(self):
        super().setUp()

        self.w_1_2 = navigation_logic.manhattan_distance(self.place_1.x, self.place_1.y, self.place_2.x, self.place_2.y)
        self.w_1_3 = navigation_logic.manhattan_distance(self.place_1.x, self.place_1.y, self.place_3.x, self.place_3.y)
        self.w_2_3 = navigation_logic.manhattan_distance(self.place_2.x, self.place_2.y, self.place_3.x, self.place_3.y)

    def test_prerequiries(self):
        self.assertTrue(self.w_1_2 > self.w_1_3 == self.w_2_3)

    def test_region_size(self):
        self.hero.position.set_place(self.place_1)

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION, self.place_1)
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION_SIZE, 2)

        hero_info = self.get_hero_info()
        hero_info.is_first_quest_path_required = False

        logic.setup_places(self.knowledge_base, hero_info)

        self.check_facts(places=[logic.fact_place(self.place_1),
                                 logic.fact_place(self.place_3)],
                         locations=[questgen_facts.LocatedIn(object=uids.hero(hero_info.id),
                                                             place=logic.fact_place(self.place_1).uid)])

    def test_region_size__add_hero_position(self):
        self.hero.position.set_place(self.place_2)

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION, self.place_1)
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION_SIZE, 2)

        hero_info = self.get_hero_info()
        hero_info.is_first_quest_path_required = False

        logic.setup_places(self.knowledge_base, hero_info)

        self.check_facts(places=[logic.fact_place(self.place_1),
                                 logic.fact_place(self.place_2),
                                 logic.fact_place(self.place_3)],
                         locations=[questgen_facts.LocatedIn(object=uids.hero(hero_info.id),
                                                             place=logic.fact_place(self.place_2).uid)])

    def test_region_size_maximum(self):
        self.hero.position.set_place(self.place_2)

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION, self.place_1)
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION_SIZE, 3)

        hero_info = self.get_hero_info()
        hero_info.is_first_quest_path_required = False

        logic.setup_places(self.knowledge_base, hero_info)

        self.check_facts(places=[logic.fact_place(self.place_1),
                                 logic.fact_place(self.place_2),
                                 logic.fact_place(self.place_3)],
                         locations=[questgen_facts.LocatedIn(object=uids.hero(hero_info.id),
                                                             place=logic.fact_place(self.place_2).uid)])


class SetupPreferencesTest(LogicTestsBase):

    def test_no_preferences(self):
        logic.setup_preferences(self.knowledge_base, self.get_hero_info())
        self.check_facts()

    def test_mob(self):
        mob = mobs_storage.mobs.all()[0]
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.MOB, mob)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        f_mob = logic.fact_mob(mob)
        self.check_facts(mobs=[f_mob],
                         prefered_mobs=[questgen_facts.PreferenceMob(object=self.hero_uid, mob=f_mob.uid)])

    def test_place(self):
        place = self.place_1
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, place)

        f_place = logic.fact_place(place)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         hometowns=[questgen_facts.PreferenceHometown(object=self.hero_uid, place=f_place.uid)])

    def test_place__second_setup(self):
        place = self.place_1
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, place)

        f_place = logic.fact_place(place)
        self.knowledge_base += f_place

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         hometowns=[questgen_facts.PreferenceHometown(object=self.hero_uid, place=f_place.uid)])

    def test_friend(self):
        place = self.place_2
        person = place.persons[0]

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.FRIEND, person)

        f_place = logic.fact_place(place)
        f_person = logic.fact_person(person)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         persons=[f_person],
                         friends=[questgen_facts.PreferenceFriend(object=self.hero_uid, person=f_person.uid)],
                         bad_branches=[questgen_facts.ExceptBadBranches(object=f_person.uid)])

    def test_friend__second_setup(self):
        place = self.place_2
        person = place.persons[0]

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.FRIEND, person)

        f_place = logic.fact_place(place)
        f_person = logic.fact_person(person)

        self.knowledge_base += f_place
        self.knowledge_base += f_person

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         persons=[f_person],
                         friends=[questgen_facts.PreferenceFriend(object=self.hero_uid, person=f_person.uid)],
                         bad_branches=[questgen_facts.ExceptBadBranches(object=f_person.uid)])

    def test_enemy(self):
        place = self.place_2
        person = place.persons[0]

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.ENEMY, person)

        f_place = logic.fact_place(place)
        f_person = logic.fact_person(person)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         persons=[f_person],
                         enemies=[questgen_facts.PreferenceEnemy(object=self.hero_uid, person=f_person.uid)],
                         good_branches=[questgen_facts.ExceptGoodBranches(object=f_person.uid)])

    def test_enemy__second_setup(self):
        place = self.place_2
        person = place.persons[0]

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.ENEMY, person)

        f_place = logic.fact_place(place)
        f_person = logic.fact_person(person)

        self.knowledge_base += f_place
        self.knowledge_base += f_person

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(places=[f_place],
                         persons=[f_person],
                         enemies=[questgen_facts.PreferenceEnemy(object=self.hero_uid, person=f_person.uid)],
                         good_branches=[questgen_facts.ExceptGoodBranches(object=f_person.uid)])

    def test_equipment_slot(self):
        slot = heroes_relations.EQUIPMENT_SLOT.HELMET

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, slot)

        logic.setup_preferences(self.knowledge_base, self.get_hero_info())

        self.check_facts(equipment_slots=[questgen_facts.PreferenceEquipmentSlot(object=self.hero_uid, equipment_slot=slot.value)])


class SetupPersonsTest(LogicTestsBase):

    def test_no_social_connections(self):
        self.hero.position.set_place(self.place_1)
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION_SIZE, 2)

        hero_info = self.get_hero_info()
        hero_info.is_first_quest_path_required = False

        logic.setup_places(self.knowledge_base, hero_info)
        logic.setup_persons(self.knowledge_base, hero_info)
        logic.setup_social_connections(self.knowledge_base)

        self.check_facts(places=[logic.fact_place(self.place_1),
                                 logic.fact_place(self.place_3)],
                         persons=[logic.fact_person(person)
                                  for person in persons_storage.persons.all()
                                  if person.place_id != self.place_2.id],
                         locations=[logic.fact_located_in(person)
                                    for person in persons_storage.persons.all()
                                    if person.place_id != self.place_2.id] +
                                   [questgen_facts.LocatedIn(object=uids.hero(hero_info.id),
                                                             place=logic.fact_place(self.place_1).uid)],
                         social_connections=[])

    def test_social_connections(self):
        persons_1 = self.place_1.persons
        persons_2 = self.place_2.persons
        persons_3 = self.place_3.persons

        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.random(), persons_1[0], persons_3[0])
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.random(), persons_1[1], persons_2[0])
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.random(), persons_3[0], persons_2[0])
        persons_logic.create_social_connection(persons_relations.SOCIAL_CONNECTION_TYPE.random(), persons_3[1], persons_2[1])

        self.hero.position.set_place(self.place_1)
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.QUESTS_REGION_SIZE, 2)

        hero_info = self.get_hero_info()
        hero_info.is_first_quest_path_required = False

        logic.setup_places(self.knowledge_base, hero_info)
        logic.setup_persons(self.knowledge_base, self.get_hero_info())
        logic.setup_social_connections(self.knowledge_base)

        expected_connections = []

        for person in persons_storage.persons.all():
            if person.place_id == self.place_2.id:
                continue

            for connection_type, connected_person_id in persons_storage.social_connections.get_person_connections(person):
                connected_person = persons_storage.persons[connected_person_id]
                if connected_person.place_id == self.place_2.id:
                    continue
                expected_connections.append(logic.fact_social_connection(connection_type, uids.person(person.id), uids.person(connected_person.id)))

        self.check_facts(places=[logic.fact_place(self.place_1),
                                 logic.fact_place(self.place_3)],
                         persons=[logic.fact_person(person)
                                  for person in persons_storage.persons.all()
                                  if person.place_id != self.place_2.id],
                         locations=[logic.fact_located_in(person)
                                    for person in persons_storage.persons.all()
                                    if person.place_id != self.place_2.id] +
                                   [questgen_facts.LocatedIn(object=uids.hero(hero_info.id),
                                                             place=logic.fact_place(self.place_1).uid)],
                         social_connections=expected_connections)
