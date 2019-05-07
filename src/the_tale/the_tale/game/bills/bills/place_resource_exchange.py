
import smart_imports

smart_imports.all()


ALLOWED_EXCHANGE_TYPES = [
    places_relations.RESOURCE_EXCHANGE_TYPE.NONE,

    places_relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_SMALL,
    places_relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_NORMAL,
    places_relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_LARGE,
    places_relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_EXTRA_LARGE,

    places_relations.RESOURCE_EXCHANGE_TYPE.SAFETY_SMALL,
    places_relations.RESOURCE_EXCHANGE_TYPE.SAFETY_NORMAL,
    places_relations.RESOURCE_EXCHANGE_TYPE.SAFETY_LARGE,
    places_relations.RESOURCE_EXCHANGE_TYPE.SAFETY_EXTRA_LARGE,

    places_relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_SMALL,
    places_relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_NORMAL,
    places_relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_LARGE,
    places_relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_EXTRA_LARGE,

    places_relations.RESOURCE_EXCHANGE_TYPE.CULTURE_SMALL,
    places_relations.RESOURCE_EXCHANGE_TYPE.CULTURE_NORMAL,
    places_relations.RESOURCE_EXCHANGE_TYPE.CULTURE_LARGE,
    places_relations.RESOURCE_EXCHANGE_TYPE.CULTURE_EXTRA_LARGE
]

ALLOWED_EXCHANGE_TYPES_CHOICES = [(record, record.text) for record in ALLOWED_EXCHANGE_TYPES]


