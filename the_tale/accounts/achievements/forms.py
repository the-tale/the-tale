# coding: utf-8

# from django import forms as django_forms

from dext.forms import forms, fields

from the_tale.common.utils import bbcode


from the_tale.accounts.achievements.prototypes import AchievementPrototype
from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE


class EditAchievementForm(forms.Form):

    approved = fields.BooleanField(label=u'Одобрена', required=False)

    order = fields.IntegerField()

    group = fields.TypedChoiceField(label=u'Группа', choices=sorted(ACHIEVEMENT_GROUP._choices(), key=lambda g: g[1]), coerce=ACHIEVEMENT_GROUP._get_from_name)
    type = fields.TypedChoiceField(label=u'Тип', choices=sorted(ACHIEVEMENT_TYPE._choices(), key=lambda g: g[1]), coerce=ACHIEVEMENT_TYPE._get_from_name)

    caption = fields.CharField(label=u'Название', max_length=AchievementPrototype.CAPTION_MAX_LENGTH, min_length=1)

    description = bbcode.BBField(label=u'Описание', min_length=1, max_length=AchievementPrototype.DESCRIPTION_MAX_LENGTH)

    barrier = fields.IntegerField(label=u'Барьер')

    points = fields.IntegerField(label=u'Очки')
