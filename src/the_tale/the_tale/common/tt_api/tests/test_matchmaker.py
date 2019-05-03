
import smart_imports

smart_imports.all()


class TEST_MATCHMAKER_TYPE(rels_django.DjangoEnum):
    records = (('TYPE_1', 0, 'type 1'),
               ('TYPE_2', 1, 'type 2'))


class TestClient(matchmaker.Client):

    def protobuf_to_battle_request(self, pb_battle_request):
        return pb_battle_request

    def protobuf_to_battle(self, pb_battle):
        return pb_battle


matchmaker_client = TestClient(entry_point=pvp_conf.settings.TT_MATCHMAKER_ENTRY_POINT)


# cmd_get_battle_requests and cmd_get_info are tested with other commands


class CreateBattleRequestTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        matchmaker_client.cmd_debug_clear_service()

    def test(self):
        battle_request_id = matchmaker_client.cmd_create_battle_request(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_1,
                                                                        initiator_id=666)

        battle_requests = matchmaker_client.cmd_get_battle_requests(battle_requests_ids=[battle_request_id])

        self.assertEqual(len(battle_requests), 1)

        self.assertEqual(battle_requests[0].id, battle_request_id)
        self.assertEqual(battle_requests[0].initiator_id, 666)
        self.assertEqual(battle_requests[0].matchmaker_type, TEST_MATCHMAKER_TYPE.TYPE_1.value)


class CancelBattleRequestTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        matchmaker_client.cmd_debug_clear_service()

    def test(self):
        matchmaker_client.cmd_cancel_battle_request(battle_request_id=100500)

        battle_request_id = matchmaker_client.cmd_create_battle_request(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_1,
                                                                        initiator_id=666)

        matchmaker_client.cmd_cancel_battle_request(battle_request_id=battle_request_id)

        battle_requests = matchmaker_client.cmd_get_battle_requests(battle_requests_ids=[battle_request_id])

        self.assertEqual(len(battle_requests), 0)


class AcceptBattleRequestTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        matchmaker_client.cmd_debug_clear_service()

    def test_success(self):
        battle_request_id = matchmaker_client.cmd_create_battle_request(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_1,
                                                                        initiator_id=666)

        result, battle_id, participants_ids = matchmaker_client.cmd_accept_battle_request(battle_request_id=battle_request_id,
                                                                                          acceptor_id=777)

        self.assertTrue(result.is_SUCCESS)
        self.assertNotEqual(battle_id, None)
        self.assertEqual(set(participants_ids), {666, 777})

        battle_requests, active_battles = matchmaker_client.cmd_get_info(matchmaker_types=TEST_MATCHMAKER_TYPE.records)

        self.assertEqual(len(battle_requests), 0)
        self.assertEqual(active_battles[TEST_MATCHMAKER_TYPE.TYPE_1], 1)

    def test_no_battle_request(self):
        result, battle_id, participants_ids = matchmaker_client.cmd_accept_battle_request(battle_request_id=100500,
                                                                                          acceptor_id=777)

        self.assertTrue(result.is_NO_BATTLE_REQUEST)
        self.assertEqual(battle_id, None)
        self.assertEqual(participants_ids, None)

        battle_requests, active_battles = matchmaker_client.cmd_get_info(matchmaker_types=TEST_MATCHMAKER_TYPE.records)

        self.assertEqual(len(battle_requests), 0)
        self.assertEqual(active_battles[TEST_MATCHMAKER_TYPE.TYPE_1], 0)

    def test_participants_intersection(self):
        battle_request_1_id = matchmaker_client.cmd_create_battle_request(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_1,
                                                                          initiator_id=666)
        battle_request_2_id = matchmaker_client.cmd_create_battle_request(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_2,
                                                                          initiator_id=777)

        result, battle_id, participants_ids = matchmaker_client.cmd_accept_battle_request(battle_request_id=battle_request_2_id,
                                                                                          acceptor_id=888)
        self.assertTrue(result.is_SUCCESS)
        self.assertNotEqual(battle_id, None)
        self.assertNotEqual(participants_ids, None)

        result, battle_id, participants_ids = matchmaker_client.cmd_accept_battle_request(battle_request_id=battle_request_1_id,
                                                                                          acceptor_id=888)

        self.assertTrue(result.is_ALREADY_IN_BATTLE)
        self.assertEqual(battle_id, None)
        self.assertEqual(participants_ids, None)

        battle_requests, active_battles = matchmaker_client.cmd_get_info(matchmaker_types=TEST_MATCHMAKER_TYPE.records)

        self.assertEqual(len(battle_requests), 1)
        self.assertEqual(battle_requests[0].id, battle_request_1_id)

        self.assertEqual(active_battles[TEST_MATCHMAKER_TYPE.TYPE_1], 0)
        self.assertEqual(active_battles[TEST_MATCHMAKER_TYPE.TYPE_2], 1)


class CreateBattleTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        matchmaker_client.cmd_debug_clear_service()

    def test_success(self):
        result, battle_id = matchmaker_client.cmd_create_battle(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_1,
                                                                participants_ids=(666, 777))

        self.assertTrue(result.is_SUCCESS)
        self.assertNotEqual(battle_id, None)

        battle_requests, active_battles = matchmaker_client.cmd_get_info(matchmaker_types=TEST_MATCHMAKER_TYPE.records)

        self.assertEqual(len(battle_requests), 0)
        self.assertEqual(active_battles[TEST_MATCHMAKER_TYPE.TYPE_1], 1)

    def test_participants_intersection(self):
        battle_request_id = matchmaker_client.cmd_create_battle_request(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_2,
                                                                        initiator_id=777)

        result, battle_id, participants_ids = matchmaker_client.cmd_accept_battle_request(battle_request_id=battle_request_id,
                                                                                          acceptor_id=888)
        self.assertTrue(result.is_SUCCESS)
        self.assertNotEqual(battle_id, None)
        self.assertNotEqual(participants_ids, None)

        result, battle_id = matchmaker_client.cmd_create_battle(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_1,
                                                                participants_ids=(666, 777))

        self.assertTrue(result.is_ALREADY_IN_BATTLE)
        self.assertEqual(battle_id, None)

        battle_requests, active_battles = matchmaker_client.cmd_get_info(matchmaker_types=TEST_MATCHMAKER_TYPE.records)

        self.assertEqual(len(battle_requests), 0)

        self.assertEqual(active_battles[TEST_MATCHMAKER_TYPE.TYPE_1], 0)
        self.assertEqual(active_battles[TEST_MATCHMAKER_TYPE.TYPE_2], 1)


class FinishBattleTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        matchmaker_client.cmd_debug_clear_service()

    def test_success(self):
        battle_request_id = matchmaker_client.cmd_create_battle_request(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_1,
                                                                        initiator_id=666)

        result, battle_id, participants_ids = matchmaker_client.cmd_accept_battle_request(battle_request_id=battle_request_id,
                                                                                          acceptor_id=777)

        self.assertTrue(result.is_SUCCESS)
        self.assertNotEqual(battle_id, None)

        matchmaker_client.cmd_finish_battle(battle_id=battle_id)

        battle_requests, active_battles = matchmaker_client.cmd_get_info(matchmaker_types=TEST_MATCHMAKER_TYPE.records)

        self.assertEqual(len(battle_requests), 0)
        self.assertEqual(active_battles[TEST_MATCHMAKER_TYPE.TYPE_1], 0)


class GetBattlesByParticipantsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        matchmaker_client.cmd_debug_clear_service()

    def test_no_battles(self):
        battles = matchmaker_client.cmd_get_battles_by_participants(participants_ids=(666,))

        self.assertEqual(len(battles), 0)

    def test_has_battles(self):
        result, battle_1_id = matchmaker_client.cmd_create_battle(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_1,
                                                                  participants_ids=(666, 777))
        result, battle_2_id = matchmaker_client.cmd_create_battle(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_2,
                                                                  participants_ids=(888, 999, 111))
        result, battle_3_id = matchmaker_client.cmd_create_battle(matchmaker_type=TEST_MATCHMAKER_TYPE.TYPE_1,
                                                                  participants_ids=(222, 333))

        battles = matchmaker_client.cmd_get_battles_by_participants(participants_ids=(222, 888))

        self.assertEqual(len(battles), 2)

        self.assertEqual(battles[0].id, battle_2_id)
        self.assertEqual(battles[0].matchmaker_type, TEST_MATCHMAKER_TYPE.TYPE_2.value)
        self.assertEqual(set(battles[0].participants_ids), {888, 999, 111})

        self.assertEqual(battles[1].id, battle_3_id)
        self.assertEqual(battles[1].matchmaker_type, TEST_MATCHMAKER_TYPE.TYPE_1.value)
        self.assertEqual(set(battles[1].participants_ids), {222, 333})
