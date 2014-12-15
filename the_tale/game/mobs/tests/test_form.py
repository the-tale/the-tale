# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.mobs.forms import MobRecordForm
from the_tale.game.mobs import relations
from the_tale.game.mobs import prototypes

from the_tale.linguistics.tests import helpers as linguistics_helpers


class MobsFormsTests(testcase.TestCase):

    def setUp(self):
        super(MobsFormsTests, self).setUp()
        create_test_map()

    def get_form_data(self):
        mob = prototypes.MobRecordPrototype.create_random(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)

        data = linguistics_helpers.get_word_post_data(mob.utg_name, prefix='name')

        data.update( { 'level': str(mob.level),
                       'global_action_probability': '0.25',
                       'terrains': ['TERRAIN.PLANE_GRASS', 'TERRAIN.HILLS_GRASS'],
                       'abilities': ['hit', 'strong_hit', 'sidestep'],
                       'type': 'MOB_TYPE.CIVILIZED',
                       'archetype': 'ARCHETYPE.NEUTRAL',
                       'description': mob.description} )

        return data

    def test_no_abilities_choosen(self):
        data = self.get_form_data()
        data['abilities'] = []
        form = MobRecordForm(data)
        self.assertFalse(form.is_valid())

    def test_wrong_ability_id(self):
        data = self.get_form_data()
        data['abilities'] = ['bla-ability']
        form = MobRecordForm(data)
        self.assertFalse(form.is_valid())

    def test_no_terrains_choosen(self):
        data = self.get_form_data()
        data['terrains'] = []
        form = MobRecordForm(data)
        self.assertFalse(form.is_valid())

    def test_wrong_terrain_id(self):
        data = self.get_form_data()
        data['terrains'] = ['lba']
        form = MobRecordForm(data)
        self.assertFalse(form.is_valid())

    def test_success_mob_record_form(self):
        data = self.get_form_data()
        form = MobRecordForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.c.abilities.__class__, frozenset)
        self.assertEqual(form.c.terrains.__class__, frozenset)

    def test_success_moderate_mob_record_form(self):
        data = self.get_form_data()
        form = MobRecordForm(data)
        self.assertTrue(form.is_valid())
