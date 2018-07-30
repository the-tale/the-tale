
import smart_imports

smart_imports.all()


class Empty(dext_forms.Form):

    def get_card_data(self):
        return {}


class Person(dext_forms.Form):
    value = dext_fields.ChoiceField(label='Мастер')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = persons_objects.Person.form_choices()

    def get_card_data(self):
        return {'value': int(self.c.value)}


class Place(dext_forms.Form):
    value = dext_fields.ChoiceField(label='Город')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = places_storage.places.get_choices()

    def get_card_data(self):
        return {'value': int(self.c.value)}


class Building(dext_forms.Form):
    value = dext_fields.ChoiceField(label='Строение')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = places_storage.buildings.get_choices()

    def get_card_data(self):
        return {'value': int(self.c.value)}


class CreateClan(dext_forms.Form):
    name = dext_fields.CharField(label='Название',
                                 max_length=clans_models.Clan.MAX_NAME_LENGTH,
                                 min_length=clans_models.Clan.MIN_NAME_LENGTH)
    abbr = dext_fields.CharField(label='Аббревиатура (до %d символов)' % clans_models.Clan.MAX_ABBR_LENGTH,
                                 max_length=clans_models.Clan.MAX_ABBR_LENGTH,
                                 min_length=clans_models.Clan.MIN_ABBR_LENGTH)

    def get_card_data(self):
        return {'name': self.c.name,
                'abbr': self.c.abbr}


class Upbringing(dext_forms.Form):
    value = dext_fields.RelationField(label='происхождение', relation=tt_beings_relations.UPBRINGING)

    def get_card_data(self):
        return {'value': int(self.c.value.value)}


class DeathAge(dext_forms.Form):
    value = dext_fields.RelationField(label='возраст смерти', relation=tt_beings_relations.AGE)

    def get_card_data(self):
        return {'value': int(self.c.value.value)}


class DeathType(dext_forms.Form):
    value = dext_fields.RelationField(label='способ первой смерти', relation=tt_beings_relations.FIRST_DEATH)

    def get_card_data(self):
        return {'value': int(self.c.value.value)}
