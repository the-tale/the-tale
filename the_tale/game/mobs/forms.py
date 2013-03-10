# coding: utf-8

from django.forms import ValidationError

from textgen.words import Noun

from dext.forms import forms, fields

from common.utils import bbcode

from game.map.places.models import TERRAIN

from game.heroes.habilities import ABILITIES
from game.heroes.habilities.battle import HIT

from game.mobs.models import MobRecord
from game.mobs.prototypes import MobRecordPrototype


def to_ability(ability_id):
    return ABILITIES[ability_id]

ABILITY_CHOICES_DICT = dict( (ability.get_id(), ability.NAME) for ability in MobRecordPrototype.get_available_abilities() )

ABILITY_CHOICES = sorted(ABILITY_CHOICES_DICT.items(), key=lambda choice: choice[1])


class MobRecordBaseForm(forms.Form):

    level = fields.IntegerField(label=u'минимальный уровень')

    terrains = fields.TypedMultipleChoiceField(label=u'места обитания', choices=TERRAIN._CHOICES, coerce=int)

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

        for terrain_id in terrains:
            if terrain_id not in TERRAIN._ID_TO_STR:
                raise ValidationError(u'неверный идентификатор типа местости')

        return frozenset(terrains)


class MobRecordForm(MobRecordBaseForm):

    name = fields.CharField(label=u'Название противника', max_length=MobRecord.MAX_NAME_LENGTH)


class ModerateMobRecordForm(MobRecordBaseForm):

    uuid = fields.CharField(label=u'уникальный идентификатор', max_length=MobRecord.MAX_NAME_LENGTH)

    name_forms = fields.JsonField(label=u'Формы названия')

    approved = fields.BooleanField(label=u'одобрен', required=False)


    def clean_name_forms(self):
        data = self.cleaned_data['name_forms']

        noun = Noun.deserialize(data)

        if not noun.is_valid:
            raise ValidationError(u'неверное описание форм существительного')

        return noun
