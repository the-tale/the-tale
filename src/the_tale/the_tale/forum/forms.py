
import smart_imports

smart_imports.all()


class NewPostForm(utils_forms.Form):

    text = bbcode_fields.BBField(label='Сообщение', min_length=1)


class NewThreadForm(NewPostForm):

    caption = utils_fields.CharField(label='Название', max_length=256, min_length=1)


class EditThreadForm(utils_forms.Form):

    caption = utils_fields.CharField(label='Название', max_length=256, min_length=1)
    subcategory = utils_fields.ChoiceField(label='Раздел', required=False)

    def __init__(self, subcategories, *args, **kwargs):
        super(EditThreadForm, self).__init__(*args, **kwargs)
        self.fields['subcategory'].choices = sorted([(subcategory.id, subcategory.caption) for subcategory in subcategories], key=lambda x: x[1])


class EditThreadModeratorForm(EditThreadForm):
    important = utils_fields.BooleanField(label='Важная', required=False)
