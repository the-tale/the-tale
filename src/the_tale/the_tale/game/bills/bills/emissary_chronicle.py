
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    emissary = emissaries_fields.EmissaryField()

    def __init__(self, initiator_clan_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['emissary'].choices = emissaries_logic.form_choices(own_clan_id=initiator_clan_id)


class UserForm(BaseForm):
    pass


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


# TODO: в has_meaning проверять изменение города и имени эмиссара

class EmissaryChronicle(base_bill.BaseBill):
    type = relations.BILL_TYPE.EMISSARY_CHRONICLE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Запись в летописи об эмиссаре'
    DESCRIPTION = 'Занести в летопись интересное событие, произошедшее с эмиссаром. Если длина текста меньше 500 символов, к записи необходимо прикрепить фольклорный рассказ, раскрывающий тему. Для одного рассказа можно создать только одну запись.'

    def __init__(self, emissary_id=None,
                 old_place_name_forms=None,
                 origin_emissary_place_id=None,
                 origin_emissary_name=None):
        super().__init__()
        self.old_place_name_forms = old_place_name_forms
        self.emissary_id = emissary_id

        self.origin_emissary_name = origin_emissary_name
        self.origin_emissary_place_id = origin_emissary_place_id

        if self.emissary_id is not None:
            self.origin_emissary_name = self.emissary.name
            self.origin_emissary_place_id = self.emissary.place_id

        if self.old_place_name_forms is None and self.origin_emissary_place_id is not None:
            self.old_place_name_forms = places_storage.places[self.origin_emissary_place_id].utg_name

    @utils_decorators.lazy_property
    def emissary(self):
        return emissaries_storage.emissaries.get_or_load(self.emissary_id)

    @property
    def origin_place(self):
        return places_storage.places[self.origin_emissary_place_id]

    @property
    def place_name_changed(self):
        return self.old_place_name_forms != self.origin_place.utg_name

    def has_meaning(self):
        return (self.emissary and
                self.emissary.state.is_IN_GAME and
                self.emissary.place_id == self.origin_emissary_place_id and
                self.emissary.name == self.origin_emissary_name)

    @property
    def actors(self):
        return [self.origin_place, self.emissary]

    def apply(self, bill=None):
        pass

    def user_form_initials(self):
        return {'emissary': self.emissary_id}

    def initialize_with_form(self, user_form):
        del self.emissary

        self.emissary_id = int(user_form.c.emissary)

        self.origin_emissary_name = self.emissary.name
        self.origin_emissary_place_id = self.emissary.place_id

        self.old_place_name_forms = self.origin_place.utg_name

    @classmethod
    def get_user_form_create(cls, post=None, **kwargs):
        membership = clans_logic.get_membership(kwargs['owner_id'])
        clan_id = membership.clan_id if membership is not None else None
        return cls.UserForm(clan_id, post)

    def get_user_form_update(self, post=None, initial=None, original_bill_id=None, **kwargs):
        membership = clans_logic.get_membership(kwargs['owner_id'])
        clan_id = membership.clan_id if membership is not None else None

        if initial:
            return self.UserForm(clan_id, initial=initial, original_bill_id=original_bill_id)

        return self.UserForm(clan_id, post, original_bill_id=original_bill_id)

    def get_moderator_form_update(self, post=None, initial=None, original_bill_id=None, **kwargs):
        if initial:
            return self.ModeratorForm(None, initial=initial, original_bill_id=original_bill_id)

        return self.ModeratorForm(None, post, original_bill_id=original_bill_id)

    def serialize(self):
        return {'type': self.type.name.lower(),
                'emissary_id': self.emissary_id,
                'origin_emissary_place_id': self.origin_emissary_place_id,
                'origin_emissary_name': self.origin_emissary_name,
                'old_place_name_forms': self.old_place_name_forms.serialize()}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.emissary_id = data['emissary_id']
        obj.origin_emissary_name = data['origin_emissary_name']
        obj.origin_emissary_place_id = data['origin_emissary_place_id']

        obj.old_place_name_forms = utg_words.Word.deserialize(data['old_place_name_forms'])

        return obj
