# coding: utf-8
import mock

from django.test import TestCase

from game.actions import prototypes as actions_prototypes
from game.actions.prototypes import HELP_CHOICES

from game.heroes.logic import create_mob_for_hero

from game.logic import create_test_bundle, create_test_map

from game.abilities.deck.help import Help

class HelpAbilityTest(TestCase):

    def setUp(self):
        p1, p2, p3 = create_test_map()
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

        self.ability = Help()

        self.bundle = create_test_bundle('ActorTest')
        self.angel = self.bundle.tests_get_angel()
        self.hero = self.bundle.tests_get_hero()
        self.action_idl = self.bundle.tests_get_last_action()
        # self.bundle.add_action(ActionBattlePvE1x1Prototype.create(self.action_idl, mob=create_mob_for_hero(self.hero)))
        # self.action_battle = self.bundle.tests_get_last_action()

    def tearDown(self):
        pass

    def test_none(self):
        with mock.patch('game.actions.prototypes.ActionPrototype.get_help_choice', lambda x: None):
            self.assertFalse(self.ability.use(self.bundle, self.angel, self.hero, None))

    def test_heal(self):
        self.hero.health = 1
        with mock.patch('game.actions.prototypes.ActionPrototype.get_help_choice', lambda x: HELP_CHOICES.HEAL):
            self.assertTrue(self.ability.use(self.bundle, self.angel, self.hero, None))
            self.assertTrue(self.hero.health > 1)

    def test_start_quest(self):
        with mock.patch('game.actions.prototypes.ActionPrototype.get_help_choice', lambda x: HELP_CHOICES.START_QUEST):
            self.assertTrue(self.ability.use(self.bundle, self.angel, self.hero, None))
            self.assertTrue(self.action_idl.percents >= 1)

    def test_money(self):
        old_hero_money = self.hero.money
        with mock.patch('game.actions.prototypes.ActionPrototype.get_help_choice', lambda x: HELP_CHOICES.MONEY):
            self.assertTrue(self.ability.use(self.bundle, self.angel, self.hero, None))
            self.assertTrue(self.hero.money > old_hero_money)

    @mock.patch('game.balance.constants.BATTLES_PER_TURN', 0)
    def test_teleport(self):
        move_place = self.p3
        if move_place.id == self.hero.position.place.id:
            move_place = self.p1
        self.bundle.add_action(actions_prototypes.ActionMoveToPrototype.create(self.action_idl, move_place))

        self.bundle.process_turn(1)

        old_road_percents = self.hero.position.percents

        with mock.patch('game.actions.prototypes.ActionPrototype.get_help_choice', lambda x: HELP_CHOICES.TELEPORT):
            self.assertTrue(self.ability.use(self.bundle, self.angel, self.hero, None))
            self.assertTrue(old_road_percents < self.hero.position.percents)

    def test_lighting(self):
        self.bundle.add_action(actions_prototypes.ActionBattlePvE1x1Prototype.create(self.action_idl, mob=create_mob_for_hero(self.hero)))
        action_battle = self.bundle.tests_get_last_action()

        self.bundle.process_turn(1)

        old_mob_health = action_battle.mob.health

        with mock.patch('game.actions.prototypes.ActionPrototype.get_help_choice', lambda x: HELP_CHOICES.LIGHTING):
            self.assertTrue(self.ability.use(self.bundle, self.angel, self.hero, None))
            self.assertTrue(old_mob_health > action_battle.mob.health)

    def test_resurrect(self):
        self.hero.kill()
        self.bundle.add_action(actions_prototypes.ActionResurrectPrototype.create(self.action_idl))

        with mock.patch('game.actions.prototypes.ActionPrototype.get_help_choice', lambda x: HELP_CHOICES.RESURRECT):
            self.assertTrue(self.ability.use(self.bundle, self.angel, self.hero, None))
            self.bundle.process_turn(1)
            self.assertEqual(self.hero.health, self.hero.max_health)
            self.assertEqual(self.hero.is_alive, True)