class BaseForm(forms.BaseUserForm):
    place_1 = dext_fields.ChoiceField(label='Первый город')
    place_2 = dext_fields.ChoiceField(label='Второй город')

    resource_1 = dext_fields.TypedChoiceField(label='Ресурс от первого города', choices=ALLOWED_EXCHANGE_TYPES_CHOICES, coerce=places_relations.RESOURCE_EXCHANGE_TYPE.get_from_name)
    resource_2 = dext_fields.TypedChoiceField(label='Ресурс от второго города', choices=ALLOWED_EXCHANGE_TYPES_CHOICES, coerce=places_relations.RESOURCE_EXCHANGE_TYPE.get_from_name)

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place_1'].choices = places_storage.places.get_choices()
        self.fields['place_2'].choices = places_storage.places.get_choices()

    def clean(self):
        cleaned_data = super(BaseForm, self).clean()

        place_1 = places_storage.places.get(int(cleaned_data['place_1']))
        place_2 = places_storage.places.get(int(cleaned_data['place_2']))

        if (c.PLACE_MAX_BILLS_NUMBER <= len(places_storage.resource_exchanges.get_exchanges_for_place(place_1)) or
            c.PLACE_MAX_BILLS_NUMBER <= len(places_storage.resource_exchanges.get_exchanges_for_place(place_2))):
            raise django_forms.ValidationError('Один город может поддерживать не более чем {max_exchanges} активных записей в Книге Судьбы'.format(max_exchanges=c.PLACE_MAX_BILLS_NUMBER))

        resource_1 = cleaned_data.get('resource_1')
        resource_2 = cleaned_data.get('resource_2')

        if resource_1 is None:
            raise django_forms.ValidationError('Не указан ресурс от первого города')

        if resource_2 is None:
            raise django_forms.ValidationError('Не указан ресурс от второго города')

        if resource_1 not in ALLOWED_EXCHANGE_TYPES:
            raise django_forms.ValidationError('Нельзя заключить договор на обмен ресурса «%s»' % resource_1.text)

        if resource_2 not in ALLOWED_EXCHANGE_TYPES:
            raise django_forms.ValidationError('Нельзя заключить договор на обмен ресурса «%s»' % resource_2.text)

        if resource_1.parameter == resource_2.parameter:
            raise django_forms.ValidationError('Нельзя заключить договор на обмен одинаковыми ресурсами')

        return cleaned_data


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PlaceResourceExchange(base_bill.BaseBill):
    type = relations.BILL_TYPE.PLACE_RESOURCE_EXCHANGE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Обмен ресурсами между городами'
    DESCRIPTION = 'Налаживает обмен ресурсами между городами. Город, указанный вторым, будет тратить производство на поддержку караванов, пропорционально длинне минимального пути между ними (по клеткам, {production} производства за каждую). Город может иметь не более {max_exchanges} активных записей в Книге Судьбы. Обмен не обязан быть равноценным.'.format(
        max_exchanges=c.PLACE_MAX_BILLS_NUMBER,
        production=c.RESOURCE_EXCHANGE_COST_PER_CELL)

    def __init__(self, place_1_id=None, place_2_id=None, resource_1=None, resource_2=None, old_place_1_name_forms=None, old_place_2_name_forms=None):
        super(PlaceResourceExchange, self).__init__()
        self.place_1_id = place_1_id
        self.place_2_id = place_2_id
        self.resource_1 = resource_1
        self.resource_2 = resource_2
        self.old_place_1_name_forms = old_place_1_name_forms
        self.old_place_2_name_forms = old_place_2_name_forms

        if self.old_place_1_name_forms is None and self.place_1_id is not None:
            self.old_place_1_name_forms = self.place_1.utg_name

        if self.old_place_2_name_forms is None and self.place_2_id is not None:
            self.old_place_2_name_forms = self.place_2.utg_name

    @property
    def place_1(self):
        return places_storage.places[self.place_1_id]

    @property
    def place_2(self):
        return places_storage.places[self.place_2_id]

    @property
    def actors(self):
        return [self.place_1, self.place_2]

    def user_form_initials(self):
        return {'place_1': self.place_1_id,
                'place_2': self.place_2_id,
                'resource_1': self.resource_1,
                'resource_2': self.resource_2}

    @property
    def place_1_name_changed(self):
        return self.old_place_1_name != self.place_1.name

    @property
    def place_2_name_changed(self):
        return self.old_place_2_name != self.place_2.name

    @property
    def old_place_1_name(self):
        return self.old_place_1_name_forms.normal_form()

    @property
    def old_place_2_name(self):
        return self.old_place_2_name_forms.normal_form()

    def initialize_with_form(self, user_form):
        self.place_1_id = int(user_form.c.place_1)
        self.place_2_id = int(user_form.c.place_2)
        self.resource_1 = user_form.c.resource_1
        self.resource_2 = user_form.c.resource_2
        self.old_place_1_name_forms = self.place_1.utg_name
        self.old_place_2_name_forms = self.place_2.utg_name

    def has_meaning(self):
        if (c.PLACE_MAX_BILLS_NUMBER <= len(places_storage.resource_exchanges.get_exchanges_for_place(self.place_1)) or
            c.PLACE_MAX_BILLS_NUMBER <= len(places_storage.resource_exchanges.get_exchanges_for_place(self.place_2))):
            return False

        return True

    def apply(self, bill=None):
        if self.has_meaning():
            places_prototypes.ResourceExchangePrototype.create(place_1=self.place_1,
                                                               place_2=self.place_2,
                                                               resource_1=self.resource_1,
                                                               resource_2=self.resource_2,
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
        return {'type': self.type.name.lower(),
                'place_1_id': self.place_1_id,
                'place_2_id': self.place_2_id,
                'old_place_1_name_forms': self.old_place_1_name_forms.serialize(),
                'old_place_2_name_forms': self.old_place_2_name_forms.serialize(),
                'resource_1': self.resource_1.value,
                'resource_2': self.resource_2.value}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.place_1_id = data['place_1_id']
        obj.place_2_id = data['place_2_id']
        obj.old_place_1_name_forms = utg_words.Word.deserialize(data['old_place_1_name_forms'])
        obj.old_place_2_name_forms = utg_words.Word.deserialize(data['old_place_2_name_forms'])
        obj.resource_1 = places_relations.RESOURCE_EXCHANGE_TYPE.index_value[data['resource_1']]
        obj.resource_2 = places_relations.RESOURCE_EXCHANGE_TYPE.index_value[data['resource_2']]

        return obj
