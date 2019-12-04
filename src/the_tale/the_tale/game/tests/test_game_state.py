
import smart_imports

smart_imports.all()


class GameStateTests(utils_testcase.TestCase):

    def setUp(self):
        super(GameStateTests, self).setUp()
        global_settings.clear()

    def test_no_state(self):
        self.assertTrue(prototypes.GameState.is_stopped())
        self.assertFalse(prototypes.GameState.is_working())

    def test_stoped(self):
        prototypes.GameState.stop()
        self.assertTrue(prototypes.GameState.is_stopped())
        self.assertFalse(prototypes.GameState.is_working())

    def test_working(self):
        prototypes.GameState.start()
        self.assertFalse(prototypes.GameState.is_stopped())
        self.assertTrue(prototypes.GameState.is_working())
