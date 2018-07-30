
import smart_imports

smart_imports.all()


class EditCollectionForm(dext_forms.Form):

    caption = dext_fields.CharField(label='Название', max_length=prototypes.CollectionPrototype.CAPTION_MAX_LENGTH, min_length=1)

    description = utils_bbcode.BBField(label='Описание', min_length=1, max_length=prototypes.CollectionPrototype.DESCRIPTION_MAX_LENGTH)


class EditKitForm(dext_forms.Form):

    collection = dext_fields.ChoiceField(label='Коллекция')

    caption = dext_fields.CharField(label='Название', max_length=prototypes.KitPrototype.CAPTION_MAX_LENGTH, min_length=1)

    description = utils_bbcode.BBField(label='Описание', min_length=1, max_length=prototypes.KitPrototype.DESCRIPTION_MAX_LENGTH)

    def __init__(self, *args, **kwargs):
        super(EditKitForm, self).__init__(*args, **kwargs)
        self.fields['collection'].choices = storage.collections.get_form_choices()

    def clean_collection(self):
        collection_id = self.cleaned_data['collection']
        collection = storage.collections[int(collection_id)]

        if collection is None:
            raise django_forms.ValidationError('Коллекция не найдена')

        return collection


class EditItemForm(dext_forms.Form):

    kit = dext_fields.ChoiceField(label='Набор')

    caption = dext_fields.CharField(label='Название', max_length=prototypes.ItemPrototype.CAPTION_MAX_LENGTH, min_length=1)

    text = utils_bbcode.BBField(label='Текст', min_length=1)

    def __init__(self, *args, **kwargs):
        super(EditItemForm, self).__init__(*args, **kwargs)
        self.fields['kit'].choices = storage.kits.get_form_choices()

    def clean_kit(self):
        kit_id = self.cleaned_data['kit']
        kit = storage.kits[int(kit_id)]

        if kit is None:
            raise django_forms.ValidationError('Колекция не найдена')

        return kit
