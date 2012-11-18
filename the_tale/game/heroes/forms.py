#coding: utf-8

from dext.forms import forms, fields

from common.utils.forms import NounFormsWithoutNumberField

from game.heroes.models import PREFERENCE_TYPE

from game.game_info import RACE, GENDER

class ChoosePreferencesForm(forms.Form):

    preference_id = fields.CharField(max_length=32, required=False)
    preference_type = fields.ChoiceField(choices=PREFERENCE_TYPE.CHOICES)


class EditNameForm(forms.Form):

    race = fields.TypedChoiceField(label=u'раса', choices=RACE.CHOICES, coerce=int)

    gender = fields.TypedChoiceField(label=u'пол', choices=GENDER.CHOICES, coerce=int)

    name_forms = NounFormsWithoutNumberField(label=u'')
