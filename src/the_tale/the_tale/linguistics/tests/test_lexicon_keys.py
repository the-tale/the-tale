
import smart_imports

smart_imports.all()


class LexiconKeysTests(utils_testcase.TestCase):

    def setUp(self):
        super(LexiconKeysTests, self).setUp()

    def test_weapon_variables(self):
        check_pairs = [(lexicon_relations.VARIABLE.HERO, lexicon_relations.VARIABLE.HERO__WEAPON),
                       (lexicon_relations.VARIABLE.KILLER, lexicon_relations.VARIABLE.KILLER__WEAPON),
                       (lexicon_relations.VARIABLE.VICTIM, lexicon_relations.VARIABLE.VICTIM__WEAPON),
                       (lexicon_relations.VARIABLE.DUELIST_1, lexicon_relations.VARIABLE.DUELIST_1__WEAPON),
                       (lexicon_relations.VARIABLE.DUELIST_2, lexicon_relations.VARIABLE.DUELIST_2__WEAPON),
                       (lexicon_relations.VARIABLE.MOB, lexicon_relations.VARIABLE.MOB__WEAPON),
                       (lexicon_relations.VARIABLE.ATTACKER, lexicon_relations.VARIABLE.ATTACKER__WEAPON),
                       (lexicon_relations.VARIABLE.DEFENDER, lexicon_relations.VARIABLE.DEFENDER__WEAPON),
                       (lexicon_relations.VARIABLE.COMPANION, lexicon_relations.VARIABLE.COMPANION__WEAPON),
                       (lexicon_relations.VARIABLE.COMPANION_OWNER, lexicon_relations.VARIABLE.COMPANION_OWNER__WEAPON)]

        for key in lexicon_keys.LEXICON_KEY.records:
            if key.group.is_HERO_HISTORY:
                continue

            for variable, weapon in check_pairs:
                self.assertEqual(variable in key.variables, weapon in key.variables)
