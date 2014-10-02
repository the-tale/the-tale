# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.artifacts import forms
from the_tale.game.artifacts import prototypes


class ArtifactFormsTests(testcase.TestCase):

    def setUp(self):
        super(ArtifactFormsTests, self).setUp()
        create_test_map()

    def get_form_data(self):
        artifact = prototypes.ArtifactRecordPrototype.create_random(uuid='sword')
        initials = forms.ModerateArtifactRecordForm.get_initials(artifact)
        initials['level'] = unicode(initials['level'])

        return initials


    def test_success_mob_record_form(self):
        data = self.get_form_data()
        form = forms.ArtifactRecordForm(data)
        self.assertTrue(form.is_valid())

    def test_success_moderate_mob_record_form(self):
        data = self.get_form_data()
        form = forms.ModerateArtifactRecordForm(data)
        self.assertTrue(form.is_valid())
