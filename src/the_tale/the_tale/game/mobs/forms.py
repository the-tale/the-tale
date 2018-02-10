
from django.forms import ValidationError

from dext.forms import forms, fields

from utg import relations as utg_relations

from tt_logic.beings import relations as beings_relations
from tt_logic.artifacts import relations as tt_artifacts_relations

from the_tale.common.utils import bbcode

from the_tale.linguistics.forms import WordField

from the_tale.game.map.relations import TERRAIN

from the_tale.game import relations as game_relations

from the_tale.game.heroes.habilities import ABILITIES
from the_tale.game.heroes.habilities.battle import HIT

from the_tale.game.artifacts import objects as artifacts_objects
from the_tale.game.artifacts import relations as artifacts_relations

from . import logic


def to_ability(ability_id):
    return ABILITIES[ability_id]

ABILITY_CHOICES_DICT = dict((ability.get_id(), ability.NAME) for ability in logic.get_available_abilities())

ABILITY_CHOICES = sorted(ABILITY_CHOICES_DICT.items(), key=lambda choice: choice[1])

MOB_TYPE_CHOICES = sorted(beings_relations.TYPE.choices(), key=lambda choice: choice[1])


class MobRecordBaseForm(forms.Form):

    level = fields.IntegerField(label='минимальный уровень')

    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label='Название')

    type = fields.TypedChoiceField(label='тип', choices=MOB_TYPE_CHOICES, coerce=beings_relations.TYPE.get_from_name)
    archetype = fields.TypedChoiceField(label='тип', choices=game_relations.ARCHETYPE.choices(), coerce=game_relations.ARCHETYPE.get_from_name)

    global_action_probability = fields.FloatField(label='вероятность встретить монстра, если идёт его набег (от 0 до 1, 0 — нет набега)')

    terrains = fields.TypedMultipleChoiceField(label='места обитания', choices=TERRAIN.choices(), coerce=TERRAIN.get_from_name)

    abilities = fields.MultipleChoiceField(label='способности', choices=ABILITY_CHOICES)

    description = bbcode.BBField(label='Описание', required=False)

    is_mercenary = fields.BooleanField(label='может быть наёмником', required=False)
    is_eatable = fields.BooleanField(label='съедобный', required=False)

    communication_verbal = fields.RelationField(label='вербальное общение', relation=beings_relations.COMMUNICATION_VERBAL)
    communication_gestures = fields.RelationField(label='невербальное общение', relation=beings_relations.COMMUNICATION_GESTURES)
    communication_telepathic = fields.RelationField(label='телепатия', relation=beings_relations.COMMUNICATION_TELEPATHIC)

    intellect_level = fields.RelationField(label='уровень интеллекта', relation=beings_relations.INTELLECT_LEVEL)

    structure = fields.RelationField(label='структура', relation=beings_relations.STRUCTURE)
    features = fields.TypedMultipleChoiceField(label='особенности', choices=beings_relations.FEATURE.choices(), coerce=beings_relations.FEATURE.get_from_name)
    movement = fields.RelationField(label='способ передвижения', relation=beings_relations.MOVEMENT)
    body = fields.RelationField(label='телосложение', relation=beings_relations.BODY)
    size = fields.RelationField(label='размер', relation=beings_relations.SIZE)

    weapon_1 = fields.RelationField(label='оружие 1', relation=artifacts_relations.STANDARD_WEAPON)
    material_1 = fields.RelationField(label='материал оружия 1', relation=tt_artifacts_relations.MATERIAL)
    power_type_1 = fields.RelationField(label='тип силы оружия 1', relation=artifacts_relations.ARTIFACT_POWER_TYPE)

    weapon_2 = fields.RelationField(label='оружие 2', required=False, relation=artifacts_relations.STANDARD_WEAPON)
    material_2 = fields.RelationField(label='материал оружия 2', required=False, relation=tt_artifacts_relations.MATERIAL)
    power_type_2 = fields.RelationField(label='тип силы оружия 2', required=False, relation=artifacts_relations.ARTIFACT_POWER_TYPE)

    weapon_3 = fields.RelationField(label='оружие 3', required=False, relation=artifacts_relations.STANDARD_WEAPON)
    material_3 = fields.RelationField(label='материал оружия 3', required=False, relation=tt_artifacts_relations.MATERIAL)
    power_type_3 = fields.RelationField(label='тип силы оружия 3', required=False, relation=artifacts_relations.ARTIFACT_POWER_TYPE)

    def clean_abilities(self):
        abilities_ids = self.cleaned_data['abilities']

        if HIT.get_id() not in abilities_ids:
            abilities_ids.append(HIT.get_id())

        if not abilities_ids:
            raise ValidationError('не указаны способности монстра')

        for ability_id in abilities_ids:
            if ability_id not in ABILITY_CHOICES_DICT:
                raise ValidationError('неверный идентификатор способности монстра')

        return frozenset(abilities_ids)

    def clean_terrains(self):
        terrains = self.cleaned_data['terrains']

        if not terrains:
            raise ValidationError('не указаны места обитания монстра')

        return frozenset(terrains)

    def clean_features(self):
        features = self.cleaned_data['features']

        if not features:
            return frozenset()

        return frozenset(features)

    def get_weapons(self):
        weapons = []

        if self.c.weapon_1 and self.c.material_1 and self.c.power_type_1:
            weapons.append(artifacts_objects.Weapon(weapon=self.c.weapon_1, material=self.c.material_1, power_type=self.c.power_type_1))

        if self.c.weapon_2 and self.c.material_2 and self.c.power_type_2:
            weapons.append(artifacts_objects.Weapon(weapon=self.c.weapon_2, material=self.c.material_2, power_type=self.c.power_type_2))

        if self.c.weapon_3 and self.c.material_3 and self.c.power_type_3:
            weapons.append(artifacts_objects.Weapon(weapon=self.c.weapon_3, material=self.c.material_3, power_type=self.c.power_type_3))

        return weapons

    @classmethod
    def get_initials(cls, mob):
        initials = {'description': mob.description,
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
                    'intellect_level': mob.intellect_level,
                    'structure': mob.structure,
                    'features': list(mob.features),
                    'movement': mob.movement,
                    'body': mob.body,
                    'size': mob.size,
                    'is_mercenary': mob.is_mercenary,
                    'is_eatable': mob.is_eatable}

        for i, weapon in enumerate(mob.weapons, start=1):
            initials['weapon_{}'.format(i)] = weapon.type
            initials['material_{}'.format(i)] = weapon.material
            initials['power_type_{}'.format(i)] = weapon.power_type

        return initials


class MobRecordForm(MobRecordBaseForm):
    pass


class ModerateMobRecordForm(MobRecordBaseForm):

    approved = fields.BooleanField(label='одобрен', required=False)

    @classmethod
    def get_initials(cls, mob):
        initials = super(ModerateMobRecordForm, cls).get_initials(mob)
        initials.update({'uuid': mob.uuid,
                         'approved': mob.state.is_ENABLED})

        return initials
