# coding: utf-8
from django import forms as django_forms

from dext.forms import forms, fields

from the_tale.game.text_generation import get_phrases_types

from the_tale.game.phrase_candidates.models import PhraseCandidate, PHRASE_CANDIDATE_STATE


class PhraseCandidateNewForm(forms.Form):

    phrase_type = fields.HiddenCharField(label=u'')
    phrase_subtype = fields.HiddenCharField(label=u'')
    text = fields.TextField(label=u'Текст', max_length=PhraseCandidate.MAX_TEXT_LENGTH, widget=django_forms.Textarea(attrs={'rows':'3'}))


UNKNOWN_TYPE_ID = '#unknown'
SUBTYPE_CHOICES = [(UNKNOWN_TYPE_ID, u'неизвестный тип')]

phrases_types = get_phrases_types()

for module in phrases_types['modules'].values():
    module_name = module['name']
    for subtype_id, subtype in module['types'].items():
        subtype_name = subtype['name']
        SUBTYPE_CHOICES.append((subtype_id, u'%s::%s' % (module_name, subtype_name)))

SUBTYPE_CHOICES = sorted(SUBTYPE_CHOICES, key=lambda x: x[0])

SUBTYPE_CHOICES_IDS = [choice[0] for choice in SUBTYPE_CHOICES]


class PhraseCandidateEditForm(forms.Form):

    state = fields.ChoiceField(label=u'Состояние', choices=( (PHRASE_CANDIDATE_STATE.IN_QUEUE, PHRASE_CANDIDATE_STATE._ID_TO_TEXT[PHRASE_CANDIDATE_STATE.IN_QUEUE]),
                                                             (PHRASE_CANDIDATE_STATE.REMOVED, PHRASE_CANDIDATE_STATE._ID_TO_TEXT[PHRASE_CANDIDATE_STATE.REMOVED]),
                                                             (PHRASE_CANDIDATE_STATE.APPROVED, PHRASE_CANDIDATE_STATE._ID_TO_TEXT[PHRASE_CANDIDATE_STATE.APPROVED]),))
    text = fields.TextField(label=u'Текст', max_length=PhraseCandidate.MAX_TEXT_LENGTH, widget=django_forms.Textarea(attrs={'rows':'3'}))

    subtype = fields.ChoiceField(label=u'тип', choices=SUBTYPE_CHOICES)
