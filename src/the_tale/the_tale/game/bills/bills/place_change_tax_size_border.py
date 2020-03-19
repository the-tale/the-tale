
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    place = utils_fields.ChoiceField(label='Город')
    tax_size_border = utils_fields.TypedChoiceField(label='поддерживаемый размер ',
                                                    choices=[(size, size) for size in range(1, c.PLACE_MAX_SIZE)],
                                                    coerce=int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()

    def clean(self):
        cleaned_data = super().clean()

        place = places_storage.places.get(int(cleaned_data['place']))
        tax_size_border = cleaned_data.get('tax_size_border')

        if tax_size_border:
            if place.attrs.tax_size_border == tax_size_border:
                raise django_forms.ValidationError('Город уже имеет выбранный поддерживаемый размер.')

        return cleaned_data


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PlaceTaxSizeBorder(base_place_bill.BasePlaceBill):
    type = relations.BILL_TYPE.PLACE_CHANGE_TAX_SIZE_BORDER

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Изменение поддерживаемого размера города'
    DESCRIPTION = f'Изменяет поддерживаемый размер города. {places_relations.ATTRIBUTE.TAX_SIZE_BORDER.description}'

    def __init__(self, tax_size_border=None, **kwargs):
        super().__init__(**kwargs)
        self.tax_size_border = tax_size_border

    def user_form_initials(self):
        data = super().user_form_initials()
        data['tax_size_border'] = self.tax_size_border
        return data

    def initialize_with_form(self, user_form):
        super().initialize_with_form(user_form)
        self.tax_size_border = user_form.c.tax_size_border

    def has_meaning(self):
        return self.place.attrs.tax_size_border != self.tax_size_border

    def apply(self, bill=None):
        if self.has_meaning():
            self.place.attrs.set_tax_size_border(self.tax_size_border)
            places_logic.save_place(self.place)

    def serialize(self):
        data = super().serialize()
        data['tax_size_border'] = self.tax_size_border
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super().deserialize(data)
        obj.tax_size_border = data['tax_size_border']
        return obj
