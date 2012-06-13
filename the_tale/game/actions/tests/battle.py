# coding: utf-8

from django.test import TestCase

from game.logic import create_test_bundle, create_test_map, test_bundle_save

from game.actions.battle import Actor
from game.actions.contexts import BattleContext

from game.heroes.habilities.prototypes import RUN_UP_PUSH, HIT
from game.mobs.storage import MobsDatabase

class ActorTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('ActorTest')

    def tearDown(self):
        pass


    def test_hero_actor(self):
        hero = self.bundle.tests_get_hero()
        hero.health = 10
        hero.abilities.add(RUN_UP_PUSH.get_id())

        actor = Actor(hero, BattleContext())

        self.assertEqual(hero.initiative, actor.initiative)
        self.assertEqual(hero.name, actor.name)
        self.assertEqual(hero.normalized_name, actor.normalized_name)
        self.assertEqual(hero.basic_damage, actor.basic_damage)
        self.assertEqual(hero.health, actor.health)
        self.assertEqual(hero.max_health, actor.max_health)

        self.assertEqual(actor.change_health(-5), -5)
        self.assertEqual(actor.health, 5)

        self.assertEqual(actor.change_health(-50), -5)
        self.assertEqual(actor.health, 0)

        self.assertEqual(actor.change_health(actor.max_health+50), actor.max_health)
        self.assertEqual(actor.health, actor.max_health)

        hit_selected = False
        run_up_push_selected = False
        for i in xrange(100):
            ability = actor.choose_ability()

            if ability.get_id() == HIT.get_id():
               hit_selected = True
            elif ability.get_id() == RUN_UP_PUSH.get_id():
                run_up_push_selected = True

        self.assertTrue(hit_selected)
        self.assertTrue(run_up_push_selected)

        test_bundle_save(self, self.bundle)


    def test_mob_actor(self):
        hero = self.bundle.tests_get_hero()
        mob = MobsDatabase.storage().get_random_mob(hero)
        mob.health = 10
        mob.abilities.add(RUN_UP_PUSH.get_id())

        actor = Actor(mob, BattleContext())

        self.assertEqual(mob.initiative, actor.initiative)
        self.assertEqual(mob.name, actor.name)
        self.assertEqual(mob.normalized_name, actor.normalized_name)
        self.assertEqual(mob.basic_damage, actor.basic_damage)
        self.assertEqual(mob.health, actor.health)
        self.assertEqual(mob.max_health, actor.max_health)

        self.assertEqual(actor.change_health(-5), -5)
        self.assertEqual(actor.health, 5)

        self.assertEqual(actor.change_health(-50), -5)
        self.assertEqual(actor.health, 0)

        self.assertEqual(actor.change_health(actor.max_health+50), actor.max_health)
        self.assertEqual(actor.health, actor.max_health)

        hit_selected = False
        run_up_push_selected = False
        for i in xrange(100):
            ability = actor.choose_ability()

            if ability.get_id() == HIT.get_id():
               hit_selected = True
            elif ability.get_id() == RUN_UP_PUSH.get_id():
                run_up_push_selected = True

        self.assertTrue(hit_selected)
        self.assertTrue(run_up_push_selected)

        test_bundle_save(self, self.bundle)
