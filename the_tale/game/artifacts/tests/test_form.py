# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.artifacts import forms
from the_tale.game.artifacts import prototypes

from the_tale.linguistics.tests import helpers as linguistics_helpers


class ArtifactFormsTests(testcase.TestCase):

    def setUp(self):
        super(ArtifactFormsTests, self).setUp()
        create_test_map()

    def get_form_data(self):
        artifact = prototypes.ArtifactRecordPrototype.create_random(uuid='sword')

        data = linguistics_helpers.get_word_post_data(artifact.utg_name, prefix='name')

        data.update({
                'level': '1',
                'type': 'ARTIFACT_TYPE.RING',
                'power_type': 'ARTIFACT_POWER_TYPE.NEUTRAL',
                'rare_effect': 'ARTIFACT_EFFECT.POISON',
                'epic_effect': 'ARTIFACT_EFFECT.GREAT_PHYSICAL_DAMAGE',
                'description': 'artifact description',
                'uuid': 'some-uuid',
                'mob':  u''})

        return data

    def test_success_mob_record_form(self):
        data = self.get_form_data()
        form = forms.ArtifactRecordForm(data)
        self.assertTrue(form.is_valid())

    def test_success_moderate_mob_record_form(self):
        data = self.get_form_data()
        form = forms.ModerateArtifactRecordForm(data)
        self.assertTrue(form.is_valid())
