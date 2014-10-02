# coding: utf-8

from the_tale.common.utils import testcase

from textgen.words import Noun

from dext.common.utils import s11n

from the_tale.game.logic import create_test_map

from the_tale.game.heroes.relations import ARCHETYPE

from the_tale.game.map.relations import TERRAIN

from the_tale.game.mobs.forms import MobRecordForm, ModerateMobRecordForm
from the_tale.game.mobs import relations
from the_tale.game.mobs import prototypes


class MobsFormsTests(testcase.TestCase):

    def setUp(self):
        super(MobsFormsTests, self).setUp()
        create_test_map()

    def get_form_data(self):
        mob = prototypes.MobRecordPrototype.create_random(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        initials = ModerateMobRecordForm.get_initials(mob)
        initials['level'] = unicode(initials['level'])
        initials['archetype'] = unicode(initials['archetype'])
        initials['abilities'] = list(initials['abilities'])
        initials['terrains'] = list(unicode(t) for t in initials['terrains'])

        return initials

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
