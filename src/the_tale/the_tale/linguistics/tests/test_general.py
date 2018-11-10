
import smart_imports

smart_imports.all()


class GeneralTests(utils_testcase.TestCase):

    def setUp(self):
        super(GeneralTests, self).setUp()

    def get_uniqueness_data(self, type=None, state=None, normal_form=None):
        if state is None:
            state = relations.WORD_STATE.ON_REVIEW
        if normal_form is None:
            normal_form = 'normal-form'

        return {'type': type,
                'state': state,
                'normal_form': normal_form,
                'forms': '',
                'used_in_status': relations.WORD_USED_IN_STATUS.NOT_USED}

    def test_uniqueness(self):
        type_1 = utg_relations.WORD_TYPE.records[0]
        type_2 = utg_relations.WORD_TYPE.records[1]

        models.Word.objects.create(**self.get_uniqueness_data(type=type_1))

        with django_transaction.atomic():
            self.assertRaises(django_db.IntegrityError, models.Word.objects.create, **self.get_uniqueness_data())

        models.Word.objects.create(**self.get_uniqueness_data(type=type_2))
        models.Word.objects.create(**self.get_uniqueness_data(type=type_1, normal_form='normal_form-2'))
        models.Word.objects.create(**self.get_uniqueness_data(type=type_1, state=relations.WORD_STATE.IN_GAME))

        with django_transaction.atomic():
            self.assertRaises(django_db.IntegrityError, models.Word.objects.create, **self.get_uniqueness_data(type=type_2))

        with django_transaction.atomic():
            self.assertRaises(django_db.IntegrityError, models.Word.objects.create, **self.get_uniqueness_data(type=type_1, normal_form='normal_form-2'))

        with django_transaction.atomic():
            self.assertRaises(django_db.IntegrityError, models.Word.objects.create, **self.get_uniqueness_data(type=type_1, state=relations.WORD_STATE.IN_GAME))

    def test_all_lexicon_verificators_in_dictionary(self):
        for verificator in lexicon_relations.VARIABLE_VERIFICATOR.records:
            if verificator.utg_type is None:
                continue
            for substitutions in verificator.substitutions:
                for word, properties in substitutions:
                    self.assertTrue(isinstance(word, int) or lexicon_dictionary.DICTIONARY.has_word(word))

    def test_all_lexicon_keys_have_suffient_number_of_verificator_substitutions(self):

        for key in lexicon_keys.LEXICON_KEY.records:
            verificators = collections.Counter(v.type.verificator for v in key.variables)
            for verificator, number in verificators.items():
                self.assertTrue(len(verificator.substitutions) >= number)

    def test_correct_autofill_of_noun_countable_form(self):
        word = utg_words.Word.create_test_word(utg_relations.WORD_TYPE.NOUN)

        for key, index in utg_data.WORDS_CACHES[word.type].items():
            if utg_relations.NOUN_FORM.COUNTABLE in key:
                word.forms[index] = ''

        word.autofill_missed_forms()

        for key, index in utg_data.WORDS_CACHES[word.type].items():
            if utg_relations.NOUN_FORM.COUNTABLE in key:
                modified_key = list(property if property != utg_relations.NOUN_FORM.COUNTABLE else utg_relations.NOUN_FORM.NORMAL for property in key)
                self.assertEqual(word.form(utg_words.Properties(*key)),
                                 word.form(utg_words.Properties(*modified_key)))

    def test_single_relation_per_restriction_group(self):

        mapping = {}

        for group in restrictions.GROUP.records:
            if group.static_relation is None:
                continue

            self.assertNotIn(group.static_relation, mapping)

            mapping[group.static_relation] = group
