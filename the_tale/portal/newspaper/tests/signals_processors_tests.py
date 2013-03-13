# coding: utf-8

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from portal.newspaper.models import NewspaperEvent
from portal.newspaper.prototypes import NewspaperEventPrototype

from game.workers.highlevel import Worker as HighlevelWorker
from game import signals as game_signals

from game.heroes.prototypes import HeroPrototype

class NewspaperDayStartedEvents(TestCase):

    def setUp(self):
        super(NewspaperDayStartedEvents, self).setUp()
        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)
        self.hero1 = HeroPrototype.get_by_account_id(self.account1.id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)
        self.hero2 = HeroPrototype.get_by_account_id(self.account2.id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)
        self.hero3 = HeroPrototype.get_by_account_id(self.account3.id)

    def test_initialize(self):
        self.assertEqual(NewspaperEvent.objects.all().count(),0)

    def test_newspaper_day_started(self):
        game_signals.day_started.send(HighlevelWorker)
        self.assertEqual(NewspaperEvent.objects.all().count(),1)
        self.assertTrue(NewspaperEventPrototype(NewspaperEvent.objects.all()[0]).data.hero_id in [self.hero1.id, self.hero2.id, self.hero3.id])

    def test_newspaper_day_started_random(self):
        hero_ids = set()

        for i in xrange(100):
            game_signals.day_started.send(HighlevelWorker)
            hero_ids.add(NewspaperEventPrototype(NewspaperEvent.objects.all().order_by('-created_at')[0]).data.hero_id)

        self.assertEqual(NewspaperEvent.objects.all().count(),100)
        self.assertEqual(hero_ids, set([self.hero1.id, self.hero2.id, self.hero3.id]))
