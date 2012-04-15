# coding: utf-8
import itertools

from django.test import TestCase

from artifacts.storage import ArtifactsDatabase
from mobs.storage import MobsDatabase

class GameTest(TestCase):

    def test_mobs_loot(self):

        for mob_record in MobsDatabase.storage().data.values():
            for artifact_name in itertools.chain(mob_record.loot, mob_record.artifacts):
                self.assertTrue(artifact_name in ArtifactsDatabase.storage().data)
