
import smart_imports

smart_imports.all()


def _conversion_record(name, id_, resource_from, resource_from_delta, resource_to, resource_to_delta):
    return (name,
            id_,
            '%s за %s' % (resource_from.text, resource_to.text),
            resource_from,
            resource_from_delta,
            resource_to,
            resource_to_delta)


RESOURCE_EXCHANGE_TYPE = places_relations.RESOURCE_EXCHANGE_TYPE


class CONVERSION(rels_django.DjangoEnum):
    resource_from = rels.Column(unique=False)
    resource_from_delta = rels.Column(unique=False)
    resource_to = rels.Column(unique=False)
    resource_to_delta = rels.Column(unique=False)

    records = (_conversion_record('TAX_TO_PRODUCTION_SMALL', 0, RESOURCE_EXCHANGE_TYPE.TAX_SMALL, 1, RESOURCE_EXCHANGE_TYPE.PRODUCTION_SMALL, 1),
               _conversion_record('TAX_TO_PRODUCTION_NORMAL', 1, RESOURCE_EXCHANGE_TYPE.TAX_NORMAL, 1, RESOURCE_EXCHANGE_TYPE.PRODUCTION_NORMAL, 1),
               _conversion_record('TAX_TO_PRODUCTION_LARGE', 9, RESOURCE_EXCHANGE_TYPE.TAX_LARGE, 1, RESOURCE_EXCHANGE_TYPE.PRODUCTION_LARGE, 1),
               _conversion_record('TAX_TO_PRODUCTION_EXTRA_LARGE', 2, RESOURCE_EXCHANGE_TYPE.TAX_EXTRA_LARGE, 1, RESOURCE_EXCHANGE_TYPE.PRODUCTION_EXTRA_LARGE, 1),

               _conversion_record('TAX_TO_SAFETY_SMALL', 3, RESOURCE_EXCHANGE_TYPE.TAX_SMALL, 1, RESOURCE_EXCHANGE_TYPE.SAFETY_SMALL, 1),
               _conversion_record('TAX_TO_SAFETY_NORMAL', 4, RESOURCE_EXCHANGE_TYPE.TAX_NORMAL, 1, RESOURCE_EXCHANGE_TYPE.SAFETY_NORMAL, 1),
               _conversion_record('TAX_TO_SAFETY_LARGE', 10, RESOURCE_EXCHANGE_TYPE.TAX_LARGE, 1, RESOURCE_EXCHANGE_TYPE.SAFETY_LARGE, 1),
               _conversion_record('TAX_TO_SAFETY_EXTRA_LARGE', 5, RESOURCE_EXCHANGE_TYPE.TAX_EXTRA_LARGE, 1, RESOURCE_EXCHANGE_TYPE.SAFETY_EXTRA_LARGE, 1),

               _conversion_record('TAX_TO_TRANSPORT_SMALL', 6, RESOURCE_EXCHANGE_TYPE.TAX_SMALL, 1, RESOURCE_EXCHANGE_TYPE.TRANSPORT_SMALL, 1),
               _conversion_record('TAX_TO_TRANSPORT_NORMAL', 7, RESOURCE_EXCHANGE_TYPE.TAX_NORMAL, 1, RESOURCE_EXCHANGE_TYPE.TRANSPORT_NORMAL, 1),
               _conversion_record('TAX_TO_TRANSPORT_LARGE', 11, RESOURCE_EXCHANGE_TYPE.TAX_LARGE, 1, RESOURCE_EXCHANGE_TYPE.TRANSPORT_LARGE, 1),
               _conversion_record('TAX_TO_TRANSPORT_EXTRA_LARGE', 8, RESOURCE_EXCHANGE_TYPE.TAX_EXTRA_LARGE, 1, RESOURCE_EXCHANGE_TYPE.TRANSPORT_EXTRA_LARGE, 1),
               )


class BaseForm(forms.BaseUserForm):
    place = dext_fields.ChoiceField(label='Город')
    conversion = dext_fields.TypedChoiceField(label='Тип конверсии', choices=CONVERSION.choices(), coerce=CONVERSION.get_from_name)

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()

    def clean(self):
        cleaned_data = super(BaseForm, self).clean()

        place = places_storage.places.get(int(cleaned_data['place']))

        if (c.PLACE_MAX_BILLS_NUMBER <= len(places_storage.resource_exchanges.get_exchanges_for_place(place))):
            raise django_forms.ValidationError('Один город может поддерживать не более чем %(max_exchanges)d активных записей в Книге Судеб' % {'max_exchanges': c.PLACE_MAX_BILLS_NUMBER})

        return cleaned_data


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PlaceResourceConversion(base_place_bill.BasePlaceBill):
    type = relations.BILL_TYPE.PLACE_RESOURCE_CONVERSION

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Изменение параметров города'
    DESCRIPTION = 'Устанавливает изменение параметров города, обычно, бонус к одним за счёт штрафа к другим. Один город может иметь не более %(max_exchanges)d активных договоров.' % {'max_exchanges': c.PLACE_MAX_BILLS_NUMBER}

    def __init__(self, conversion=None, **kwargs):
        super(PlaceResourceConversion, self).__init__(**kwargs)
        self.conversion = conversion

    def user_form_initials(self):
        data = super(PlaceResourceConversion, self).user_form_initials()
        data['conversion'] = self.conversion
        return data

    def initialize_with_form(self, user_form):
        super(PlaceResourceConversion, self).initialize_with_form(user_form)
        self.conversion = user_form.c.conversion

    def has_meaning(self):
        return True

    def apply(self, bill=None):
        if self.has_meaning():
            places_prototypes.ResourceExchangePrototype.create(place_1=self.place,
                                                               place_2=None,
                                                               resource_1=self.conversion.resource_from,
                                                               resource_2=self.conversion.resource_to,
                                                               bill=bill)

    def decline(self, bill):
        exchange = places_storage.resource_exchanges.get_exchange_for_bill_id(bill.id)
        if exchange:
            exchange.remove()

    def end(self, bill):
        exchange = places_storage.resource_exchanges.get_exchange_for_bill_id(bill.id)
        if exchange:
            exchange.remove()

    def serialize(self):
        data = super(PlaceResourceConversion, self).serialize()
        data['conversion'] = self.conversion.value
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PlaceResourceConversion, cls).deserialize(data)
        obj.conversion = CONVERSION.index_value[data['conversion']]
        return obj
