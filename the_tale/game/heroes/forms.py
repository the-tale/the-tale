#coding: utf-8
import re

from django.forms import ValidationError

from dext.forms import forms, fields

from utg import relations as utg_relations

from the_tale.linguistics.forms import WordField

from the_tale.game.relations import GENDER, RACE

from the_tale.game.heroes import models
from the_tale.game.heroes import relations
from the_tale.game.heroes import conf


NAME_REGEX = re.compile(conf.heroes_settings.NAME_REGEX)


class ChoosePreferencesForm(forms.Form):

    preference_id = fields.CharField(max_length=32, required=False)
    preference_type = fields.TypedChoiceField(choices=relations.PREFERENCE_TYPE.choices(), coerce=relations.PREFERENCE_TYPE.get_from_name)


class EditNameForm(forms.Form):

    race = fields.TypedChoiceField(label=u'раса', choices=RACE.choices(), coerce=RACE.get_from_name)
    gender = fields.TypedChoiceField(label=u'пол', choices=GENDER.choices(), coerce=GENDER.get_from_name)
    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'имя', skip_markers=(utg_relations.NOUN_FORM.COUNTABLE,), show_properties=False)

    def clean(self):
        cleaned_data = super(EditNameForm, self).clean()

        name = cleaned_data.get('name')

        if name is not None:
            for name_form in cleaned_data['name'].forms:
                if len(name_form) > models.Hero.MAX_NAME_LENGTH:
                    raise ValidationError(u'Слишком длинное имя, максимальное число символов: %d' % modelsHero.MAX_NAME_LENGTH)

                if len(name_form) < conf.heroes_settings.NAME_MIN_LENGHT:
                    raise ValidationError(u'Слишком короткое имя, минимальное число символов: %d' % conf.heroes_settings.NAME_MIN_LENGHT)

                if NAME_REGEX.match(name_form) is None:
                    print name_form
                    raise ValidationError(u'Имя героя может содержать только следующие символы: %s' % conf.heroes_settings.NAME_SYMBOLS_DESCRITION)

            name.properties = name.properties.clone(cleaned_data['gender'].utg_id)

        return cleaned_data


    @classmethod
    def get_initials(cls, hero):
        return {'gender': hero.gender,
                'race': hero.race,
                'name':  hero.utg_name }
