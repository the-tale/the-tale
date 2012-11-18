# coding: utf-8

from django.test import TestCase

from game.logic import create_test_map

from game.bundles import BundlePrototype

from accounts.logic import register_user

from game.models import Bundle
from game.logic import clean_database


class LogicTests(TestCase):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.bundle = BundlePrototype.get_by_id(bundle_id)

    def test_clean_database(self):

        BundlePrototype.create()
        BundlePrototype.create()

        self.assertEqual(Bundle.objects.all().count(), 3)

        clean_database()

        self.assertEqual(list(Bundle.objects.all().values_list('id', flat=True)), [self.bundle.id])
