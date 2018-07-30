
import smart_imports

smart_imports.all()


class TestClient(timers.Client):

    def protobuf_to_type(self, type):
        return type

    def type_to_protobuf(self, type):
        return type


timers_client = TestClient(entry_point=accounts_conf.settings.TT_PLAYERS_TIMERS_EMPTY_POINTS)


class CreateTimerTests(utils_testcase.TestCase):

    def setUp(self):
        timers_client.cmd_debug_clear_service()

    def test_create_timer(self):
        timers_client.cmd_create_timer(owner_id=666,
                                       type=0,
                                       speed=14,
                                       border=15,
                                       entity_id=16,
                                       resources=3,
                                       callback_data='')

        timers = timers_client.cmd_get_owner_timers(owner_id=666)

        self.assertEqual(len(timers), 1)

        self.assertEqual(timers[0].entity_id, 16)
        self.assertEqual(timers[0].type, 0)
        self.assertEqual(timers[0].speed, 14)
        self.assertEqual(timers[0].border, 15)
        self.assertEqual(timers[0].resources, 3)

    def test_exception_in_error(self):
        timers_client.cmd_create_timer(owner_id=666,
                                       type=0,
                                       speed=14,
                                       border=15,
                                       entity_id=16,
                                       resources=3,
                                       callback_data='')

        with self.assertRaises(exceptions.CanNotCreateTimer):
            timers_client.cmd_create_timer(owner_id=666,
                                           type=0,
                                           speed=14,
                                           border=15,
                                           entity_id=16,
                                           resources=3,
                                           callback_data='')


class ChangeCardsTimerSpeedTests(utils_testcase.TestCase):

    def setUp(self):
        timers_client.cmd_debug_clear_service()

    def test_create_timer(self):
        timers_client.cmd_create_timer(owner_id=666,
                                       type=0,
                                       speed=14,
                                       border=15,
                                       entity_id=16,
                                       resources=3,
                                       callback_data='')

        timers_client.cmd_change_timer_speed(owner_id=666, speed=2, type=0, entity_id=16)

        timers = timers_client.cmd_get_owner_timers(owner_id=666)

        self.assertEqual(len(timers), 1)

        self.assertEqual(timers[0].entity_id, 16)
        self.assertEqual(timers[0].type, 0)
        self.assertEqual(timers[0].speed, 2)
        self.assertEqual(timers[0].border, 15)

    def test_exception_in_error(self):
        timers_client.cmd_create_timer(owner_id=666,
                                       type=0,
                                       speed=14,
                                       border=15,
                                       entity_id=16,
                                       resources=3,
                                       callback_data='')

        with self.assertRaises(exceptions.CanNotChangeTimerSpeed):
            timers_client.cmd_change_timer_speed(owner_id=777, speed=2, type=0)


class GetOwnerTimersTests(utils_testcase.TestCase):

    def setUp(self):
        timers_client.cmd_debug_clear_service()

    def test_create_timer(self):
        timers_client.cmd_create_timer(owner_id=666,
                                       type=0,
                                       speed=14,
                                       border=15,
                                       entity_id=16,
                                       resources=3,
                                       callback_data='')

        timers = timers_client.cmd_get_owner_timers(owner_id=666)

        self.assertEqual(len(timers), 1)

        self.assertEqual(timers[0].entity_id, 16)
        self.assertEqual(timers[0].type, 0)
        self.assertEqual(timers[0].speed, 14)
        self.assertEqual(timers[0].border, 15)
