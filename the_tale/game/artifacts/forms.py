# coding: utf-8

from django.forms import ValidationError

from textgen.words import Noun

from dext.forms import forms, fields

from common.utils.forms import BBField

from game.artifacts.models import ArtifactRecord, ARTIFACT_TYPE, RARITY_TYPE


class ArtifactRecordBaseForm(forms.Form):

    min_level = fields.IntegerField(label=u'минимальный уровень')
    max_level = fields.IntegerField(label=u'максимальный уровень')

    description = BBField(label=u'Описание', required=False)

    type = fields.TypedChoiceField(choices=ARTIFACT_TYPE._CHOICES, coerce=int)

    rarity = fields.TypedChoiceField(choices=RARITY_TYPE._CHOICES, coerce=int)

    def clean(self):
        cleaned_data = super(ArtifactRecordBaseForm, self).clean()
        min_level = cleaned_data.get('min_level')
        max_level = cleaned_data.get('max_level')

        if None not in (min_level, max_level):
            if min_level > max_level:
                raise ValidationError('min level MUST be less then max level')

        return cleaned_data


class ArtifactRecordForm(ArtifactRecordBaseForm):

    name = fields.CharField(label=u'Название артефакта', max_length=ArtifactRecord.MAX_NAME_LENGTH)


class ModerateArtifactRecordForm(ArtifactRecordBaseForm):

    uuid = fields.CharField(label=u'уникальный идентификатор', max_length=ArtifactRecord.MAX_NAME_LENGTH)

    name_forms = fields.JsonField(label=u'Формы названия')

    approved = fields.BooleanField(label=u'одобрен', required=False)

    def clean_name_forms(self):
        data = self.cleaned_data['name_forms']

        noun = Noun.deserialize(data)

        if not noun.is_valid:
            raise ValidationError(u'неверное описание форм существительного')

        return noun
