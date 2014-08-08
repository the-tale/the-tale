# coding: utf-8

from the_tale.common.utils import testcase

from textgen.words import Noun

from dext.common.utils import s11n

from the_tale.game.logic import create_test_map

from the_tale.game.heroes.relations import ARCHETYPE

from the_tale.game.map.relations import TERRAIN

from the_tale.game.mobs.forms import MobRecordForm, ModerateMobRecordForm
from the_tale.game.mobs.relations import MOB_TYPE


class MobsFormsTests(testcase.TestCase):

    def setUp(self):
        super(MobsFormsTests, self).setUp()
        create_test_map()

    def test_no_abilities_choosen(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [str(TERRAIN.PLANE_GRASS)],
                              'abilities': [],
                              'type': MOB_TYPE.CIVILIZED,
                              'archetype': ARCHETYPE.NEUTRAL,
                              'name': 'mob name'})
        self.assertFalse(form.is_valid())

    def test_wrong_ability_id(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [str(TERRAIN.PLANE_GRASS)],
                              'abilities': ['bla-ability'],
                              'type': MOB_TYPE.CIVILIZED,
                              'archetype': ARCHETYPE.NEUTRAL,
                              'name': 'mob name'})
        self.assertFalse(form.is_valid())

    def test_no_terrains_choosen(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [],
                              'abilities': ['hit'],
                              'type': MOB_TYPE.CIVILIZED,
                              'archetype': ARCHETYPE.NEUTRAL,
                              'name': 'mob name'})
        self.assertFalse(form.is_valid())

    def test_wrong_terrain_id(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [str(666)],
                              'abilities': ['hit'],
                              'type': MOB_TYPE.CIVILIZED,
                              'archetype': ARCHETYPE.NEUTRAL,
                              'name': 'mob name'})
        self.assertFalse(form.is_valid())

    def test_success_mob_record_form(self):
        form = MobRecordForm({'level': '1',
                              'terrains': [str(TERRAIN.PLANE_GRASS)],
                              'abilities': ['hit'],
                              'type': MOB_TYPE.CIVILIZED,
                              'archetype': ARCHETYPE.NEUTRAL,
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
                                      'type': MOB_TYPE.CIVILIZED,
                                      'archetype': ARCHETYPE.NEUTRAL,
                                      'name_forms': s11n.to_json(Noun(normalized='mob name',
                                                                      forms=['mob name'] * Noun.FORMS_NUMBER,
                                                                      properties=(u'мр',)).serialize())})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.c.name_forms.__class__, Noun)
