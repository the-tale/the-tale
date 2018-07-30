
import smart_imports

smart_imports.all()


class MobsFormsTests(utils_testcase.TestCase):

    def setUp(self):
        super(MobsFormsTests, self).setUp()
        game_logic.create_test_map()

    def get_form_data(self):
        mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)

        data = linguistics_helpers.get_word_post_data(mob.utg_name, prefix='name')

        data.update({'level': str(mob.level),
                     'terrains': ['TERRAIN.PLANE_GRASS', 'TERRAIN.HILLS_GRASS'],
                     'abilities': ['hit', 'strong_hit', 'sidestep'],
                     'type': 'TYPE.CIVILIZED',
                     'archetype': 'ARCHETYPE.NEUTRAL',
                     'description': mob.description,
                     'communication_verbal': tt_beings_relations.COMMUNICATION_VERBAL.CAN,
                     'communication_gestures': tt_beings_relations.COMMUNICATION_GESTURES.CAN,
                     'communication_telepathic': tt_beings_relations.COMMUNICATION_TELEPATHIC.CAN,
                     'intellect_level': tt_beings_relations.INTELLECT_LEVEL.NORMAL,

                     'structure': 'STRUCTURE.STRUCTURE_1',
                     'features': ['FEATURE.FEATURE_1', 'FEATURE.FEATURE_7'],
                     'movement': 'MOVEMENT.MOVEMENT_2',
                     'body': 'BODY.BODY_3',
                     'size': 'SIZE.SIZE_4',
                     'orientation': 'ORIENTATION.HORIZONTAL',
                     'weapon_1': 'STANDARD_WEAPON.WEAPON_1',
                     'material_1': 'MATERIAL.MATERIAL_1',
                     'power_type_1': 'ARTIFACT_POWER_TYPE.NEUTRAL',
                     'weapon_2': 'STANDARD_WEAPON.WEAPON_10',
                     'material_2': 'MATERIAL.MATERIAL_10',
                     'power_type_2': 'ARTIFACT_POWER_TYPE.MOST_PHYSICAL', })

        return data

    def test_no_abilities_choosen(self):
        data = self.get_form_data()
        data['abilities'] = []
        form = forms.MobRecordForm(data)
        self.assertFalse(form.is_valid())

    def test_wrong_ability_id(self):
        data = self.get_form_data()
        data['abilities'] = ['bla-ability']
        form = forms.MobRecordForm(data)
        self.assertFalse(form.is_valid())

    def test_no_terrains_choosen(self):
        data = self.get_form_data()
        data['terrains'] = []
        form = forms.MobRecordForm(data)
        self.assertFalse(form.is_valid())

    def test_wrong_terrain_id(self):
        data = self.get_form_data()
        data['terrains'] = ['lba']
        form = forms.MobRecordForm(data)
        self.assertFalse(form.is_valid())

    def test_success_mob_record_form(self):
        data = self.get_form_data()
        form = forms.MobRecordForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.c.abilities.__class__, frozenset)
        self.assertEqual(form.c.terrains.__class__, frozenset)

    def test_success_moderate_mob_record_form(self):
        data = self.get_form_data()
        form = forms.MobRecordForm(data)
        form.is_valid()
        self.assertTrue(form.is_valid())
