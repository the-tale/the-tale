# coding: utf-8

from dext.settings.models import Setting
from dext.settings import settings

from the_tale.common.utils import testcase

from the_tale.game.prototypes import GameState


class GameStateTests(testcase.TestCase):

    def setUp(self):
        super(GameStateTests, self).setUp()
        Setting.objects.all().delete()
        settings.refresh()

    def test_no_state(self):
        self.assertTrue(GameState.is_stopped())
        self.assertFalse(GameState.is_working())

    def test_stoped(self):
        GameState.stop()
        self.assertTrue(GameState.is_stopped())
        self.assertFalse(GameState.is_working())

    def test_working(self):
        GameState.start()
        self.assertFalse(GameState.is_stopped())
        self.assertTrue(GameState.is_working())
