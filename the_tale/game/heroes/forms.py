#coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields

from the_tale.common.utils.forms import NounFormsWithoutNumberField

from the_tale.game.heroes.models import Hero
from the_tale.game.heroes.relations import PREFERENCE_TYPE

from the_tale.game.relations import GENDER, RACE


class ChoosePreferencesForm(forms.Form):

    preference_id = fields.CharField(max_length=32, required=False)
    preference_type = fields.TypedChoiceField(choices=PREFERENCE_TYPE.choices(), coerce=PREFERENCE_TYPE.get_from_name)


class EditNameForm(forms.Form):

    race = fields.TypedChoiceField(label=u'раса', choices=RACE.choices(), coerce=RACE.get_from_name)

    gender = fields.TypedChoiceField(label=u'пол', choices=GENDER.choices(), coerce=GENDER.get_from_name)

    name_forms = NounFormsWithoutNumberField(label=u'')

    def clean_name_forms(self):
        data = self.cleaned_data['name_forms']

        if len(data[0]) > Hero.MAX_NAME_LENGTH:
            raise ValidationError(u'слишком длинное имя, максимальное число символов: %d' % Hero.MAX_NAME_LENGTH)

        return data
