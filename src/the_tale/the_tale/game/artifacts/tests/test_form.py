
import smart_imports

smart_imports.all()


class ArtifactFormsTests(utils_testcase.TestCase):

    def setUp(self):
        super(ArtifactFormsTests, self).setUp()
        game_logic.create_test_map()

    def get_form_data(self):
        artifact = logic.create_random_artifact_record(uuid='sword')

        data = linguistics_helpers.get_word_post_data(artifact.utg_name, prefix='name')

        data.update({
            'level': '1',
            'type': 'ARTIFACT_TYPE.RING',
            'power_type': 'ARTIFACT_POWER_TYPE.NEUTRAL',
            'rare_effect': 'ARTIFACT_EFFECT.POISON',
            'epic_effect': 'ARTIFACT_EFFECT.GREAT_PHYSICAL_DAMAGE',
            'special_effect': 'ARTIFACT_EFFECT.NO_EFFECT',
            'description': 'artifact description',
            'weapon_type': 'WEAPON_TYPE.TYPE_1',
            'material': 'MATERIAL.MATERIAL_3',
            'uuid': 'some-uuid',
            'mob': ''})

        return data

    def test_success_mob_record_form(self):
        data = self.get_form_data()
        form = forms.ArtifactRecordForm(data)
        self.assertTrue(form.is_valid())

    def test_success_moderate_mob_record_form(self):
        data = self.get_form_data()
        form = forms.ModerateArtifactRecordForm(data)
        self.assertTrue(form.is_valid())
