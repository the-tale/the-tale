
from django import forms as django_forms

from dext.forms import forms
from dext.forms import fields
from dext.common import utils as dext_utils

from the_tale.game import relations as game_relations
from the_tale.game.places import storage as places_storage
from the_tale.game.persons import objects as persons_objects
from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.mobs import storage as mobs_storage


def form(preference):

    name = preference.text
    name = name[0].upper()+name[1:]

    class Preference(forms.Form):
        PREFERENCE = preference
        value = fields.ChoiceField(required=False)

        def __init__(self, *args, **kwargs):
            self.hero = kwargs.pop('hero')
            super().__init__(*args, **kwargs)
            self.fields['value'].label = name

        def get_card_data(self):
            return {'value': int(self.c.value) if self.c.value else None}

        def clean_value(self):
            value = self.cleaned_data['value']

            if not value and self.hero.preferences._get(preference) is None:
                raise django_forms.ValidationError('Предпочтение уже сброшено.')

            if value and value == self.hero.preferences._get(preference):
                raise django_forms.ValidationError('Нельзя заменить предпочтение на то же самое.')

            return value


    return Preference


class Mob(form(heroes_relations.PREFERENCE_TYPE.MOB)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mobs = mobs_storage.mobs_storage.get_available_mobs_list(level=self.hero.level, terrain=None, mercenary=None)
        self.fields['value'].choices = [(None, 'забыть предпочтение')] + [(mob.id, mob.name) for mob in mobs]


class Hometown(form(heroes_relations.PREFERENCE_TYPE.PLACE)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = [(None, 'забыть предпочтение')] + places_storage.places.get_choices()


class Friend(form(heroes_relations.PREFERENCE_TYPE.FRIEND)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = [(None, 'забыть предпочтение')] + persons_objects.Person.form_choices()

    def clean_value(self):
        value = super().clean_value()

        if value and self.hero.preferences.enemy and self.hero.preferences.enemy.id == int(value):
            raise django_forms.ValidationError('Мастер уже выбран противником героя и не может стать его соратником.')

        return value


class Enemy(form(heroes_relations.PREFERENCE_TYPE.ENEMY)):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = [(None, 'забыть предпочтение')] + persons_objects.Person.form_choices()

    def clean_value(self):
        value = super().clean_value()

        if value and self.hero.preferences.friend and self.hero.preferences.friend.id == int(value):
            raise django_forms.ValidationError('Мастер уже выбран соратником героя и не может стать его противником.')

        return value


class RelationMixin:
    def get_card_data(self):
        return {'value': self.c.value.value if self.c.value else None}


class EnergyRegenerationType(RelationMixin, form(heroes_relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE)):
    value = fields.RelationField(relation=heroes_relations.ENERGY_REGENERATION)


class EquipmentSlot(RelationMixin, form(heroes_relations.PREFERENCE_TYPE.EQUIPMENT_SLOT)):
    value = fields.RelationField(relation=heroes_relations.EQUIPMENT_SLOT, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value'].choices = [(None, 'забыть предпочтение')] + self.fields['value'].choices[1:]


class RiskLevel(RelationMixin, form(heroes_relations.PREFERENCE_TYPE.RISK_LEVEL)):
    value = fields.RelationField(relation=heroes_relations.RISK_LEVEL)


class FavoriteItem(RelationMixin, form(heroes_relations.PREFERENCE_TYPE.FAVORITE_ITEM)):
    value = fields.RelationField(relation=heroes_relations.EQUIPMENT_SLOT, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['value'].choices = [(None, 'забыть предпочтение')]

        for slot in heroes_relations.EQUIPMENT_SLOT.records:
            artifact = self.hero.equipment.get(slot)

            if artifact is None:
                continue

            self.fields['value'].choices.append((slot, artifact.name))


class Archetype(RelationMixin, form(heroes_relations.PREFERENCE_TYPE.ARCHETYPE)):
    value = fields.RelationField(relation=game_relations.ARCHETYPE)


class CompanionDedication(RelationMixin, form(heroes_relations.PREFERENCE_TYPE.COMPANION_DEDICATION)):
    value = fields.RelationField(relation=heroes_relations.COMPANION_DEDICATION)


class CompanionEmpathy(RelationMixin, form(heroes_relations.PREFERENCE_TYPE.COMPANION_EMPATHY)):
    value = fields.RelationField(relation=heroes_relations.COMPANION_EMPATHY)


FORMS = {form_class.PREFERENCE: form_class
         for form_class in dext_utils.discovering.discover_classes(globals().values(), forms.Form)}
