# coding: utf-8

from django.test import TestCase

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map

from game.actions.battle import Actor
from game.actions.contexts import BattleContext

from game.heroes.habilities.battle import RUN_UP_PUSH, HIT
from game.mobs.storage import MobsDatabase
from game.logic_storage import LogicStorage

class ActorTest(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

    def tearDown(self):
        pass


    def test_hero_actor(self):
        self.hero.health = 10
        self.hero.abilities.add(RUN_UP_PUSH.get_id())

        actor = Actor(self.hero, BattleContext())

        self.assertEqual(self.hero.initiative, actor.initiative)
        self.assertEqual(self.hero.name, actor.name)
        self.assertEqual(self.hero.normalized_name, actor.normalized_name)
        self.assertEqual(self.hero.basic_damage, actor.basic_damage)
        self.assertEqual(self.hero.health, actor.health)
        self.assertEqual(self.hero.max_health, actor.max_health)

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

        self.storage._test_save()

    def test_initiative_change(self):
        actor = Actor(self.hero, BattleContext())
        actor.context.use_initiative([2])
        self.assertEqual(actor.initiative, self.hero.initiative*2)


    def test_mob_actor(self):
        mob = MobsDatabase.storage().get_random_mob(self.hero)
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

        self.storage._test_save()
