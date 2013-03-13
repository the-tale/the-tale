# coding: utf-8

from common.utils import testcase

from textgen.words import Noun

from dext.utils import s11n

from game.logic import create_test_map

from game.map.relations import TERRAIN

from game.mobs.forms import MobRecordForm, ModerateMobRecordForm


class MobsFormsTests(testcase.TestCase):

    def setUp(self):
        super(MobsFormsTests, self).setUp()
        create_test_map()

    def test_no_abilities_choosen(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [str(TERRAIN.PLANE_GRASS)],
                              'abilities': [],
                              'name': 'mob name'})
        self.assertFalse(form.is_valid())

    def test_wrong_ability_id(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [str(TERRAIN.PLANE_GRASS)],
                              'abilities': ['bla-ability'],
                              'name': 'mob name'})
        self.assertFalse(form.is_valid())

    def test_no_terrains_choosen(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [],
                              'abilities': ['hit'],
                              'name': 'mob name'})
        self.assertFalse(form.is_valid())

    def test_wrong_terrain_id(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [str(666)],
                              'abilities': ['hit'],
                              'name': 'mob name'})
        self.assertFalse(form.is_valid())

    def test_success_mob_record_form(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [str(TERRAIN.PLANE_GRASS)],
                              'abilities': ['hit'],
                              'name': 'mob name'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.c.abilities.__class__, frozenset)
        self.assertEqual(form.c.terrains.__class__, frozenset)

    def test_success_moderate_mob_record_form(self):
        form = ModerateMobRecordForm({'level': '1',
                                      'terrains': [str(TERRAIN.PLANE_GRASS)],
                                      'abilities': ['hit'],
                                      'name': 'mob name',
                                      'uuid': 'mob_uuid',
                                      'name_forms': s11n.to_json(Noun(normalized='mob name',
                                                                      forms=['mob name'] * Noun.FORMS_NUMBER,
                                                                      properties=(u'мр',)).serialize())})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.c.name_forms.__class__, Noun)
