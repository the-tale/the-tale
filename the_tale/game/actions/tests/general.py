# coding: utf-8
import mock

from common.utils import testcase

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.logic import create_test_map
from game.prototypes import TimePrototype
from game.balance import constants as c

from game.abilities.relations import HELP_CHOICES

from game.actions.prototypes import ACTION_TYPES, ActionBase
from game.actions.tests.helpers import TestAction


class GeneralTest(testcase.TestCase):

    def setUp(self):
        super(GeneralTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.bundle_id = bundle_id
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

    def tearDown(self):
        pass

    def test_HELP_CHOICES(self):
        for action_class in ACTION_TYPES.values():
            self.assertTrue('HELP_CHOICES' in action_class.__dict__)

    def test_TEXTGEN_TYPE(self):
        for action_class in ACTION_TYPES.values():
            self.assertTrue('TEXTGEN_TYPE' in action_class.__dict__)

    def test_get_help_choice_has_heal(self):
        self.hero.health = 1

        heal_found = False
        for i in xrange(100):
            heal_found = heal_found or (self.action_idl.get_help_choice() == HELP_CHOICES.HEAL)

        self.assertTrue(heal_found)

    def check_heal_in_choices(self, result):
        heal_found = False
        for i in xrange(100):
            heal_found = heal_found or (self.action_idl.get_help_choice() == HELP_CHOICES.HEAL)

        self.assertEqual(heal_found, result)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL,)))
    def test_help_choice_has_heal__for_full_health_without_alternative(self):
        self.check_heal_in_choices(False)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal__for_full_health_with_alternative(self):
        self.check_heal_in_choices(False)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL,)))
    def test_help_choice_has_heal__for_large_health_without_alternative(self):
        self.hero.health = self.hero.max_health - 1
        self.check_heal_in_choices(True)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal__for_large_health_with_alternative(self):
        self.hero.health = self.hero.max_health - 1
        self.check_heal_in_choices(False)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL,)))
    def test_help_choice_has_heal__for_low_health_without_alternative(self):
        self.hero.health = 1
        self.check_heal_in_choices(True)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal__for_low_health_with_alternative(self):
        self.hero.health = 1
        self.check_heal_in_choices(True)

    def check_stock_up_energy_in_choices(self, result):
        stock_found = False
        for i in xrange(100):
            stock_found = stock_found or (self.action_idl.get_help_choice() == HELP_CHOICES.STOCK_UP_ENERGY)

        self.assertEqual(stock_found, result)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.MONEY)))
    def test_help_choice_has_stock_up_energy__can_stock(self):
        self.hero.energy_charges = 0
        self.check_stock_up_energy_in_choices(True)

    @mock.patch('game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.MONEY)))
    def test_help_choice_has_stock_up_energy__can_not_stock(self):
        self.hero.energy_charges = c.ANGEL_FREE_ENERGY_CHARGES_MAXIMUM
        self.check_stock_up_energy_in_choices(False)

    def test_percents_consistency(self):
        current_time = TimePrototype.get_current_time()

        # just test that quest will be ended
        while not self.action_idl.leader:
            self.storage.process_turn()
            current_time.increment_turn()
            self.assertEqual(self.storage.tests_get_last_action().percents, self.hero.last_action_percents)

    def test_help_choice_heal_not_in_choices_for_dead_hero(self):

        self.hero.health = 1
        self.hero.save()

        self.assertTrue(HELP_CHOICES.HEAL in self.action_idl.help_choices)

        self.hero.kill()
        self.hero.save()

        self.assertFalse(HELP_CHOICES.HEAL in self.action_idl.help_choices)

    def test_action_default_serialization(self):
        class TestAction(ActionBase):
            TYPE = 'test-action'

        default_action = TestAction( hero=self.hero,
                                     bundle_id=self.bundle_id,
                                     state=TestAction.STATE.UNINITIALIZED)

        self.assertEqual(default_action.serialize(), {'bundle_id': self.bundle_id,
                                                      'state': TestAction.STATE.UNINITIALIZED,
                                                      'percents': 0.0,
                                                      'description': None,
                                                      'type': TestAction.TYPE,
                                                      'created_at_turn': TimePrototype.get_current_turn_number()})

        self.assertEqual(default_action, TestAction.deserialize(self.hero, default_action.serialize()))


    def test_action_full_serialization(self):
        from game.heroes.logic import create_mob_for_hero

        mob = create_mob_for_hero(self.hero)

        default_action = TestAction( hero=self.hero,
                                     bundle_id=self.bundle_id,
                                     state=TestAction.STATE.UNINITIALIZED,
                                     created_at_turn=666,
                                     context=TestAction.CONTEXT_MANAGER(),
                                     description=u'description',
                                     quest_id=1,
                                     place_id=2,
                                     mob=mob,
                                     data={'xxx': 'yyy'},
                                     break_at=0.75,
                                     length=777,
                                     destination_x=20,
                                     destination_y=30,
                                     percents_barier=77,
                                     extra_probability=0.6,
                                     mob_context=TestAction.CONTEXT_MANAGER(),
                                     textgen_id='textgen_id',
                                     hero_health_lost=20,
                                     back=True,
                                     info_link='/bla-bla',
                                     meta_action_id=7)

        self.assertEqual(default_action.serialize(), {'bundle_id': self.bundle_id,
                                                      'state': TestAction.STATE.UNINITIALIZED,
                                                      'context': TestAction.CONTEXT_MANAGER().serialize(),
                                                      'mob_context': TestAction.CONTEXT_MANAGER().serialize(),
                                                      'mob': mob.serialize(),
                                                      'meta_action_id': 7,
                                                      'length': 777,
                                                      'back': True,
                                                      'hero_health_lost': 20,
                                                      'textgen_id': 'textgen_id',
                                                      'extra_probability': 0.6,
                                                      'percents_barier': 77,
                                                      'destination_x': 20,
                                                      'destination_y': 30,
                                                      'percents': 0.0,
                                                      'description': u'description',
                                                      'type': TestAction.TYPE,
                                                      'created_at_turn': 666,
                                                      'quest_id': 1,
                                                      'place_id': 2,
                                                      'data': {'xxx': 'yyy'},
                                                      'info_link': '/bla-bla',
                                                      'break_at': 0.75})

        self.assertEqual(default_action, TestAction.deserialize(self.hero, default_action.serialize()))
