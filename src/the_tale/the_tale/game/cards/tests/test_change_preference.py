
import random


from the_tale.common.utils import testcase

from the_tale.game import relations as game_relations

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.heroes import relations as heroes_relations
from the_tale.game.places import storage as places_storage
from the_tale.game.persons import storage as persons_storage
from the_tale.game.mobs import storage as mobs_storage


from . import helpers


class ChangePreference(testcase.TestCase, helpers.CardsTestMixin):

    def setUp(self):
        super().setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]


    def test_every_preference_has_form(self):
        for preference in heroes_relations.PREFERENCE_TYPE.records:
            card = cards.CARD.CHANGE_PREFERENCE.effect.create_card(type=cards.CARD.CHANGE_PREFERENCE,
                                                                   available_for_auction=True,
                                                                   preference=preference)
            self.assertNotEqual(card.get_form(hero=self.hero), None)


    def use_card(self, preference, form_value):
        card = cards.CARD.CHANGE_PREFERENCE.effect.create_card(type=cards.CARD.CHANGE_PREFERENCE,
                                                               available_for_auction=True,
                                                               preference=preference)

        form = card.get_form(data={'value': form_value}, hero=self.hero)

        self.assertTrue(form.is_valid())

        result, step, postsave_actions = card.effect.use(**self.use_attributes(storage=self.storage,
                                                                               hero=self.hero,
                                                                               value=form.get_card_data()['value'],
                                                                               card=card))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

    def test_mob(self):
        mob = mobs_storage.mobs.all()[0]

        self.assertEqual(self.hero.preferences.mob, None)

        self.use_card(heroes_relations.PREFERENCE_TYPE.MOB, mob.id)

        self.assertEqual(self.hero.preferences.mob.id, mob.id)

        self.use_card(heroes_relations.PREFERENCE_TYPE.MOB, None)

        self.assertEqual(self.hero.preferences.mob, None)

    def test_place(self):
        place = places_storage.places.all()[0]

        self.assertEqual(self.hero.preferences.place, None)

        self.use_card(heroes_relations.PREFERENCE_TYPE.PLACE, place.id)

        self.assertEqual(self.hero.preferences.place.id, place.id)

        self.use_card(heroes_relations.PREFERENCE_TYPE.PLACE, None)

        self.assertEqual(self.hero.preferences.place, None)

    def test_friend(self):
        friend = persons_storage.persons.all()[0]

        self.assertEqual(self.hero.preferences.friend, None)

        self.use_card(heroes_relations.PREFERENCE_TYPE.FRIEND, friend.id)

        self.assertEqual(self.hero.preferences.friend.id, friend.id)

        self.use_card(heroes_relations.PREFERENCE_TYPE.FRIEND, None)

        self.assertEqual(self.hero.preferences.friend, None)

    def test_enemy(self):
        enemy = persons_storage.persons.all()[0]

        self.assertEqual(self.hero.preferences.enemy, None)

        self.use_card(heroes_relations.PREFERENCE_TYPE.ENEMY, enemy.id)

        self.assertEqual(self.hero.preferences.enemy.id, enemy.id)

        self.use_card(heroes_relations.PREFERENCE_TYPE.ENEMY, None)

        self.assertEqual(self.hero.preferences.enemy, None)

    def test_energy_regeneration_type(self):
        self.hero.preferences.set(preferences_type=heroes_relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE,
                                  value=heroes_relations.ENERGY_REGENERATION.PRAY)

        self.use_card(heroes_relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, heroes_relations.ENERGY_REGENERATION.SACRIFICE)

        self.assertTrue(self.hero.preferences.energy_regeneration_type.is_SACRIFICE)

    def test_equipment_slot(self):
        slot = heroes_relations.EQUIPMENT_SLOT.random()

        self.assertEqual(self.hero.preferences.equipment_slot, None)

        self.use_card(heroes_relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, slot)

        self.assertEqual(self.hero.preferences.equipment_slot, slot)

        self.use_card(heroes_relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, None)

        self.assertEqual(self.hero.preferences.equipment_slot, None)

    def test_favorite_item(self):
        choices = [heroes_relations.EQUIPMENT_SLOT(slot_id) for slot_id in self.hero.equipment.equipment.keys()]

        slot = random.choice(choices)

        self.assertEqual(self.hero.preferences.favorite_item, None)

        self.use_card(heroes_relations.PREFERENCE_TYPE.FAVORITE_ITEM, slot)

        self.assertEqual(self.hero.preferences.favorite_item, slot)

        self.use_card(heroes_relations.PREFERENCE_TYPE.FAVORITE_ITEM, None)

        self.assertEqual(self.hero.preferences.favorite_item, None)

    def test_risk_level(self):
        self.assertTrue(self.hero.preferences.risk_level.is_NORMAL)

        self.use_card(heroes_relations.PREFERENCE_TYPE.RISK_LEVEL, heroes_relations.RISK_LEVEL.LOW)

        self.assertTrue(self.hero.preferences.risk_level.is_LOW)

    def test_architype(self):
        self.assertTrue(self.hero.preferences.archetype.is_NEUTRAL)

        self.use_card(heroes_relations.PREFERENCE_TYPE.ARCHETYPE, game_relations.ARCHETYPE.MAGICAL)

        self.assertTrue(self.hero.preferences.archetype.is_MAGICAL)

    def test_companion_dedication(self):
        self.assertTrue(self.hero.preferences.companion_dedication.is_NORMAL)

        self.use_card(heroes_relations.PREFERENCE_TYPE.COMPANION_DEDICATION, heroes_relations.COMPANION_DEDICATION.EGOISM)

        self.assertTrue(self.hero.preferences.companion_dedication.is_EGOISM)

    def test_companion_empathy(self):
        self.assertTrue(self.hero.preferences.companion_empathy.is_ORDINAL)

        self.use_card(heroes_relations.PREFERENCE_TYPE.COMPANION_EMPATHY, heroes_relations.COMPANION_EMPATHY.EMPATH)

        self.assertTrue(self.hero.preferences.companion_empathy.is_EMPATH)
