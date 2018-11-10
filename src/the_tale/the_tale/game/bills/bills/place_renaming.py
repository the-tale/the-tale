
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    place = dext_fields.ChoiceField(label='Город')
    name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN, label='Название', skip_markers=(utg_relations.NOUN_FORM.COUNTABLE,))

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PlaceRenaming(base_place_bill.BasePlaceBill):
    type = relations.BILL_TYPE.PLACE_RENAMING

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Переименование города'
    DESCRIPTION = 'Изменяет название города. При выборе нового названия постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается.'

    def __init__(self, name_forms=None, **kwargs):
        super(PlaceRenaming, self).__init__(**kwargs)
        self.name_forms = name_forms

    @property
    def base_name(self): return self.name_forms.normal_form()

    @property
    def old_name(self): return self.old_name_forms.normal_form()

    @property
    def place_name_changed(self):
        return self.old_name != self.place.name

    def user_form_initials(self):
        data = super(PlaceRenaming, self).user_form_initials()
        data['name'] = self.name_forms
        return data

    def initialize_with_form(self, user_form):
        super(PlaceRenaming, self).initialize_with_form(user_form)
        self.name_forms = user_form.c.name

    def has_meaning(self):
        return self.place.utg_name != self.name_forms

    def apply(self, bill=None):
        if self.has_meaning():
            self.place.set_utg_name(self.name_forms)
            places_logic.save_place(self.place)

    def serialize(self):
        data = super(PlaceRenaming, self).serialize()
        data['name_forms'] = self.name_forms.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PlaceRenaming, cls).deserialize(data)
        obj.name_forms = utg_words.Word.deserialize(data['name_forms'])
        return obj
