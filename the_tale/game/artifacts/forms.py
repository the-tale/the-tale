# coding: utf-8

from django.forms import ValidationError

from textgen.words import Noun

from dext.forms import forms, fields

from common.utils.forms import BBField

from game.mobs.storage import mobs_storage

from game.artifacts.models import ArtifactRecord, ARTIFACT_TYPE, RARITY_TYPE


class ArtifactRecordBaseForm(forms.Form):

    level = fields.IntegerField(label=u'минимальный уровень')

    description = BBField(label=u'Описание', required=False)

    type = fields.TypedChoiceField(label=u'тип', choices=ARTIFACT_TYPE._CHOICES, coerce=int)

    rarity = fields.TypedChoiceField(label=u'Редкость', choices=RARITY_TYPE._CHOICES, coerce=int)

    mob = fields.ChoiceField(label=u'Монстр', required=False)

    def __init__(self, *args, **kwargs):
        super(ArtifactRecordBaseForm, self).__init__(*args, **kwargs)
        self.fields['mob'].choices = [('', u'-------')] + [(mob.id, mob.name) for mob in sorted(mobs_storage.all(), key=lambda mob: mob.name)]

    def clean_mob(self):
        mob = self.cleaned_data.get('mob')

        if mob:
            return mobs_storage[int(mob)]

        return None


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
