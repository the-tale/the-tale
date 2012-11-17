# coding: utf-8
import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from common.utils.fake import FakeLogger

from game.heroes.models import Hero
from game.quests.models import Quest
from game.actions.models import Action
from game.models import Bundle
from game.logic import create_test_map

from accounts.logic import block_expired_accounts
from accounts.prototypes import RegistrationTaskPrototype
from accounts.models import Account, RegistrationTask


class TestLogic(TestCase):

    def setUp(self):
        create_test_map()


    def test_block_expired_accounts(self):
        task = RegistrationTaskPrototype.create()
        task.process(FakeLogger())

        task.account.model.created_at = datetime.datetime.fromtimestamp(0)
        task.account.model.save()

        block_expired_accounts()

        self.assertEqual(Hero.objects.all().count(), 0)
        self.assertEqual(Quest.objects.all().count(), 0)
        self.assertEqual(Action.objects.all().count(), 0)

        self.assertEqual(Bundle.objects.all().count(), 0)

        self.assertEqual(Account.objects.all().count(), 0)
        self.assertEqual(User.objects.all().count(), 0)

        self.assertEqual(RegistrationTask.objects.all().count(), 1)
