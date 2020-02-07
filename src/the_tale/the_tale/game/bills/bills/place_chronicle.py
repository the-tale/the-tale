
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    place = utils_fields.ChoiceField(label='Город', )

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PlaceChronicle(base_place_bill.BasePlaceBill):
    type = relations.BILL_TYPE.PLACE_CHRONICLE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Запись в летописи о городе'
    DESCRIPTION = 'Занести в летопись интересное событие, произошедшее в городе. Если длина текста меньше 500 символов, к записи необходимо прикрепить фольклорный рассказ, раскрывающий тему. Для одного рассказа можно создать только одну запись.'

    def __init__(self, power_bonus=None, **kwargs):
        super(PlaceChronicle, self).__init__(**kwargs)
        self.power_bonus = power_bonus

    def initialize_with_form(self, user_form):
        super(PlaceChronicle, self).initialize_with_form(user_form)
        self.power_bonus = relations.POWER_BONUS_CHANGES.NOT_CHANGE

    def has_meaning(self):
        return True

    def apply(self, bill=None):
        pass

    def serialize(self):
        data = super(PlaceChronicle, self).serialize()
        data['power_bonus'] = self.power_bonus.value
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PlaceChronicle, cls).deserialize(data)
        obj.power_bonus = relations.POWER_BONUS_CHANGES(data['power_bonus'])
        return obj
