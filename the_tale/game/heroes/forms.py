#coding: utf-8

from dext.forms import forms, fields

from game.heroes.models import PREFERENCE_TYPE_CHOICES

class ChoosePreferencesForm(forms.Form):

    preference_id = fields.CharField(max_length=32)
    preference_type = fields.ChoiceField(choices=PREFERENCE_TYPE_CHOICES)
