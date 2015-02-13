# coding: utf-8

from django import forms as django_forms
from django.core.exceptions import ValidationError

import jinja2

from dext.forms import fields

from the_tale.game.companions.abilities import effects
from the_tale.game.companions.abilities import container
from the_tale.game.companions.abilities import relations

def ChoiceField(filter=lambda ability: True, sort_key=None):
    choices = [('', u'---')] + sorted([(ability, u'%s [%d]' % (ability.text, ability.rarity_delta))
                                       for ability in effects.ABILITIES.records
                                       if filter(ability)],
                                       key=sort_key)
    return fields.TypedChoiceField(label=u'', choices=choices, required=False, coerce=effects.ABILITIES.get_from_name)


def get_abilities_fields():
    def common_filter(ability):
        if ability.effect.TYPE.is_COHERENCE_SPEED:
            return False
        if ability.effect.TYPE.is_CHANGE_HABITS:
            return False
        return True

    sort_key = lambda x: x[1]
    return {
        relations.FIELDS.COHERENCE_SPEED: ChoiceField(filter=lambda ability: ability.effect.TYPE.is_COHERENCE_SPEED),
        relations.FIELDS.HONOR: ChoiceField(filter=lambda ability: ability.effect.TYPE.is_CHANGE_HABITS and ability.effect.habit_type.is_HONOR),
        relations.FIELDS.PEACEFULNESS: ChoiceField(filter=lambda ability: ability.effect.TYPE.is_CHANGE_HABITS and ability.effect.habit_type.is_PEACEFULNESS),
        relations.FIELDS.START_1: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.START_2: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.START_3: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.START_4: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.START_5: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.ABILITY_1: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.ABILITY_2: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.ABILITY_3: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.ABILITY_4: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.ABILITY_5: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.ABILITY_6: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.ABILITY_7: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.ABILITY_8: ChoiceField(filter=common_filter, sort_key=sort_key),
        relations.FIELDS.ABILITY_9: ChoiceField(filter=common_filter, sort_key=sort_key)
    }



def decompress_abilities(value):
    abilities_fields = get_abilities_fields()
    # keys = []

    decompressed = [None] * len(abilities_fields)

    if value is None:
        return decompressed

    decompressed[relations.FIELDS.COHERENCE_SPEED.value] = value.coherence
    decompressed[relations.FIELDS.HONOR.value] = value.honor
    decompressed[relations.FIELDS.PEACEFULNESS.value] = value.peacefulness

    for field, ability in zip((relations.FIELDS.START_1, relations.FIELDS.START_2, relations.FIELDS.START_3), value.start):
        decompressed[field.value] = ability

    for field, ability in zip((field for field in relations.FIELDS.records if field.common), value.common):
        decompressed[field.value] = ability

    return decompressed


class AbilitiesWidget(django_forms.MultiWidget):

    def __init__(self, **kwargs):
        abilities_fields = get_abilities_fields()
        super(AbilitiesWidget, self).__init__(widgets=[abilities_fields[key].widget for key in relations.FIELDS.records], **kwargs)

    def decompress(self, value):
        return decompress_abilities(value)

    def format_output(self, rendered_widgets):
        from dext.jinja2 import render
        return jinja2.Markup(render.template('companions/abilities/abilities_field.html', context={'widgets': rendered_widgets,
                                                                                                   'FIELDS': relations.FIELDS}))



@fields.pgf
class AbilitiesField(django_forms.MultiValueField):

    def __init__(self, **kwargs):
        abilities_fields = get_abilities_fields()
        super(AbilitiesField, self).__init__(fields=[abilities_fields[key] for key in relations.FIELDS.records], widget=AbilitiesWidget(), **kwargs)

    def clean(self, value):
        cleaned_value = super(AbilitiesField, self).clean(value)

        if cleaned_value.has_duplicates():
            raise ValidationError(u'В описании особенностей спутника есть дубликат')

        if cleaned_value.has_same_effects():
            raise ValidationError(u'В описании особенностей спутника есть несколько способностей с одним эффектом')

        return cleaned_value

    def compress(self, data_list):
        common = list()
        start = set()
        coherence = None
        honor = None
        peacefulness = None

        for field, ability in zip(relations.FIELDS.records, data_list):
            if ability is u'':
                continue

            if field in (relations.FIELDS.START_1, relations.FIELDS.START_2, relations.FIELDS.START_3):
                start.add(ability)

            elif field.is_COHERENCE_SPEED:
                coherence = ability

            elif field.is_HONOR:
                honor = ability

            elif field.is_PEACEFULNESS:
                peacefulness = ability

            elif ability:
                common.append(ability)

        return container.Container(common=common,
                                   start=start,
                                   coherence=coherence,
                                   honor=honor,
                                   peacefulness=peacefulness)
