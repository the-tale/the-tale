#coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields

from utg import relations as utg_relations
from utg import words as utg_words

from the_tale.game.heroes.models import Hero
from the_tale.game.heroes.relations import PREFERENCE_TYPE

from the_tale.game.relations import GENDER, RACE

from the_tale.linguistics import forms as linguisitcs_forms


class ChoosePreferencesForm(forms.Form):

    preference_id = fields.CharField(max_length=32, required=False)
    preference_type = fields.TypedChoiceField(choices=PREFERENCE_TYPE.choices(), coerce=PREFERENCE_TYPE.get_from_name)


class EditNameForm(forms.Form):

    race = fields.TypedChoiceField(label=u'раса', choices=RACE.choices(), coerce=RACE.get_from_name)

    gender = fields.TypedChoiceField(label=u'пол', choices=GENDER.choices(), coerce=GENDER.get_from_name)

    def __init__(self, *args, **kwargs):
        super(EditNameForm, self).__init__(*args, **kwargs)
        self.fields.update(linguisitcs_forms.get_word_fields_dict(utg_relations.WORD_TYPE.NOUN))


    def get_name(self):
        forms = linguisitcs_forms.get_word_forms(form=self, word_type=utg_relations.WORD_TYPE.NOUN)
        return utg_words.Word(type=utg_relations.WORD_TYPE.NOUN,
                              forms=forms,
                              properties=utg_words.Properties(self.c.gender.utg_id, utg_relations.ANIMALITY.ANIMATE))


    def clean(self):
        cleaned_data = super(EditNameForm, self).clean()

        for field_id in linguisitcs_forms.get_word_fields_dict(utg_relations.WORD_TYPE.NOUN):
            if field_id not in cleaned_data:
                raise ValidationError(u'Указаны не все формы слова')

            name_form = cleaned_data[field_id]

            if len(name_form) > Hero.MAX_NAME_LENGTH:
                raise ValidationError(u'слишком длинное имя, максимальное число символов: %d' % Hero.MAX_NAME_LENGTH)
            if len(name_form) < 3:
                raise ValidationError(u'слишком короткое имя, минимальное число символов: %d' % 3)

        return cleaned_data


    @classmethod
    def get_initials(cls, hero):
        initials = linguisitcs_forms.get_word_fields_initials(hero.utg_name)
        initials['gender'] = hero.gender
        initials['race'] = hero.race

        return initials
