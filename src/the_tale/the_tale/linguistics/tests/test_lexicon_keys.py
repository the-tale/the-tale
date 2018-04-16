
from the_tale.common.utils.testcase import TestCase

from ..lexicon import keys
from ..lexicon import relations


class LexiconKeysTests(TestCase):

    def setUp(self):
        super(LexiconKeysTests, self).setUp()

    def test_weapon_variables(self):
        check_pairs = [(relations.VARIABLE.HERO, relations.VARIABLE.HERO__WEAPON),
                       (relations.VARIABLE.KILLER, relations.VARIABLE.KILLER__WEAPON),
                       (relations.VARIABLE.VICTIM, relations.VARIABLE.VICTIM__WEAPON),
                       (relations.VARIABLE.DUELIST_1, relations.VARIABLE.DUELIST_1__WEAPON),
                       (relations.VARIABLE.DUELIST_2, relations.VARIABLE.DUELIST_2__WEAPON),
                       (relations.VARIABLE.MOB, relations.VARIABLE.MOB__WEAPON),
                       (relations.VARIABLE.ATTACKER, relations.VARIABLE.ATTACKER__WEAPON),
                       (relations.VARIABLE.DEFENDER, relations.VARIABLE.DEFENDER__WEAPON),
                       (relations.VARIABLE.COMPANION, relations.VARIABLE.COMPANION__WEAPON),
                       (relations.VARIABLE.COMPANION_OWNER, relations.VARIABLE.COMPANION_OWNER__WEAPON)]

        for key in keys.LEXICON_KEY.records:
            if key.group.is_HERO_HISTORY:
                continue

            for variable, weapon in check_pairs:
                self.assertEqual(variable in key.variables, weapon in key.variables)
