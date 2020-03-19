
import smart_imports

smart_imports.all()


class EmailFieldTest(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.field = fields.EmailField()

    def test_clean__right_dog(self):
        self.assertEqual(self.field.clean('Bla@Bla.blA'), 'bla@bla.bla')
