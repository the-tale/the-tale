
import smart_imports

smart_imports.all()


class TimeTest(utils_testcase.TestCase):

    def test_creation(self):
        dext_settings_models.Setting.objects.all().delete()
        dext_settings.settings.refresh()

        settings_number = dext_settings_models.Setting.objects.all().count()

        self.assertEqual(game_turn.number(), 0)
        self.assertEqual(dext_settings_models.Setting.objects.all().count(), settings_number)

        game_turn.increment()

        self.assertEqual(game_turn.number(), 1)
        self.assertEqual(dext_settings_models.Setting.objects.all().count(), settings_number + 1)

    def test_get_current_time(self):
        self.assertEqual(game_turn.number(), 0)

    def test_increment_turn(self):
        self.assertEqual(game_turn.number(), 0)

        game_turn.increment()

        self.assertEqual(game_turn.number(), 1)

    def test_ui_info(self):
        game_turn.increment()

        self.assertEqual(game_turn.ui_info()['number'], 1)

    def test_game_time(self):
        self.assertEqual(game_turn.game_datetime(), tt_calendar.DateTime(0, 0, 0, 0, 0, 0))

        game_turn.increment()

        self.assertEqual(game_turn.game_datetime(), tt_calendar.DateTime(0, 0, 0, 0, 2, 0))


class LinguisticsDateTests(utils_testcase.TestCase):

    def setUp(self):
        super(LinguisticsDateTests, self).setUp()

        linguistics_logic.sync_static_restrictions()

        self.date = game_turn.LinguisticsDate(tt_calendar.Date(year=1, month=2, day=3))

    def test_utg_name_form(self):
        self.assertEqual(self.date.utg_name_form, utg_words.WordForm(utg_words.Word(type=utg_relations.WORD_TYPE.TEXT, forms=('4 юного квинта сырого месяца 2 года',), properties=utg_words.Properties())))

    def test_linguistics_restrictions__no_feasts(self):
        now = datetime.datetime(year=34, month=2, day=28, hour=0, minute=0, second=0)

        for feast in tt_calendar.REAL_FEAST.records:
            restriction_id = linguistics_restrictions.get(feast)
            self.assertNotIn(restriction_id, self.date.linguistics_restrictions(now))

    def test_linguistics_restrictions__has_feast(self):
        for feast in tt_calendar.REAL_FEAST.records:
            restriction_id = linguistics_restrictions.get(feast)
            for interval in feast.intervals:
                self.assertIn(restriction_id, self.date.linguistics_restrictions(interval[0] + (interval[1] - interval[0]) / 2))
