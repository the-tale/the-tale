# coding: utf-8

from django import forms as django_forms

from dext.forms import forms, fields

from the_tale.common.utils import bbcode


from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype
from the_tale.collections.storage import collections_storage, kits_storage


class EditCollectionForm(forms.Form):

    caption = fields.CharField(label=u'Название', max_length=CollectionPrototype.CAPTION_MAX_LENGTH, min_length=1)

    description = bbcode.BBField(label=u'Описание', min_length=1, max_length=CollectionPrototype.DESCRIPTION_MAX_LENGTH)


class EditKitForm(forms.Form):

    collection = fields.ChoiceField(label=u'Коллекция')

    caption = fields.CharField(label=u'Название', max_length=KitPrototype.CAPTION_MAX_LENGTH, min_length=1)

    description = bbcode.BBField(label=u'Описание', min_length=1, max_length=KitPrototype.DESCRIPTION_MAX_LENGTH)

    def __init__(self, *args, **kwargs):
        super(EditKitForm, self).__init__(*args, **kwargs)
        self.fields['collection'].choices = collections_storage.get_form_choices()

    def clean_collection(self):
        collection_id = self.cleaned_data['collection']
        collection =  collections_storage[int(collection_id)]

        if collection is None:
            raise django_forms.ValidationError(u'Коллекция не найдена')

        return collection


class EditItemForm(forms.Form):

    kit = fields.ChoiceField(label=u'Набор')

    caption = fields.CharField(label=u'Название', max_length=ItemPrototype.CAPTION_MAX_LENGTH, min_length=1)

    text = bbcode.BBField(label=u'Текст', min_length=1)

    def __init__(self, *args, **kwargs):
        super(EditItemForm, self).__init__(*args, **kwargs)
        self.fields['kit'].choices = kits_storage.get_form_choices()


    def clean_kit(self):
        kit_id = self.cleaned_data['kit']
        kit =  kits_storage[int(kit_id)]

        if kit is None:
            raise django_forms.ValidationError(u'Колекция не найдена')

        return kit
