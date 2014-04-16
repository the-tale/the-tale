# coding: utf-8


from textgen.words import Noun

from dext.utils import s11n

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.artifacts import relations
from the_tale.game.artifacts.forms import ArtifactRecordForm, ModerateArtifactRecordForm


class ArtifactFormsTests(testcase.TestCase):

    def setUp(self):
        super(ArtifactFormsTests, self).setUp()
        create_test_map()

    def test_success_mob_record_form(self):
        form = ArtifactRecordForm({'level': '1',
                                   'type': relations.ARTIFACT_TYPE.USELESS,
                                   'power_type': relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                                   'name': 'mob name'})
        self.assertTrue(form.is_valid())

    def test_success_moderate_mob_record_form(self):
        form = ModerateArtifactRecordForm({'level': '1',
                                           'type': relations.ARTIFACT_TYPE.USELESS,
                                           'power_type': relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                                           'uuid': 'artifact_uuid',
                                           'name_forms': s11n.to_json(Noun(normalized='artifact name',
                                                                           forms=['artifact name'] * Noun.FORMS_NUMBER,
                                                                           properties=(u'мр',)).serialize())})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.c.name_forms.__class__, Noun)
