
import smart_imports

smart_imports.all()

uniquer_client = emissaries_tt_services.events_effects_ids


class TTAPiTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()
        uniquer_client.cmd_debug_clear_service()

    def test(self):
        key_1 = uuid.uuid4().hex

        key_1_id = uniquer_client.cmd_get_id(key_1)
        same_key_1_id = uniquer_client.cmd_get_id(key_1)
        self.assertEqual(key_1_id, same_key_1_id)

        self.assertEqual(uniquer_client._cache[key_1], key_1_id)

        key_2 = uuid.uuid4().hex

        key_2_id = uniquer_client.cmd_get_id(key_2)
        same_key_2_id = uniquer_client.cmd_get_id(key_2)
        self.assertEqual(key_2_id, same_key_2_id)

        self.assertNotEqual(key_1_id, key_2_id)

        # test returning of old key
        same_key_1_id = uniquer_client.cmd_get_id(key_1)
        self.assertEqual(key_1_id, same_key_1_id)
