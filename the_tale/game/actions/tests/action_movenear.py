# coding: utf-8
import mock

from common.utils import testcase

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage


from game.balance import constants as c, formulas as f, enums as e

from game.logic import create_test_map
from game.actions.prototypes import ActionMoveNearPlacePrototype, ActionRestPrototype, ActionResurrectPrototype
from game.actions.prototypes import ActionIdlenessPrototype, ActionBattlePvE1x1Prototype, ActionInPlacePrototype, ActionRegenerateEnergyPrototype
from game.prototypes import TimePrototype

class MoveNearActionTest(testcase.TestCase):

    def setUp(self):
        super(MoveNearActionTest, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

        self.hero.position.set_place(self.p1)

        self.action_move = ActionMoveNearPlacePrototype.create(self.action_idl, self.p1, False)
    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_move.leader, True)
        self.assertEqual(self.action_move.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()


    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 0)
    def test_processed(self):

        current_time = TimePrototype.get_current_time()

        self.storage.process_turn()

        x, y = self.action_move.get_destination()
        self.hero.position.set_coordinates(x, y, x, y, percents=1)

        current_time.increment_turn()
        self.storage.process_turn()

        # can end in field or in start place
        self.assertTrue(self.storage.heroes_to_actions[self.hero.id][-1].TYPE in [ActionIdlenessPrototype.TYPE, ActionInPlacePrototype.TYPE])
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place)

        self.storage._test_save()


    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 0)
    def test_not_ready(self):
        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_move)
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place) # can end in start place
        self.storage._test_save()

    def test_full_move_and_back(self):

        current_time = TimePrototype.get_current_time()

        while len(self.storage.actions) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionIdlenessPrototype.TYPE)
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place)  # can end in start place

        ActionMoveNearPlacePrototype.create(self.action_idl, self.p1, True)
        while self.hero.position.place is None or self.hero.position.place.id != self.p1.id:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionInPlacePrototype.TYPE)
        self.assertTrue(not self.hero.position.is_walking)
        self.storage._test_save()

    def test_move_change_place_coordinates_and_back(self):

        current_time = TimePrototype.get_current_time()

        while len(self.storage.actions) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionIdlenessPrototype.TYPE)
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place)  # can end in start place

        ActionMoveNearPlacePrototype.create(self.action_idl, self.p1, True)
        self.p1._model.x = self.p1.x + 1
        self.p1._model.y = self.p1.y + 1
        self.p1.save()

        while self.hero.position.place is None or self.hero.position.place.id != self.p1.id:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionInPlacePrototype.TYPE)
        self.assertTrue(not self.hero.position.is_walking)
        self.storage._test_save()

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        while len(self.storage.actions) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()

    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 1.0)
    def test_battle(self):
        self.storage.process_turn()
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionBattlePvE1x1Prototype.TYPE)
        self.storage._test_save()

    def test_regenerate_energy_on_move(self):
        self.hero.preferences.energy_regeneration_type = e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.action_move.state = self.action_move.STATE.MOVING

        self.storage.process_turn()

        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()

    def test_not_regenerate_energy_on_move_for_sacrifice(self):
        self.hero.preferences.energy_regeneration_type = e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.action_move.state = self.action_move.STATE.MOVING

        self.storage.process_turn()

        self.assertNotEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()


    def test_regenerate_energy_after_battle_for_sacrifice(self):
        self.hero.preferences.energy_regeneration_type = e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.action_move.state = self.action_move.STATE.BATTLE

        self.storage.process_turn()

        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()


    def test_rest(self):
        self.hero.health = 1
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn()

        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionRestPrototype.TYPE)
        self.storage._test_save()


    def test_resurrect(self):
        self.hero.kill()
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn()

        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionResurrectPrototype.TYPE)
        self.storage._test_save()
