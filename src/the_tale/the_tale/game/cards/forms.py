
from dext.forms import forms
from dext.forms import fields

from the_tale.accounts.clans import models as clan_models

from the_tale.game.places import storage as places_storage
from the_tale.game.persons import objects as persons_objects


class Empty(forms.Form):

    def get_card_data(self):
        return {}


class Person(forms.Form):
    value = fields.ChoiceField(label='Мастер')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = persons_objects.Person.form_choices()

    def get_card_data(self):
        return {'value': int(self.c.value)}


class Place(forms.Form):
    value = fields.ChoiceField(label='Город')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = places_storage.places.get_choices()

    def get_card_data(self):
        return {'value': int(self.c.value)}


class Building(forms.Form):
    value = fields.ChoiceField(label='Строение')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = places_storage.buildings.get_choices()

    def get_card_data(self):
        return {'value': int(self.c.value)}


class CreateClan(forms.Form):
    name = fields.CharField(label='Название',
                            max_length=clan_models.Clan.MAX_NAME_LENGTH,
                            min_length=clan_models.Clan.MIN_NAME_LENGTH)
    abbr = fields.CharField(label='Аббревиатура (до %d символов)' % clan_models.Clan.MAX_ABBR_LENGTH,
                            max_length=clan_models.Clan.MAX_ABBR_LENGTH,
                            min_length=clan_models.Clan.MIN_ABBR_LENGTH)

    def get_card_data(self):
        return {'name': self.c.name,
                'abbr': self.c.abbr}
