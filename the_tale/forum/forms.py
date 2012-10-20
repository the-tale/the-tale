# coding: utf-8
from dext.forms import forms, fields

from common.utils.forms import BBField


class NewPostForm(forms.Form):

    text = BBField(label=u'Сообщение')


class NewThreadForm(NewPostForm):

    caption = fields.CharField(label=u'Название', max_length=256)


class EditThreadForm(forms.Form):

    caption = fields.CharField(label=u'Название', max_length=256)
    subcategory = fields.ChoiceField(label=u'Раздел', required=False)

    def __init__(self, subcategories, *args, **kwargs):
        super(EditThreadForm, self).__init__(*args, **kwargs)
        self.fields['subcategory'].choices = [ (subcategory.id, subcategory.caption) for subcategory in subcategories]
