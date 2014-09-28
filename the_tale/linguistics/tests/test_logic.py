# coding: utf-8
import random
import collections

from django.db import IntegrityError
from django.db import transaction

from utg import templates as utg_templates

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations
from the_tale.linguistics import logic

from the_tale.linguistics.lexicon import relations as lexicon_relations
from the_tale.linguistics.lexicon import dictionary as lexicon_dictinonary
from the_tale.linguistics.lexicon import keys

from the_tale.linguistics.lexicon.groups import relations as groups_relations


class LogicTests(TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()


    def test_get_templates_count(self):
        key_1 = random.choice(keys.LEXICON_KEY.records)
        key_2 = random.choice(keys.LEXICON_KEY.records)

        utg_template_1 = utg_templates.Template()
        utg_template_1.parse(u'some-text', externals=[v.value for v in key_1.variables])

        utg_template_2 = utg_templates.Template()
        utg_template_2.parse(u'some-text-2', externals=[v.value for v in key_2.variables])

        template_1_1 = prototypes.TemplatePrototype.create(key=key_1, raw_template=u'template-1-1', utg_template=utg_template_1, verificators=[], author=None)
        template_1_2 = prototypes.TemplatePrototype.create(key=key_1, raw_template=u'template-1-2', utg_template=utg_template_1, verificators=[], author=None)

        template_2_1 = prototypes.TemplatePrototype.create(key=key_2, raw_template=u'template-2-1', utg_template=utg_template_2, verificators=[], author=None)

        template_1_1.state = relations.TEMPLATE_STATE.IN_GAME
        template_1_1.save()

        template_1_2.state = relations.TEMPLATE_STATE.IN_GAME
        template_1_2.save()

        template_2_1.state = relations.TEMPLATE_STATE.IN_GAME
        template_2_1.save()

        groups_count, keys_count = logic.get_templates_count()

        if key_1.group == key_2.group:
            for group in groups_relations.LEXICON_GROUP.records:
                if group == key_1.group:
                    self.assertEqual(groups_count[group], 3)
                else:
                    self.assertEqual(groups_count[group], 0)

        else:
            for group in groups_relations.LEXICON_GROUP.records:
                if group == key_1.group:
                    self.assertEqual(groups_count[group], 2)
                elif group == key_2.group:
                    self.assertEqual(groups_count[group], 1)
                else:
                    self.assertEqual(groups_count[group], 0)


        if key_1 == key_2:
            for key in keys.LEXICON_KEY.records:
                if key == key_1:
                    self.assertEqual(keys_count[key], 3)
                else:
                    self.assertEqual(keys_count[key], 0)
        else:
            for key in keys.LEXICON_KEY.records:
                if key == key_1:
                    self.assertEqual(keys_count[key], 2)
                elif key == key_2:
                    self.assertEqual(keys_count[key], 1)
                else:
                    self.assertEqual(keys_count[key], 0)
