# coding: utf-8

from dext.forms import forms, fields

from common.utils import bbcode


from achievements.models import Section, Kit


class EditSectionForm(forms.Form):

    caption = fields.CharField(label=u'Название', max_length=Section.CAPTION_MAX_LENGTH, min_length=1)

    description = bbcode.BBField(label=u'Описание', min_length=1, max_length=Section.DESCRIPTION_MAX_LENGTH)


class EditKitForm(forms.Form):

    caption = fields.CharField(label=u'Название', max_length=Kit.CAPTION_MAX_LENGTH, min_length=1)

    description = bbcode.BBField(label=u'Описание', min_length=1, max_length=Kit.DESCRIPTION_MAX_LENGTH)
