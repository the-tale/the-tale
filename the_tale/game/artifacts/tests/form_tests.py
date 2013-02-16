# coding: utf-8

from django.test import TestCase

from textgen.words import Noun

from dext.utils import s11n

from game.logic import create_test_map

from game.artifacts.models import RARITY_TYPE, ARTIFACT_TYPE
from game.artifacts.forms import ArtifactRecordForm, ModerateArtifactRecordForm


class ArtifactFormsTests(TestCase):

    def setUp(self):
        create_test_map()

    def test_success_mob_record_form(self):
        form = ArtifactRecordForm({'level': '1',
                                   'type': ARTIFACT_TYPE.USELESS,
                                   'rarity': RARITY_TYPE.NORMAL,
                                   'name': 'mob name'})
        self.assertTrue(form.is_valid())

    def test_success_moderate_mob_record_form(self):
        form = ModerateArtifactRecordForm({'level': '1',
                                           'type': ARTIFACT_TYPE.USELESS,
                                           'rarity': RARITY_TYPE.NORMAL,
                                           'uuid': 'artifact_uuid',
                                           'name_forms': s11n.to_json(Noun(normalized='artifact name',
                                                                           forms=['artifact name'] * Noun.FORMS_NUMBER,
                                                                           properties=(u'мр',)).serialize())})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.c.name_forms.__class__, Noun)
