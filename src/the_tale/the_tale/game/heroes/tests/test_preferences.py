
import datetime

from the_tale.common.utils.testcase import TestCase

from the_tale.game.logic import create_test_map

from the_tale.game.mobs import logic as mobs_logic
from the_tale.game.mobs import storage as mobs_storage
from the_tale.game.mobs import relations as mobs_relations

from the_tale.game.logic_storage import LogicStorage

from the_tale.game import relations as game_relations

from the_tale.game.persons import storage as persons_storage

from the_tale.game.heroes import relations
from the_tale.game.heroes.preferences import HeroPreferences

from .. import logic


class HeroPreferencesEnergyRegenerationTypeTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE

    def setUp(self):
        super(HeroPreferencesEnergyRegenerationTypeTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE.level_required
        self.hero.preferences.set(relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, relations.ENERGY_REGENERATION.SACRIFICE)
        logic.save_hero(self.hero)

    def test_preferences_serialization(self):
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, relations.ENERGY_REGENERATION.PRAY)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.energy_regeneration_type, relations.ENERGY_REGENERATION.PRAY)


class HeroPreferencesMobTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.MOB

    def setUp(self):
        super(HeroPreferencesMobTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.MOB.level_required
        logic.save_hero(self.hero)

        self.mob_uuid = mobs_storage.mobs.get_available_mobs_list(level=self.hero.level)[0].uuid
        self.mob_2_uuid = mobs_storage.mobs.get_available_mobs_list(level=self.hero.level)[1].uuid

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.MOB, mobs_storage.mobs.all()[0])
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        mob = mobs_storage.mobs.all()[0]
        self.hero.preferences.set(relations.PREFERENCE_TYPE.MOB, mob)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.mob.id, mob.id)

    def test_reset_mob_when_it_disabled(self):
        mob_record = mobs_storage.mobs.all()[0]
        self.hero.preferences.set(relations.PREFERENCE_TYPE.MOB, mob_record)

        self.assertEqual(self.hero.preferences.mob, mob_record)

        mob_record.state = mobs_relations.MOB_RECORD_STATE.DISABLED
        mobs_logic.save_mob_record(mob_record)

        self.assertEqual(self.hero.preferences.mob, None)



class HeroPreferencesPlaceTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.PLACE

    def setUp(self):
        super(HeroPreferencesPlaceTest, self).setUp()

        self.place, self.place_2, self.place_3 = create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.PLACE.level_required
        logic.save_hero(self.hero)

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.place.id, self.place.id)


    def test_get_citizens_number(self):
        hero_1 = self.hero
        hero_1.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_1)

        account_2 = self.accounts_factory.create_account()
        hero_2 = logic.load_hero(account_id=account_2.id)
        hero_2.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        logic.save_hero(hero_2)

        account_3 = self.accounts_factory.create_account()
        hero_3 = logic.load_hero(account_id=account_3.id)
        hero_3.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_3)

        account_4 = self.accounts_factory.create_account(is_fast=True)
        hero_4 = logic.load_hero(account_id=account_4.id)
        hero_4.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        logic.save_hero(hero_4)

        account_5 = self.accounts_factory.create_account()
        hero_5 = logic.load_hero(account_id=account_5.id)
        hero_5.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_5)

        account_6 = self.accounts_factory.create_account()
        hero_6 = logic.load_hero(account_id=account_6.id)
        hero_6.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place_2)
        hero_6.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_6)

        account_7 = self.accounts_factory.create_account()
        hero_7 = logic.load_hero(account_id=account_7.id)
        hero_7.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        hero_7.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        logic.save_hero(hero_7)

        self.assertEqual(set([h.id for h in HeroPreferences.get_citizens_of(self.place, all=False)]), set([hero_1.id, hero_3.id]))
        self.assertEqual(set([h.id for h in HeroPreferences.get_citizens_of(self.place, all=True)]), set([hero_1.id, hero_2.id, hero_3.id]))


    def test_count_habit_values(self):
        hero_1 = self.hero
        hero_1.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.habit_honor.change(-1)
        hero_1.habit_peacefulness.change(1)
        logic.save_hero(hero_1)

        account_2 = self.accounts_factory.create_account()
        hero_2 = logic.load_hero(account_id=account_2.id)
        hero_2.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        hero_2.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_2.habit_honor.change(2)
        hero_2.habit_peacefulness.change(-2)
        logic.save_hero(hero_2)

        account_3 = self.accounts_factory.create_account()
        hero_3 = logic.load_hero(account_id=account_3.id)
        hero_3.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place_2)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_3.habit_honor.change(-4)
        hero_3.habit_peacefulness.change(4)
        logic.save_hero(hero_3)

        account_4 = self.accounts_factory.create_account()
        hero_4 = logic.load_hero(account_id=account_4.id)
        hero_4.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        hero_4.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_4.habit_honor.change(8)
        hero_4.habit_peacefulness.change(-8)
        logic.save_hero(hero_4)

        self.assertEqual(HeroPreferences.count_habit_values(self.place, all=False), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=False), ((0, -4), (4, 0)))

        self.assertEqual(HeroPreferences.count_habit_values(self.place, all=True), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=True), ((0, -4), (4, 0)))



class HeroPreferencesFriendTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.FRIEND

    def setUp(self):
        super(HeroPreferencesFriendTest, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.FRIEND.level_required
        logic.save_hero(self.hero)

        self.friend = self.place_1.persons[0]
        self.friend_2 = self.place_2.persons[0]
        self.enemy = self.place_3.persons[0]

        self.friend_id = self.friend.id
        self.friend_2_id = self.friend_2.id
        self.enemy_id = self.enemy.id

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.FRIEND, persons_storage.persons[self.friend_id])
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        friend = persons_storage.persons[self.friend_id]

        self.hero.preferences.set(relations.PREFERENCE_TYPE.FRIEND, friend)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.friend.id, friend.id)


    def test_get_friends_number(self):
        hero_1 = self.hero

        account_2 = self.accounts_factory.create_account()
        hero_2 = logic.load_hero(account_id=account_2.id)

        account_3 = self.accounts_factory.create_account()
        hero_3 = logic.load_hero(account_id=account_3.id)

        person_1 = self.place_1.persons[0]
        person_2 = self.place_1.persons[-1]

        hero_1.preferences.set(relations.PREFERENCE_TYPE.FRIEND, person_1)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_1)

        hero_2.preferences.set(relations.PREFERENCE_TYPE.FRIEND, person_1)
        logic.save_hero(hero_2)

        hero_3.preferences.set(relations.PREFERENCE_TYPE.FRIEND, person_1)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_3)

        account_4 = self.accounts_factory.create_account(is_fast=True)
        hero_4 = logic.load_hero(account_id=account_4.id)
        hero_4.preferences.set(relations.PREFERENCE_TYPE.FRIEND, person_1)
        logic.save_hero(hero_4)

        account_5 = self.accounts_factory.create_account()
        hero_5 = logic.load_hero(account_id=account_5.id)
        hero_5.preferences.set(relations.PREFERENCE_TYPE.FRIEND, person_1)
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_5)

        account_6 = self.accounts_factory.create_account()
        hero_6 = logic.load_hero(account_id=account_6.id)
        hero_6.preferences.set(relations.PREFERENCE_TYPE.FRIEND, person_1)
        hero_6.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        logic.save_hero(hero_6)

        self.assertEqual(set([h.id for h in HeroPreferences.get_friends_of(person_1, all=False)]), set([hero_1.id, hero_3.id]))
        self.assertEqual(set([h.id for h in HeroPreferences.get_friends_of(person_1, all=True)]), set([hero_1.id, hero_2.id, hero_3.id]))


    def test_count_habit_values(self):
        hero_1 = self.hero
        hero_1.preferences.set(relations.PREFERENCE_TYPE.FRIEND, self.friend)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.habit_honor.change(-1)
        hero_1.habit_peacefulness.change(1)
        logic.save_hero(hero_1)

        account_2 = self.accounts_factory.create_account()
        hero_2 = logic.load_hero(account_id=account_2.id)
        hero_2.preferences.set(relations.PREFERENCE_TYPE.FRIEND, self.friend)
        hero_2.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_2.habit_honor.change(2)
        hero_2.habit_peacefulness.change(-2)
        logic.save_hero(hero_2)

        account_3 = self.accounts_factory.create_account()
        hero_3 = logic.load_hero(account_id=account_3.id)
        hero_3.preferences.set(relations.PREFERENCE_TYPE.FRIEND, self.friend_2)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_3.habit_honor.change(-4)
        hero_3.habit_peacefulness.change(4)
        logic.save_hero(hero_3)

        account_4 = self.accounts_factory.create_account()
        hero_4 = logic.load_hero(account_id=account_4.id)
        hero_4.preferences.set(relations.PREFERENCE_TYPE.FRIEND, self.friend)
        hero_4.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_4.habit_honor.change(8)
        hero_4.habit_peacefulness.change(-8)
        logic.save_hero(hero_4)

        self.assertEqual(HeroPreferences.count_habit_values(self.place_1, all=False), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=False), ((0, -4), (4, 0)))

        self.assertEqual(HeroPreferences.count_habit_values(self.place_1, all=True), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=True), ((0, -4), (4, 0)))




class HeroPreferencesEnemyTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.ENEMY

    def setUp(self):
        super(HeroPreferencesEnemyTest, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.ENEMY.level_required
        logic.save_hero(self.hero)

        self.enemy = self.place_1.persons[0]
        self.enemy_2 = self.place_2.persons[0]
        self.friend = self.place_3.persons[0]

        self.enemy_id = self.enemy.id
        self.enemy_2_id = self.enemy_2.id
        self.friend_id =  self.friend.id

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.ENEMY, persons_storage.persons[self.enemy_id])
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        enemy = persons_storage.persons[self.enemy_id]

        self.hero.preferences.set(relations.PREFERENCE_TYPE.ENEMY, enemy)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.enemy.id, enemy.id)


    def test_get_enemies_number(self):
        hero_1 = self.hero

        account_2 = self.accounts_factory.create_account()
        hero_2 = logic.load_hero(account_id=account_2.id)

        account_3 = self.accounts_factory.create_account()
        hero_3 = logic.load_hero(account_id=account_3.id)

        person_1 = self.place_1.persons[0]
        person_2 = self.place_1.persons[-1]

        hero_1.preferences.set(relations.PREFERENCE_TYPE.ENEMY, person_1)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_1)

        hero_2.preferences.set(relations.PREFERENCE_TYPE.ENEMY, person_1)
        logic.save_hero(hero_2)

        hero_3.preferences.set(relations.PREFERENCE_TYPE.ENEMY, person_1)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_3)

        account_4 = self.accounts_factory.create_account(is_fast=True)
        hero_4 = logic.load_hero(account_id=account_4.id)
        hero_4.preferences.set(relations.PREFERENCE_TYPE.ENEMY, person_1)
        logic.save_hero(hero_4)

        account_5 = self.accounts_factory.create_account()
        hero_5 = logic.load_hero(account_id=account_5.id)
        hero_5.preferences.set(relations.PREFERENCE_TYPE.ENEMY, person_1)
        hero_5.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        logic.save_hero(hero_5)

        account_6 = self.accounts_factory.create_account()
        hero_6 = logic.load_hero(account_id=account_6.id)
        hero_6.preferences.set(relations.PREFERENCE_TYPE.ENEMY, person_1)
        hero_6.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        logic.save_hero(hero_6)

        self.assertEqual(set([h.id for h in HeroPreferences.get_enemies_of(person_1, all=False)]), set([hero_1.id, hero_3.id]))
        self.assertEqual(set([h.id for h in HeroPreferences.get_enemies_of(person_1, all=True)]), set([hero_1.id, hero_2.id, hero_3.id]))


    def test_count_habit_values(self):
        hero_1 = self.hero
        hero_1.preferences.set(relations.PREFERENCE_TYPE.ENEMY, self.enemy)
        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.habit_honor.change(-1)
        hero_1.habit_peacefulness.change(1)
        logic.save_hero(hero_1)

        account_2 = self.accounts_factory.create_account()
        hero_2 = logic.load_hero(account_id=account_2.id)
        hero_2.preferences.set(relations.PREFERENCE_TYPE.ENEMY, self.enemy)
        hero_2.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_2.habit_honor.change(2)
        hero_2.habit_peacefulness.change(-2)
        logic.save_hero(hero_2)

        account_3 = self.accounts_factory.create_account()
        hero_3 = logic.load_hero(account_id=account_3.id)
        hero_3.preferences.set(relations.PREFERENCE_TYPE.ENEMY, self.enemy_2)
        hero_3.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_3.habit_honor.change(-4)
        hero_3.habit_peacefulness.change(4)
        logic.save_hero(hero_3)

        account_4 = self.accounts_factory.create_account()
        hero_4 = logic.load_hero(account_id=account_4.id)
        hero_4.preferences.set(relations.PREFERENCE_TYPE.ENEMY, self.enemy)
        hero_4.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=30)
        hero_4.habit_honor.change(8)
        hero_4.habit_peacefulness.change(-8)
        logic.save_hero(hero_4)

        self.assertEqual(HeroPreferences.count_habit_values(self.place_1, all=False), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=False), ((0, -4), (4, 0)))

        self.assertEqual(HeroPreferences.count_habit_values(self.place_1, all=True), ((10, -1), (1, -10)))
        self.assertEqual(HeroPreferences.count_habit_values(self.place_2, all=True), ((0, -4), (4, 0)))



class HeroPreferencesEquipmentSlotTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.EQUIPMENT_SLOT

    def setUp(self):
        super(HeroPreferencesEquipmentSlotTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.EQUIPMENT_SLOT.level_required
        logic.save_hero(self.hero)

        self.slot_1 = relations.EQUIPMENT_SLOT.HAND_PRIMARY
        self.slot_2 = relations.EQUIPMENT_SLOT.PLATE

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, self.slot_1)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.equipment_slot, self.slot_1)


class HeroPreferencesFavoriteItemTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.FAVORITE_ITEM

    def setUp(self):
        super(HeroPreferencesFavoriteItemTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.FAVORITE_ITEM.level_required
        logic.save_hero(self.hero)

        self.slot_1 = relations.EQUIPMENT_SLOT.HAND_PRIMARY
        self.slot_2 = relations.EQUIPMENT_SLOT.PLATE

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.FAVORITE_ITEM, self.slot_1)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.FAVORITE_ITEM, self.slot_1)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.favorite_item, self.slot_1)


class HeroPreferencesRiskLevelTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.RISK_LEVEL

    def setUp(self):
        super(HeroPreferencesRiskLevelTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.RISK_LEVEL.level_required
        logic.save_hero(self.hero)

        self.risk_1 = relations.RISK_LEVEL.VERY_HIGH
        self.risk_2 = relations.RISK_LEVEL.VERY_LOW

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.RISK_LEVEL, self.risk_1)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.RISK_LEVEL, self.risk_1)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.risk_level, self.risk_1)


class HeroPreferencesArchetypeTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.ARCHETYPE

    def setUp(self):
        super(HeroPreferencesArchetypeTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.ARCHETYPE.level_required
        logic.save_hero(self.hero)

        self.mage = game_relations.ARCHETYPE.MAGICAL
        self.warior = game_relations.ARCHETYPE.PHYSICAL

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.ARCHETYPE, self.mage)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.ARCHETYPE, self.mage)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.archetype, self.mage)


class HeroPreferencesCompanionDedicationTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.COMPANION_DEDICATION

    def setUp(self):
        super(HeroPreferencesCompanionDedicationTest, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.COMPANION_DEDICATION.level_required
        logic.save_hero(self.hero)

        self.egoism = relations.COMPANION_DEDICATION.EGOISM
        self.altruism = relations.COMPANION_DEDICATION.ALTRUISM

    def test_initialization(self):
        self.assertTrue(self.hero.preferences.companion_dedication.is_NORMAL)

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.COMPANION_DEDICATION, self.egoism)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.COMPANION_DEDICATION, self.egoism)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.companion_dedication, self.egoism)


class HeroPreferencesCompanionEmpathyTest(TestCase):
    PREFERENCE_TYPE = relations.PREFERENCE_TYPE.COMPANION_EMPATHY

    def setUp(self):
        super(HeroPreferencesCompanionEmpathyTest, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.hero.level = relations.PREFERENCE_TYPE.COMPANION_EMPATHY.level_required
        logic.save_hero(self.hero)

        self.empath = relations.COMPANION_EMPATHY.EMPATH
        self.egocentric = relations.COMPANION_EMPATHY.EGOCENTRIC

    def test_initialization(self):
        self.assertTrue(self.hero.preferences.companion_empathy.is_ORDINAL)

    def test_preferences_serialization(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.COMPANION_EMPATHY, self.empath)
        data = self.hero.preferences.serialize()
        self.assertEqual(data, HeroPreferences.deserialize(data).serialize())

    def test_save(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.COMPANION_EMPATHY, self.empath)
        logic.save_hero(self.hero)
        self.hero = logic.load_hero(hero_id=self.hero.id)
        self.assertEqual(self.hero.preferences.companion_empathy, self.empath)
