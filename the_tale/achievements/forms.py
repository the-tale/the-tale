# coding: utf-8

from django import forms as django_forms

from dext.forms import forms, fields

from common.utils import bbcode


from achievements.prototypes import SectionPrototype, KitPrototype, RewardPrototype


class EditSectionForm(forms.Form):

    caption = fields.CharField(label=u'Название', max_length=SectionPrototype.CAPTION_MAX_LENGTH, min_length=1)

    description = bbcode.BBField(label=u'Описание', min_length=1, max_length=SectionPrototype.DESCRIPTION_MAX_LENGTH)


class EditKitForm(forms.Form):

    section = fields.ChoiceField(label=u'Раздел')

    caption = fields.CharField(label=u'Название', max_length=KitPrototype.CAPTION_MAX_LENGTH, min_length=1)

    description = bbcode.BBField(label=u'Описание', min_length=1, max_length=KitPrototype.DESCRIPTION_MAX_LENGTH)

    def __init__(self, *args, **kwargs):
        super(EditKitForm, self).__init__(*args, **kwargs)
        self.fields['section'].choices = [(s.id, s.caption) for s in SectionPrototype._db_all()]

    def clean_section(self):
        section_id = self.cleaned_data['section']
        section =  SectionPrototype.get_by_id(section_id)

        if section is None:
            raise django_forms.ValidationError(u'Раздел не найден')

        return section


class EditRewardForm(forms.Form):

    kit = fields.ChoiceField(label=u'Набор')

    caption = fields.CharField(label=u'Название', max_length=RewardPrototype.CAPTION_MAX_LENGTH, min_length=1)

    text = bbcode.BBField(label=u'Текст', min_length=1)

    def __init__(self, *args, **kwargs):
        super(EditRewardForm, self).__init__(*args, **kwargs)
        self.fields['kit'].choices = [(k.id, k.caption) for k in KitPrototype._db_all()]


    def clean_kit(self):
        kit_id = self.cleaned_data['kit']
        kit =  KitPrototype.get_by_id(kit_id)

        if kit is None:
            raise django_forms.ValidationError(u'Раздел не найден')

        return kit
