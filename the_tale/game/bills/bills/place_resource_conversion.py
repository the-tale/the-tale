# coding: utf-8

from django.forms import ValidationError

import rels
from rels.django import DjangoEnum

from utg import words as utg_words

from dext.forms import fields

from the_tale.game.balance import constants as c

from the_tale.game.bills import relations
from the_tale.game.bills.forms import BaseUserForm, BaseModeratorForm
from the_tale.game.bills.bills.base_bill import BaseBill

from the_tale.game.map.places.storage import places_storage, resource_exchange_storage
from the_tale.game.map.places.prototypes import ResourceExchangePrototype
from the_tale.game.map.places.relations import RESOURCE_EXCHANGE_TYPE


def _conversion_record(name, id_, resource_from, resource_from_delta, resource_to, resource_to_delta):
    return (name,
            id_,
            u'%s за %s' % (resource_from.text, resource_to.text),
            resource_from,
            resource_from_delta,
            resource_to,
            resource_to_delta)


class CONVERSION(DjangoEnum):
    resource_from = rels.Column(unique=False)
    resource_from_delta = rels.Column(unique=False)
    resource_to = rels.Column(unique=False)
    resource_to_delta = rels.Column(unique=False)

    records = ( _conversion_record('TAX_TO_PRODUCTION_SMALL', 0, RESOURCE_EXCHANGE_TYPE.TAX_SMALL, 1, RESOURCE_EXCHANGE_TYPE.PRODUCTION_SMALL, 1),
                _conversion_record('TAX_TO_PRODUCTION_NORMAL', 1, RESOURCE_EXCHANGE_TYPE.TAX_NORMAL, 1, RESOURCE_EXCHANGE_TYPE.PRODUCTION_NORMAL, 1),
                _conversion_record('TAX_TO_PRODUCTION_LARGE', 2, RESOURCE_EXCHANGE_TYPE.TAX_LARGE, 1, RESOURCE_EXCHANGE_TYPE.PRODUCTION_LARGE, 1),

                _conversion_record('TAX_TO_SAFETY_SMALL', 3, RESOURCE_EXCHANGE_TYPE.TAX_SMALL, 1, RESOURCE_EXCHANGE_TYPE.SAFETY_SMALL, 1),
                _conversion_record('TAX_TO_SAFETY_NORMAL', 4, RESOURCE_EXCHANGE_TYPE.TAX_NORMAL, 1, RESOURCE_EXCHANGE_TYPE.SAFETY_NORMAL, 1),
                _conversion_record('TAX_TO_SAFETY_LARGE', 5, RESOURCE_EXCHANGE_TYPE.TAX_LARGE, 1, RESOURCE_EXCHANGE_TYPE.SAFETY_LARGE, 1),

                _conversion_record('TAX_TO_TRANSPORT_SMALL', 6, RESOURCE_EXCHANGE_TYPE.TAX_SMALL, 1, RESOURCE_EXCHANGE_TYPE.TRANSPORT_SMALL, 1),
                _conversion_record('TAX_TO_TRANSPORT_NORMAL', 7, RESOURCE_EXCHANGE_TYPE.TAX_NORMAL, 1, RESOURCE_EXCHANGE_TYPE.TRANSPORT_NORMAL, 1),
                _conversion_record('TAX_TO_TRANSPORT_LARGE', 8, RESOURCE_EXCHANGE_TYPE.TAX_LARGE, 1, RESOURCE_EXCHANGE_TYPE.TRANSPORT_LARGE, 1),
        )


class UserForm(BaseUserForm):

    place = fields.ChoiceField(label=u'Город')
    conversion = fields.TypedChoiceField(label=u'Тип конверсии', choices=CONVERSION.choices(), coerce=CONVERSION.get_from_name)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.get_choices()

    def clean(self):
        cleaned_data = super(UserForm, self).clean()

        place = places_storage.get(int(cleaned_data['place']))

        if (c.PLACE_MAX_BILLS_NUMBER <= len(resource_exchange_storage.get_exchanges_for_place(place)) ):
            raise ValidationError(u'Один город может поддерживать не более чем %(max_exchanges)d активных закона' %  {'max_exchanges': c.PLACE_MAX_BILLS_NUMBER})

        return cleaned_data


class ModeratorForm(BaseModeratorForm):
    pass


class PlaceResourceConversion(BaseBill):

    type = relations.BILL_TYPE.PLACE_RESOURCE_CONVERSION

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    USER_FORM_TEMPLATE = 'bills/bills/place_resource_conversion_user_form.html'
    MODERATOR_FORM_TEMPLATE = 'bills/bills/place_resource_conversion_moderator_form.html'
    SHOW_TEMPLATE = 'bills/bills/place_resource_conversion_show.html'

    CAPTION = u'Изменение параметров города'
    DESCRIPTION = u'Устанавливает изменение параметров города, обычно, бонус к одним за счёт штрафа к другим. Один город может иметь не более %(max_exchanges)d активных договоров.' %  {'max_exchanges': c.PLACE_MAX_BILLS_NUMBER}

    def __init__(self, place_id=None, conversion=None, old_place_name_forms=None):
        super(PlaceResourceConversion, self).__init__()
        self.place_id = place_id
        self.conversion = conversion
        self.old_place_name_forms = old_place_name_forms

        if self.old_place_name_forms is None and self.place_id is not None:
            self.old_place_name_forms = self.place.utg_name

    @property
    def place(self): return places_storage[self.place_id]

    @property
    def actors(self): return [self.place]

    @property
    def user_form_initials(self):
        return {'place': self.place_id,
                'conversion': self.conversion}

    @property
    def place_name_changed(self):
        return self.old_place_name != self.place.name

    @property
    def old_place_name(self): return self.old_place_name_forms.normal_form()

    def initialize_with_user_data(self, user_form):
        self.place_id = int(user_form.c.place)
        self.conversion = user_form.c.conversion
        self.old_place_name_forms = self.place.utg_name

    def apply(self, bill=None):
        ResourceExchangePrototype.create(place_1=self.place,
                                         place_2=None,
                                         resource_1=self.conversion.resource_from,
                                         resource_2=self.conversion.resource_to,
                                         bill=bill)

    def decline(self, bill):
        exchange = resource_exchange_storage.get_exchange_for_bill_id(bill.id)
        if exchange:
            exchange.remove()

    def end(self, bill):
        exchange = resource_exchange_storage.get_exchange_for_bill_id(bill.id)
        if exchange:
            exchange.remove()

    def serialize(self):
        return {'type': self.type.name.lower(),
                'place_id': self.place_id,
                'old_place_name_forms': self.old_place_name_forms.serialize(),
                'conversion': self.conversion.value}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.place_id = data['place_id']
        obj.old_place_name_forms = utg_words.Word.deserialize(data['old_place_name_forms'])
        obj.conversion = CONVERSION.index_value[data['conversion']]
        return obj
