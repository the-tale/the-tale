# coding: utf-8

from dext.forms import forms

from the_tale.common.utils import testcase

from the_tale.common.utils.forms import NounFormsWithoutNumberField


class NounFormsWithoutNumber(forms.Form):
    name_forms = NounFormsWithoutNumberField(label=u'')



class TestNounFormsWithoutNumberField(testcase.TestCase):

    NORMAL_DATA = {'name_forms_0': 'xxx name',
                   'name_forms_1': 'xxx name',
                   'name_forms_2': 'xxx name',
                   'name_forms_3': 'xxx name',
                   'name_forms_4': 'xxx name',
                   'name_forms_5': 'xxx name'}

    XSS_DATA = {'name_forms_0': 'xxx<tag>',
                'name_forms_1': 'xxx<tag>',
                'name_forms_2': 'xxx<tag>',
                'name_forms_3': 'xxx<tag>',
                'name_forms_4': 'xxx<tag>',
                'name_forms_5': 'xxx<tag>'}

    def setUp(self):
        super(TestNounFormsWithoutNumberField, self).setUp()

    def test_normal_data(self):

        form = NounFormsWithoutNumber(self.NORMAL_DATA)

        self.assertTrue(form.is_valid())


        self.assertEqual(form.c.name_forms,
                         ['xxx name', 'xxx name', 'xxx name', 'xxx name', 'xxx name', 'xxx name'])


    def test_xss_protect(self):

        form = NounFormsWithoutNumber(self.XSS_DATA)

        self.assertFalse(form.is_valid())
