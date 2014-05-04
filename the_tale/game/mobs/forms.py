# coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields

from the_tale.common.utils.forms import SimpleWordField
from the_tale.common.utils import bbcode

from the_tale.game.map.relations import TERRAIN

from the_tale.game.heroes.habilities import ABILITIES
from the_tale.game.heroes.habilities.battle import HIT
from the_tale.game.heroes.relations import ARCHETYPE

from the_tale.game.mobs.models import MobRecord
from the_tale.game.mobs.prototypes import MobRecordPrototype
from the_tale.game.mobs.relations import MOB_TYPE


def to_ability(ability_id):
    return ABILITIES[ability_id]

ABILITY_CHOICES_DICT = dict( (ability.get_id(), ability.NAME) for ability in MobRecordPrototype.get_available_abilities() )

ABILITY_CHOICES = sorted(ABILITY_CHOICES_DICT.items(), key=lambda choice: choice[1])

MOB_TYPE_CHOICES = sorted(MOB_TYPE.choices(), key=lambda choice: choice[1])


class MobRecordBaseForm(forms.Form):

    level = fields.IntegerField(label=u'минимальный уровень')

    type = fields.TypedChoiceField(label=u'тип', choices=MOB_TYPE_CHOICES, coerce=MOB_TYPE.get_from_name)
    archetype = fields.TypedChoiceField(label=u'тип', choices=ARCHETYPE.choices(), coerce=ARCHETYPE.get_from_name)

    terrains = fields.TypedMultipleChoiceField(label=u'места обитания', choices=TERRAIN.choices(), coerce=TERRAIN.get_from_name)

    abilities = fields.MultipleChoiceField(label=u'способности', choices=ABILITY_CHOICES)

    description = bbcode.BBField(label=u'Описание', required=False)

    def clean_abilities(self):
        abilities_ids = self.cleaned_data['abilities']

        if HIT.get_id() not in abilities_ids:
            abilities_ids.append(HIT.get_id())

        if not abilities_ids:
            raise ValidationError(u'не указаны способности монстра')

        for ability_id in abilities_ids:
            if ability_id not in ABILITY_CHOICES_DICT:
                raise ValidationError(u'неверный идентификатор способности монстра')

        return frozenset(abilities_ids)

    def clean_terrains(self):

        terrains = self.cleaned_data['terrains']

        if not terrains:
            raise ValidationError(u'не указаны места обитания монстра')

        return frozenset(terrains)


class MobRecordForm(MobRecordBaseForm):

    name = fields.CharField(label=u'Название противника', max_length=MobRecord.MAX_NAME_LENGTH)


class ModerateMobRecordForm(MobRecordBaseForm):

    uuid = fields.CharField(label=u'уникальный идентификатор', max_length=MobRecord.MAX_NAME_LENGTH)

    name_forms = SimpleWordField(label=u'Формы названия')

    approved = fields.BooleanField(label=u'одобрен', required=False)
