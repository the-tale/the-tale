# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype
from the_tale.game.balance import constants as c

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.abilities.relations import HELP_CHOICES

from the_tale.game.heroes import logic as heroes_logic

from .. import meta_actions
from ..prototypes import ACTION_TYPES
from .helpers import TestAction


class GeneralTest(testcase.TestCase):

    def setUp(self):
        super(GeneralTest, self).setUp()
        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action

        self.bundle_id = self.action_idl.bundle_id

    def tearDown(self):
        pass

    def test_HELP_CHOICES(self):
        for action_class in ACTION_TYPES.values():
            self.assertTrue('HELP_CHOICES' in action_class.__dict__)
            if (not action_class.TYPE.is_IDLENESS and           # TODO: check
                not action_class.TYPE.is_BATTLE_PVE_1X1 and     # TODO: check
                not action_class.TYPE.is_MOVE_TO and            # TODO: check
                not action_class.TYPE.is_HEAL_COMPANION and
                not action_class.TYPE.is_RESURRECT):
                self.assertIn(HELP_CHOICES.MONEY, action_class.HELP_CHOICES) # every action MUST has MONEY choice, or it will be great disbalance in energy & experience receiving

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


    def check_heal_companion_in_choices(self, result):
        heal_found = False
        for i in xrange(100):
            heal_found = heal_found or (self.action_idl.get_help_choice() == HELP_CHOICES.HEAL_COMPANION)

        self.assertEqual(heal_found, result)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL,)))
    def test_help_choice_has_heal__for_full_health_without_alternative(self):
        self.check_heal_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal__for_full_health_with_alternative(self):
        self.check_heal_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL,)))
    def test_help_choice_has_heal__for_large_health_without_alternative(self):
        self.hero.health = self.hero.max_health - 1
        self.check_heal_in_choices(True)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal__for_large_health_with_alternative(self):
        self.hero.health = self.hero.max_health - 1
        self.check_heal_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL,)))
    def test_help_choice_has_heal__for_low_health_without_alternative(self):
        self.hero.health = 1
        self.check_heal_in_choices(True)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL, HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal__for_low_health_with_alternative(self):
        self.hero.health = 1
        self.check_heal_in_choices(True)


    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL_COMPANION,)))
    def test_help_choice_has_heal_companion__for_no_companion(self):
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL_COMPANION, HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal_companion__for_no_companion_with_alternative(self):
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL_COMPANION,)))
    def test_help_choice_has_heal_companion__for_full_health_without_alternative(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL_COMPANION,)))
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_heal_disabled', lambda hero: True)
    def test_help_choice_has_heal_companion__for_companion_heal_disabled(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL_COMPANION, HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal_companion__for_full_health_with_alternative(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL_COMPANION,)))
    def test_help_choice_has_heal_companion__for_low_health_without_alternative(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.hero.companion.health = 1
        self.check_heal_companion_in_choices(True)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.HEAL_COMPANION, HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal_companion__for_low_health_with_alternative(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.hero.companion.health = 1
        self.check_heal_companion_in_choices(True)


    def check_stock_up_energy_in_choices(self, result):
        stock_found = False
        for i in xrange(1000):
            stock_found = stock_found or (self.action_idl.get_help_choice() == HELP_CHOICES.STOCK_UP_ENERGY)

        self.assertEqual(stock_found, result)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.MONEY)))
    def test_help_choice_has_stock_up_energy__can_stock(self):
        self.hero.energy_bonus = 0
        self.check_stock_up_energy_in_choices(True)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((HELP_CHOICES.STOCK_UP_ENERGY, HELP_CHOICES.MONEY)))
    def test_help_choice_has_stock_up_energy__can_not_stock(self):
        self.hero.energy_bonus = c.ANGEL_FREE_ENERGY_MAXIMUM
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
        heroes_logic.save_hero(self.hero)

        self.assertTrue(HELP_CHOICES.HEAL in self.action_idl.help_choices)

        self.hero.kill()
        heroes_logic.save_hero(self.hero)

        self.assertFalse(HELP_CHOICES.HEAL in self.action_idl.help_choices)

    def test_action_default_serialization(self):
        # class TestAction(ActionBase):
        #     TYPE = 'test-action'

        default_action = TestAction( hero=self.hero,
                                     bundle_id=self.bundle_id,
                                     state=TestAction.STATE.UNINITIALIZED)

        self.assertEqual(default_action.serialize(), {'bundle_id': self.bundle_id,
                                                      'state': TestAction.STATE.UNINITIALIZED,
                                                      'percents': 0.0,
                                                      'description': None,
                                                      'type': TestAction.TYPE.value,
                                                      'created_at_turn': TimePrototype.get_current_turn_number()})
        deserialized_action = TestAction.deserialize(default_action.serialize())
        deserialized_action.hero = self.hero
        self.assertEqual(default_action, deserialized_action)

    def test_action_full_serialization(self):
        mob = mobs_storage.create_mob_for_hero(self.hero)

        account_2 = self.accounts_factory.create_account()

        self.storage.load_account_data(account_2)
        hero_2 = self.storage.accounts_to_heroes[account_2.id]


        meta_action = meta_actions.ArenaPvP1x1.create(self.storage, self.hero, hero_2)

        default_action = TestAction( hero=self.hero,
                                     bundle_id=self.bundle_id,
                                     state=TestAction.STATE.UNINITIALIZED,
                                     created_at_turn=666,
                                     context=TestAction.CONTEXT_MANAGER(),
                                     description=u'description',
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
                                     back=True,
                                     info_link='/bla-bla',
                                     meta_action=meta_action,
                                     replane_required=True)

        self.assertEqual(default_action.serialize(), {'bundle_id': self.bundle_id,
                                                      'state': TestAction.STATE.UNINITIALIZED,
                                                      'context': TestAction.CONTEXT_MANAGER().serialize(),
                                                      'mob_context': TestAction.CONTEXT_MANAGER().serialize(),
                                                      'mob': mob.serialize(),
                                                      'length': 777,
                                                      'back': True,
                                                      'textgen_id': 'textgen_id',
                                                      'extra_probability': 0.6,
                                                      'percents_barier': 77,
                                                      'destination_x': 20,
                                                      'destination_y': 30,
                                                      'percents': 0.0,
                                                      'description': u'description',
                                                      'type': TestAction.TYPE.value,
                                                      'created_at_turn': 666,
                                                      'place_id': 2,
                                                      'data': {'xxx': 'yyy'},
                                                      'info_link': '/bla-bla',
                                                      'break_at': 0.75,
                                                      'meta_action': meta_action.serialize(),
                                                      'replane_required': True})
        deserialized_action = TestAction.deserialize(default_action.serialize())
        deserialized_action.hero = self.hero
        self.assertEqual(default_action, deserialized_action)
