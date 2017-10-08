
import datetime

from utg.words import WordForm, Word, Properties
from utg.relations import WORD_TYPE

from dext.settings import settings
from dext.settings.models import Setting

import tt_calendar

from the_tale.common.utils import testcase

from the_tale.linguistics import storage as lignuistics_storage
from the_tale.linguistics import logic as linguistics_logic
from the_tale.linguistics import relations as linguistics_relations


from the_tale.game import turn


class TimeTest(testcase.TestCase):

    def test_creation(self):
        Setting.objects.all().delete()
        settings.refresh()

        settings_number = Setting.objects.all().count()

        self.assertEqual(turn.number(), 0)
        self.assertEqual(Setting.objects.all().count(), settings_number)

        turn.increment()

        self.assertEqual(turn.number(), 1)
        self.assertEqual(Setting.objects.all().count(), settings_number+1)

    def test_get_current_time(self):
        self.assertEqual(turn.number(), 0)

    def test_increment_turn(self):
        self.assertEqual(turn.number(), 0)

        turn.increment()

        self.assertEqual(turn.number(), 1)

    def test_ui_info(self):
        turn.increment()

        self.assertEqual(turn.ui_info()['number'], 1)

    def test_game_time(self):
        self.assertEqual(turn.game_datetime(), tt_calendar.DateTime(0,0,0,0,0,0))

        turn.increment()

        self.assertEqual(turn.game_datetime(), tt_calendar.DateTime(0,0,0,0,2,0))


class LinguisticsDateTests(testcase.TestCase):

    def setUp(self):
        super(LinguisticsDateTests, self).setUp()

        linguistics_logic.sync_static_restrictions()

        self.date = turn.LinguisticsDate(tt_calendar.Date(year=1, month=2, day=3))

    def test_utg_name_form(self):
        self.assertEqual(self.date.utg_name_form, WordForm(Word(type=WORD_TYPE.TEXT, forms=('4 юного квинта сырого месяца 2 года',), properties=Properties())))

    def test_linguistics_restrictions__no_feasts(self):
        now = datetime.datetime(year=34, month=2, day=28, hour=0, minute=0, second=0)

        for feast in tt_calendar.REAL_FEAST.records:
            restriction = lignuistics_storage.restrictions_storage.get_restriction(linguistics_relations.TEMPLATE_RESTRICTION_GROUP.REAL_FEAST, feast.value).id
            self.assertNotIn(restriction, self.date.linguistics_restrictions(now))

    def test_linguistics_restrictions__has_feast(self):
        for feast in tt_calendar.REAL_FEAST.records:
            restriction = lignuistics_storage.restrictions_storage.get_restriction(linguistics_relations.TEMPLATE_RESTRICTION_GROUP.REAL_FEAST, feast.value).id
            for interval in feast.intervals:
                self.assertIn(restriction, self.date.linguistics_restrictions(interval[0] + (interval[1]-interval[0])/2))
