# coding: utf-8

from dext.forms import forms, fields

from the_tale.common.utils.forms import SimpleWordField
from the_tale.common.utils import bbcode

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.artifacts.models import ArtifactRecord, RARITY_TYPE
from the_tale.game.artifacts.relations import ARTIFACT_TYPE


class ArtifactRecordBaseForm(forms.Form):

    level = fields.IntegerField(label=u'минимальный уровень')

    description = bbcode.BBField(label=u'Описание', required=False)

    type = fields.TypedChoiceField(label=u'тип', choices=ARTIFACT_TYPE._choices(), coerce=ARTIFACT_TYPE._get_from_name)

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

    name_forms = SimpleWordField(label=u'Формы названия')

    approved = fields.BooleanField(label=u'одобрен', required=False)
