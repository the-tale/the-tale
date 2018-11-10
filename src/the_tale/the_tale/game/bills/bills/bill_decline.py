
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    declined_bill = dext_fields.TypedChoiceField(label='Отменяемая запись', coerce=int)

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        bills = [exchange.bill for exchange in places_storage.resource_exchanges.all() if exchange.bill]
        self.fields['declined_bill'].choices = [(bill.id, bill.caption) for bill in bills]

    def clean(self):
        cleaned_data = super(BaseForm, self).clean()

        if 'declined_bill' not in cleaned_data or not places_storage.resource_exchanges.get_exchange_for_bill_id(cleaned_data['declined_bill']):
            raise django_forms.ValidationError('Запись уже не действует или не может быть отменена')

        return cleaned_data


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class BillDecline(base_bill.BaseBill):
    type = relations.BILL_TYPE.BILL_DECLINE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Отмена действующей записи Книги Судеб'
    DESCRIPTION = 'Отменяет действующую в текущий момент запись Книги Судеб.'

    def __init__(self, declined_bill_id=None):
        super(BillDecline, self).__init__()
        self.declined_bill_id = declined_bill_id

    @utils_decorators.lazy_property
    def declined_bill(self):
        return prototypes.BillPrototype.get_by_id(self.declined_bill_id)

    @property
    def actors(self): return self.declined_bill.data.actors

    def user_form_initials(self):
        return {'declined_bill': self.declined_bill_id}

    def initialize_with_form(self, user_form):
        self.declined_bill_id = int(user_form.c.declined_bill)

    def has_meaning(self):
        self.declined_bill.reload()  # enshure that we loaded latest bill version
        return not self.declined_bill.is_declined

    def apply(self, bill=None):
        if self.has_meaning():
            self.declined_bill.decline(bill)

    def serialize(self):
        return {'type': self.type.name.lower(),
                'declined_bill_id': self.declined_bill_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.declined_bill_id = data['declined_bill_id']

        return obj
