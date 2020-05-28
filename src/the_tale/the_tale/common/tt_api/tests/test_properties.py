
import smart_imports

smart_imports.all()


class TestClient(properties.Client):
    pass


class TEST_PROPERTIES(properties.PROPERTIES):
    records = (('test_1', 0, 'тест 1', lambda x: x, lambda x: x, None, tt_api_properties.TYPE.REPLACE),
               ('test_2', 1, 'тест 2', str, int, list, tt_api_properties.TYPE.APPEND))


properties_client = TestClient(entry_point=accounts_conf.settings.TT_PLAYERS_PROPERTIES_ENTRY_POINT,
                               properties=TEST_PROPERTIES)


class SetGetTests(utils_testcase.TestCase):

    def setUp(self):
        properties_client.cmd_debug_clear_service()

    def test_simple(self):
        properties_client.cmd_set_properties([(666, 'test_1', 'x.1')])
        properties = properties_client.cmd_get_properties({666: ['test_1']})

        self.assertEqual(properties[666].test_1, 'x.1')
        self.assertEqual(properties[666].test_2, 100500)

    def test_multiple(self):
        properties_client.cmd_set_properties([(666, 'test_1', 'x.1'),
                                              (777, 'test_2', 13),
                                              (888, 'test_1', 'x.2'),
                                              (888, 'test_2', 14)])

        properties = properties_client.cmd_get_properties({666: ['test_1'],
                                                           777: ['test_1', 'test_2'],
                                                           888: ['test_1', 'test_2']})

        self.assertEqual(properties[666].test_1, 'x.1')
        self.assertEqual(properties[666].test_2, 100500)
        self.assertEqual(properties[777].test_1, None)
        self.assertEqual(properties[777].test_2, 13)
        self.assertEqual(properties[888].test_1, 'x.2')
        self.assertEqual(properties[888].test_2, 14)

    def test_types(self):
        properties_client.cmd_set_properties([(666, 'test_1', 'x.1'),
                                              (777, 'test_2', 13),
                                              (666, 'test_1', 'x.2'),
                                              (777, 'test_2', 14)])

        properties = properties_client.cmd_get_properties({666: ['test_1', 'test_2'],
                                                           777: ['test_1', 'test_2']})

        self.assertEqual(properties[666].test_1, 'x.2')
        self.assertEqual(properties[666].test_2, [])
        self.assertEqual(properties[777].test_1, None)
        self.assertEqual(properties[777].test_2, [13, 14])

    def test_unknown_property(self):
        with self.assertRaises(exceptions.TTPropertiesError):
            properties_client.cmd_set_properties([(666, 'unknown', 'x.1')])

        with self.assertRaises(exceptions.TTPropertiesError):
            properties_client.cmd_get_properties({666: ['unknown']})


class SetGetSimplifiedTests(utils_testcase.TestCase):

    def setUp(self):
        properties_client.cmd_debug_clear_service()

    def test_simple(self):
        properties_client.cmd_set_property(object_id=666, name='test_1', value='x.1')
        value = properties_client.cmd_get_object_property(object_id=666, name='test_1')
        self.assertEqual(value, 'x.1')

    def test_default(self):
        value = properties_client.cmd_get_object_property(object_id=666, name='test_2')
        self.assertEqual(value, 100500)

    def test_wrong_properties(self):

        with self.assertRaises(exceptions.TTPropertiesError):
            properties_client.cmd_set_property(object_id=666, name='unknown', value='x.1')

        with self.assertRaises(exceptions.TTPropertiesError):
            properties_client.cmd_get_object_property(object_id=666, name='unknown')


class GetAllObjectProperties(utils_testcase.TestCase):

    def setUp(self):
        properties_client.cmd_debug_clear_service()

    def test_simple(self):
        properties_client.cmd_set_properties([(666, 'test_1', 'x.1'),
                                              (666, 'test_2', 13),
                                              (777, 'test_2', 14)])

        properties = properties_client.cmd_get_all_object_properties(object_id=666)
        self.assertEqual(properties.test_1, 'x.1')
        self.assertEqual(properties.test_2, 13)

        properties = properties_client.cmd_get_all_object_properties(object_id=777)
        self.assertEqual(properties.test_1, None)
        self.assertEqual(properties.test_2, 14)
