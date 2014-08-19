# coding: utf-8


from dext.forms import forms, fields

from utg.relations import WORD_TYPE
from utg.words import INVERTED_WORDS_CACHES


from the_tale.linguistics import models


class BaseWordForm(forms.Form):
    pass


def create_word_type_form(word_type):

    class WordForm(BaseWordForm):
        pass

    for i, key in enumerate(INVERTED_WORDS_CACHES):
        name_form_field = fields.CharField(max_length=models.Word.MAX_FORM_LENGTH)
        setattr(WordForm, 'field_%d' % i, name_form_field)

    return WordForm


WORD_FORMS = {word_type: create_word_type_form(word_type)
              for word_type in WORD_TYPE.records}
