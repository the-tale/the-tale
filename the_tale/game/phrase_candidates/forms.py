# coding: utf-8
from django import forms as django_forms

from dext.forms import forms, fields

from game.phrase_candidates.models import PhraseCandidate, PHRASE_CANDIDATE_STATE


class PhraseCandidateNewForm(forms.Form):

    phrase_type = fields.HiddenCharField(label=u'')
    phrase_subtype = fields.HiddenCharField(label=u'')
    text = fields.TextField(label=u'Текст', max_length=PhraseCandidate.MAX_TEXT_LENGTH, widget=django_forms.Textarea(attrs={'rows':'3'}))


class PhraseCandidateEditForm(forms.Form):

    state = fields.ChoiceField(label=u'Состояние', choices=( (PHRASE_CANDIDATE_STATE.IN_QUEUE, PHRASE_CANDIDATE_STATE.ID_2_TEXT[PHRASE_CANDIDATE_STATE.IN_QUEUE]),
                                                             (PHRASE_CANDIDATE_STATE.REMOVED, PHRASE_CANDIDATE_STATE.ID_2_TEXT[PHRASE_CANDIDATE_STATE.REMOVED]),
                                                             (PHRASE_CANDIDATE_STATE.APPROVED, PHRASE_CANDIDATE_STATE.ID_2_TEXT[PHRASE_CANDIDATE_STATE.APPROVED]),))
    text = fields.TextField(label=u'Текст', max_length=PhraseCandidate.MAX_TEXT_LENGTH, widget=django_forms.Textarea(attrs={'rows':'3'}))
