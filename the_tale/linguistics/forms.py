# coding: utf-8


from dext.forms import forms, fields

from utg.relations import WORD_TYPE
from utg.words import INVERTED_WORDS_CACHES


from the_tale.linguistics import models


class BaseWordForm(forms.Form):
    pass


def create_word_type_form(word_type):

    class WordForm(BaseWordForm):

        def __init__(self, *args, **kwargs):
            super(WordForm, self).__init__(*args, **kwargs)

            for i, key in enumerate(INVERTED_WORDS_CACHES[word_type]):
                self.fields['field_%d' % i] = fields.CharField(label='', max_length=models.Word.MAX_FORM_LENGTH)

    return WordForm


WORD_FORMS = {word_type: create_word_type_form(word_type)
              for word_type in WORD_TYPE.records}
