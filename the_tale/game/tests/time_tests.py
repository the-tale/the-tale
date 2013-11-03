# coding: utf-8

from the_tale.common.utils import testcase

from dext.settings import settings
from dext.settings.models import Setting

from the_tale.game.prototypes import TimePrototype, GameTime


class TimeTest(testcase.TestCase):

    def test_creation(self):
        Setting.objects.all().delete()
        settings.refresh()

        settings_number = Setting.objects.all().count()
        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 0)
        self.assertEqual(Setting.objects.all().count(), settings_number+1)
        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 0)
        self.assertEqual(Setting.objects.all().count(), settings_number+1)

    def test_get_current_time(self):
        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 0)
        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 0)

    def test_increment_turn(self):
        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 0)

        time.increment_turn()
        self.assertEqual(time.turn_number, 1)
        time.save()

        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 1)

    def test_ui_info(self):
        time = TimePrototype.get_current_time()
        self.assertEqual(time.turn_number, 0)
        time.increment_turn()

        self.assertEqual(time.ui_info()['number'], 1)

    def test_game_time(self):
        time = TimePrototype.get_current_time()
        self.assertEqual(time.game_time, GameTime(0,1,1,0,0,0))

        time.increment_turn()
        self.assertEqual(time.game_time, GameTime(0,1,1,0,2,0))
