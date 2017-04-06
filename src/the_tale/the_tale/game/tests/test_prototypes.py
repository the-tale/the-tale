# coding: utf-8
import datetime
from unittest import mock

from utg.words import WordForm, Word, Properties
from utg.relations import WORD_TYPE

from the_tale.common.utils import testcase

from the_tale.linguistics import storage
from the_tale.linguistics import logic as linguistics_logic
from the_tale.linguistics import relations as linguistics_relations

from the_tale.game import prototypes
from the_tale.game import relations


class GameTimeTests(testcase.TestCase):

    def setUp(self):
        super(GameTimeTests, self).setUp()

        linguistics_logic.sync_static_restrictions()

        self.time = prototypes.GameTime(year=1, month=2, day=3, hour=4, minute=5, second=6)


    def test_utg_name_form(self):
        self.assertEqual(self.time.utg_name_form, WordForm(Word(type=WORD_TYPE.TEXT, forms=('3 сырого месяца 1 года',), properties=Properties())))


    def test_linguistics_restrictions__no_feasts(self):
        now = datetime.datetime(year=34, month=2, day=28, hour=0, minute=0, second=0)
        self.assertEqual(self.time.linguistics_restrictions(now), ())


    def test_linguistics_restrictions__has_feast(self):
        for feast in relations.REAL_FEAST.records:
            restriction = storage.restrictions_storage.get_restriction(linguistics_relations.TEMPLATE_RESTRICTION_GROUP.REAL_FEAST, feast.value).id
            self.assertEqual(self.time.linguistics_restrictions(feast.start_at + (feast.end_at-feast.start_at)/2), (restriction,))
