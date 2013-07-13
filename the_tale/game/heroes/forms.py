#coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields

from common.utils.forms import NounFormsWithoutNumberField

from game.heroes.models import Hero
from game.heroes.relations import PREFERENCE_TYPE

from game.game_info import GENDER
from game.balance.enums import RACE

class ChoosePreferencesForm(forms.Form):

    preference_id = fields.CharField(max_length=32, required=False)
    preference_type = fields.TypedChoiceField(choices=PREFERENCE_TYPE._choices(), coerce=PREFERENCE_TYPE._get_from_name)


class EditNameForm(forms.Form):

    race = fields.TypedChoiceField(label=u'раса', choices=RACE._CHOICES, coerce=int)

    gender = fields.TypedChoiceField(label=u'пол', choices=GENDER._CHOICES, coerce=int)

    name_forms = NounFormsWithoutNumberField(label=u'')

    def clean_name_forms(self):
        data = self.cleaned_data['name_forms']

        if len(data[0]) > Hero.MAX_NAME_LENGTH:
            raise ValidationError(u'слишком длинное имя, максимальное число символов: %d' % Hero.MAX_NAME_LENGTH)

        return data
