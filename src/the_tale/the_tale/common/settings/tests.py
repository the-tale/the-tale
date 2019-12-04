
import smart_imports

smart_imports.all()


class SettingsTest(utils_testcase.TestCase):

    def setUp(self):
        from . import Settings
        self.settings = Settings()

    def test_set_wrong_key(self):
        self.assertRaises(exceptions.WrongKeyType, self.settings.__setitem__, 1, 'value')

    def test_set_wrong_value(self):
        self.assertRaises(exceptions.WrongValueType, self.settings.__setitem__, 'key', 1)

    def test_set_with_create(self):
        self.assertEqual(models.Setting.objects.all().count(), 0)

        self.settings['key'] = 'value'

        self.assertEqual(models.Setting.objects.all().count(), 1)

        record = models.Setting.objects.all()[0]
        self.assertEqual(record.key, 'key')
        self.assertEqual(record.value, 'value')

    def test_set_without_create(self):

        self.assertEqual(models.Setting.objects.all().count(), 0)

        self.settings['key'] = 'value'
        self.assertEqual(models.Setting.objects.all().count(), 1)
        self.settings['key'] = 'value 2'

        self.assertEqual(models.Setting.objects.all().count(), 1)

        record = models.Setting.objects.all()[0]
        self.assertEqual(record.key, 'key')
        self.assertEqual(record.value, 'value 2')

    def test_get_wrong_key(self):
        self.settings['key'] = 'value'
        self.assertRaises(exceptions.WrongKeyType, self.settings.__getitem__, 1)

    def test_get_no_value(self):
        self.settings['key'] = 'value'
        self.assertRaises(exceptions.UnregisteredKey, self.settings.__getitem__, 'unknown key')

    def test_get(self):
        self.settings['key'] = 'value'
        self.assertEqual(self.settings['key'], 'value')

    def test_refresh(self):
        models.Setting.objects.create(key='key 1', value='value 1')
        models.Setting.objects.create(key='ключ 2', value='значение 2')
        self.settings.refresh()
        self.assertEqual(self.settings['key 1'], 'value 1')
        self.assertEqual(self.settings['ключ 2'], 'значение 2')

    def test_model_delete(self):
        model = models.Setting.objects.create(key='key 1', value='value 1')

        model.delete()

        self.assertEqual(models.Setting.objects.all().count(), 0)

    def test_delitem_wrong_key(self):
        self.settings['key'] = 'value'
        self.assertRaises(exceptions.WrongKeyType, self.settings.__delitem__, 1)

    def test_delitem_no_key(self):
        self.settings['key'] = 'value'
        self.assertRaises(exceptions.KeyNotInSettings, self.settings.__delitem__, 'key_2')

    def test_delitem(self):
        self.settings['key'] = 'value'
        self.assertEqual(models.Setting.objects.all().count(), 1)
        self.assertEqual(self.settings.get('key'), 'value')
        del self.settings['key']
        self.assertEqual(models.Setting.objects.all().count(), 0)
        self.assertEqual(self.settings.get('key'), None)
