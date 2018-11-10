
import smart_imports

smart_imports.all()


class NewPostForm(dext_forms.Form):

    text = utils_bbcode.BBField(label='Сообщение', min_length=1)


class NewThreadForm(NewPostForm):

    caption = dext_fields.CharField(label='Название', max_length=256, min_length=1)


class EditThreadForm(dext_forms.Form):

    caption = dext_fields.CharField(label='Название', max_length=256, min_length=1)
    subcategory = dext_fields.ChoiceField(label='Раздел', required=False)

    def __init__(self, subcategories, *args, **kwargs):
        super(EditThreadForm, self).__init__(*args, **kwargs)
        self.fields['subcategory'].choices = sorted([(subcategory.id, subcategory.caption) for subcategory in subcategories], key=lambda x: x[1])


class EditThreadModeratorForm(EditThreadForm):
    important = dext_fields.BooleanField(label='Важная', required=False)
