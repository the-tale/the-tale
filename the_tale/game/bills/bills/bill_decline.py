# coding: utf-8

from django.forms import ValidationError

from dext.forms import fields

from common.utils.decorators import lazy_property


from game.bills.models import BILL_TYPE
from game.bills.forms import BaseUserForm, BaseModeratorForm
from game.bills.bills.base_bill import BaseBill

from game.map.places.storage import resource_exchange_storage


class UserForm(BaseUserForm):

    declined_bill = fields.TypedChoiceField(label=u'Отменяемый закон', coerce=int)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        bills = [exchange.bill for exchange in resource_exchange_storage.all() if exchange.bill]
        self.fields['declined_bill'].choices = [(bill.id, bill.caption) for bill in bills]

    def clean(self):
        cleaned_data = super(UserForm, self).clean()

        if 'declined_bill' not in cleaned_data or not resource_exchange_storage.get_exchange_for_bill_id(cleaned_data['declined_bill']):
            raise ValidationError(u'Закон уже не действует или не может быть отменён')

        return cleaned_data


class ModeratorForm(BaseModeratorForm):
    pass


class BillDecline(BaseBill):

    type = BILL_TYPE.BILL_DECLINE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/bill_decline_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/bill_decline_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/bill_decline_show.html'

    CAPTION = u'Отмена действующего закона'
    DESCRIPTION = u'Отменяет действующий в текущий момент закон'

    def __init__(self, declined_bill_id=None):
        super(BillDecline, self).__init__()
        self.declined_bill_id = declined_bill_id

    @lazy_property
    def declined_bill(self):
        from game.bills.prototypes import BillPrototype
        return BillPrototype.get_by_id(self.declined_bill_id)

    @property
    def actors(self): return self.declined_bill.data.actors

    @property
    def user_form_initials(self):
        return {'bill': self.declined_bill_id}

    def initialize_with_user_data(self, user_form):
        self.declined_bill_id = int(user_form.c.declined_bill)

    def apply(self, bill=None):
        if not self.declined_bill.is_declined:
            self.declined_bill.decline(bill)

    def serialize(self):
        return {'type': self.type.name.lower(),
                'declined_bill_id': self.declined_bill_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.declined_bill_id = data['declined_bill_id']

        return obj
