
import smart_imports

smart_imports.all()


def create_clean_item_method(number):

    def clean_item(self):
        item = self.cleaned_data.get('item_%d' % number)

        if item != '':
            return collections_storage.items[int(item)]

        return None

    return clean_item


class NewAchievementForm(dext_forms.Form):

    approved = dext_fields.BooleanField(label='Одобрена', required=False)

    order = dext_fields.IntegerField()

    group = dext_fields.TypedChoiceField(label='Группа', choices=sorted(relations.ACHIEVEMENT_GROUP.choices(), key=lambda g: g[1]), coerce=relations.ACHIEVEMENT_GROUP.get_from_name)
    type = dext_fields.TypedChoiceField(label='Тип', choices=sorted(relations.ACHIEVEMENT_TYPE.choices(), key=lambda g: g[1]), coerce=relations.ACHIEVEMENT_TYPE.get_from_name)

    caption = dext_fields.CharField(label='Название', max_length=prototypes.AchievementPrototype.CAPTION_MAX_LENGTH, min_length=1)

    description = utils_bbcode.BBField(label='Описание', min_length=1, max_length=prototypes.AchievementPrototype.DESCRIPTION_MAX_LENGTH)

    barrier = dext_fields.IntegerField(label='Барьер')

    points = dext_fields.IntegerField(label='Очки')

    item_1 = dext_fields.ChoiceField(label='награда 1', choices=[], required=False)
    item_2 = dext_fields.ChoiceField(label='награда 2', choices=[], required=False)
    item_3 = dext_fields.ChoiceField(label='награда 3', choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super(NewAchievementForm, self).__init__(*args, **kwargs)
        self.fields['item_1'].choices = [('', '-----')] + collections_storage.items.form_choices()
        self.fields['item_2'].choices = [('', '-----')] + collections_storage.items.form_choices()
        self.fields['item_3'].choices = [('', '-----')] + collections_storage.items.form_choices()

    clean_item_1 = create_clean_item_method(1)
    clean_item_2 = create_clean_item_method(2)
    clean_item_3 = create_clean_item_method(3)


class EditAchievementForm(NewAchievementForm):

    approved = dext_fields.BooleanField(label='Одобрена', required=False)
