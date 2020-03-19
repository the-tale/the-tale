
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    person = utils_fields.ChoiceField(label='Мастер')

    def __init__(self, choosen_person_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['person'].choices = persons_objects.Person.form_choices(choosen_person=persons_storage.persons.get(choosen_person_id))


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PersonChronicle(base_person_bill.BasePersonBill):
    type = relations.BILL_TYPE.PERSON_CHRONICLE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Запись в летописи о Мастере'
    DESCRIPTION = 'Занести в летопись интересное событие, произошедшее с Мастером. Если длина текста меньше 500 символов, к записи необходимо прикрепить фольклорный рассказ, раскрывающий тему. Для одного рассказа можно создать только одну запись.'

    def __init__(self, power_bonus=None, **kwargs):
        super().__init__(**kwargs)
        self.power_bonus = power_bonus

    def has_meaning(self):
        return self.person

    def apply(self, bill=None):
        pass

    def initialize_with_form(self, user_form):
        super(PersonChronicle, self).initialize_with_form(user_form)
        self.power_bonus = relations.POWER_BONUS_CHANGES.NOT_CHANGE

    def serialize(self):
        data = super(PersonChronicle, self).serialize()
        data['power_bonus'] = self.power_bonus.value
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PersonChronicle, cls).deserialize(data)
        obj.power_bonus = relations.POWER_BONUS_CHANGES(data['power_bonus'])
        return obj
