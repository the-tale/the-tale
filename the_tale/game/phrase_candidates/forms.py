# coding: utf-8
from django import forms as django_forms

from dext.forms import forms, fields

from game.phrase_candidates.models import PhraseCandidate


class PhraseCandidateForm(forms.Form):

    phrase_type = fields.HiddenCharField(label=u'')
    phrase_subtype = fields.HiddenCharField(label=u'')
    text = fields.TextField(label=u'Текст', max_length=PhraseCandidate.MAX_TEXT_LENGTH, widget=django_forms.Textarea(attrs={'rows':'3'}))
