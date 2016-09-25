# coding: utf-8
from dext.forms import forms, fields

from the_tale.common.utils import bbcode


class NewPostForm(forms.Form):

    text = bbcode.BBField(label=u'Сообщение', min_length=1)


class NewThreadForm(NewPostForm):

    caption = fields.CharField(label=u'Название', max_length=256, min_length=1)


class EditThreadForm(forms.Form):

    caption = fields.CharField(label=u'Название', max_length=256, min_length=1)
    subcategory = fields.ChoiceField(label=u'Раздел', required=False)

    def __init__(self, subcategories, *args, **kwargs):
        super(EditThreadForm, self).__init__(*args, **kwargs)
        self.fields['subcategory'].choices = [ (subcategory.id, subcategory.caption) for subcategory in subcategories]


class EditThreadModeratorForm(EditThreadForm):
    important = fields.BooleanField(label=u'Важная', required=False)
