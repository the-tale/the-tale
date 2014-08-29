# coding: utf-8

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics.lexicon import logic
from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon import relations


class LexiconLogicTests(TestCase):

    def setUp(self):
        super(LexiconLogicTests, self).setUp()


    def test_get_verificators_externals(self):
        verificators = logic.get_verificators_externals(keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP)

        self.assertEqual(verificators,
                         [{relations.VARIABLE.HERO.value: u'призрак', relations.VARIABLE.LEVEL.value: 13},
                          {relations.VARIABLE.HERO.value: u'привидение', relations.VARIABLE.LEVEL.value: 13},
                          {relations.VARIABLE.HERO.value: u'русалка', relations.VARIABLE.LEVEL.value: 13}])
