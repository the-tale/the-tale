# coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields

from utg import relations as utg_relations

from the_tale.common.utils import bbcode

from the_tale.linguistics.forms import WordField

from the_tale.game.map.relations import TERRAIN

from the_tale.game import relations as game_relations

from the_tale.game.heroes.habilities import ABILITIES
from the_tale.game.heroes.habilities.battle import HIT



from the_tale.game.mobs.prototypes import MobRecordPrototype
from the_tale.game.mobs.relations import MOB_TYPE


def to_ability(ability_id):
    return ABILITIES[ability_id]

ABILITY_CHOICES_DICT = dict( (ability.get_id(), ability.NAME) for ability in MobRecordPrototype.get_available_abilities() )

ABILITY_CHOICES = sorted(ABILITY_CHOICES_DICT.items(), key=lambda choice: choice[1])

MOB_TYPE_CHOICES = sorted(MOB_TYPE.choices(), key=lambda choice: choice[1])


class MobRecordBaseForm(forms.Form):

    level = fields.IntegerField(label=u'минимальный уровень')

    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label=u'Название')

    type = fields.TypedChoiceField(label=u'тип', choices=MOB_TYPE_CHOICES, coerce=MOB_TYPE.get_from_name)
    archetype = fields.TypedChoiceField(label=u'тип', choices=game_relations.ARCHETYPE.choices(), coerce=game_relations.ARCHETYPE.get_from_name)

    global_action_probability = fields.FloatField(label=u'вероятность встретить монстра, если идёт его набег (от 0 до 1, 0 — нет набега)')

    terrains = fields.TypedMultipleChoiceField(label=u'места обитания', choices=TERRAIN.choices(), coerce=TERRAIN.get_from_name)

    abilities = fields.MultipleChoiceField(label=u'способности', choices=ABILITY_CHOICES)

    description = bbcode.BBField(label=u'Описание', required=False)

    communication_verbal = fields.RelationField(label=u'вербальное общение', relation=game_relations.COMMUNICATION_VERBAL, required=False)
    communication_gestures = fields.RelationField(label=u'невербальное общение', relation=game_relations.COMMUNICATION_GESTURES, required=False)
    communication_telepathic = fields.RelationField(label=u'телепатия', relation=game_relations.COMMUNICATION_TELEPATHIC, required=False)

    intellect_level = fields.RelationField(label=u'уровень интеллекта', relation=game_relations.INTELLECT_LEVEL)

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

    @classmethod
    def get_initials(cls, mob):
        return {'description': mob.description,
                'type': mob.type,
                'name': mob.utg_name,
                'archetype': mob.archetype,
                'level': mob.level,
                'global_action_probability': mob.global_action_probability,
                'terrains': mob.terrains,
                'abilities': mob.abilities,
                'communication_verbal': mob.communication_verbal,
                'communication_gestures': mob.communication_gestures,
                'communication_telepathic': mob.communication_telepathic,
                'intellect_level': mob.intellect_level}


class MobRecordForm(MobRecordBaseForm):
    pass

class ModerateMobRecordForm(MobRecordBaseForm):

    approved = fields.BooleanField(label=u'одобрен', required=False)

    @classmethod
    def get_initials(cls, mob):
        initials = super(ModerateMobRecordForm, cls).get_initials(mob)
        initials.update({'uuid': mob.uuid,
                         'approved': mob.state.is_ENABLED})

        return initials
