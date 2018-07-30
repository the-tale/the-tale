
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    place = dext_fields.ChoiceField(label='Город')
    new_description = utils_bbcode.BBField(label='Новое описание', max_length=places_conf.settings.MAX_DESCRIPTION_LENGTH)

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PlaceDescripton(base_place_bill.BasePlaceBill):
    type = relations.BILL_TYPE.PLACE_DESCRIPTION

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Изменение описания города'
    DESCRIPTION = 'Изменяет описание города. При создании нового описания постарайтесь учесть, какой расе принадлежит город, кто является его жителями и в какую сторону он развивается. Также не забывайте, что описание должно соответствовать названию города. Описание должно быть небольшим по размеру.'

    def __init__(self, description=None, old_description=None, **kwargs):
        super(PlaceDescripton, self).__init__(**kwargs)
        self.description = description
        self.old_description = old_description

        if self.old_name_forms is None and self.place_id is not None:
            self.old_name_forms = self.place.utg_name

    @property
    def description_html(self): return utils_bbcode.render(self.description)

    @property
    def old_description_html(self): return utils_bbcode.render(self.old_description)

    def user_form_initials(self):
        data = super(PlaceDescripton, self).user_form_initials()
        data['new_description'] = self.description
        return data

    def initialize_with_form(self, user_form):
        super(PlaceDescripton, self).initialize_with_form(user_form)
        self.description = user_form.c.new_description
        self.old_description = self.place.description

    def has_meaning(self):
        return self.place.description != self.description

    def apply(self, bill=None):
        if self.has_meaning():
            self.place.description = self.description
            places_logic.save_place(self.place)

    def serialize(self):
        data = super(PlaceDescripton, self).serialize()
        data['description'] = self.description
        data['old_description'] = self.old_description
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PlaceDescripton, cls).deserialize(data)
        obj.description = data['description']
        obj.old_description = data.get('old_description', 'утрачено')
        return obj
