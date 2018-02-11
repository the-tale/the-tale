
from dext.forms import forms, fields

from utg import relations as utg_relations

from tt_logic.beings import relations as beings_relations
from tt_logic.artifacts import relations as tt_artifacts_relations

from the_tale.common.utils import bbcode

from the_tale.linguistics.forms import WordField

from the_tale.game import relations as game_relations

from the_tale.game.artifacts import objects as artifacts_objects
from the_tale.game.artifacts import relations as artifacts_relations

from the_tale.game.companions import relations

from the_tale.game.balance import constants as c

from the_tale.game.companions.abilities import forms as abilities_forms


class CompanionRecordForm(forms.Form):

    name = WordField(word_type=utg_relations.WORD_TYPE.NOUN, label='Название')

    max_health = fields.IntegerField(label='здоровье', min_value=c.COMPANIONS_MIN_HEALTH, max_value=c.COMPANIONS_MAX_HEALTH)

    type = fields.RelationField(label='тип', relation=beings_relations.TYPE)
    dedication = fields.RelationField(label='самоотверженность', relation=relations.DEDICATION)
    archetype = fields.RelationField(label='архетип', relation=game_relations.ARCHETYPE)
    mode = fields.RelationField(label='режим появления в игре', relation=relations.MODE)

    communication_verbal = fields.RelationField(label='вербальное общение', relation=beings_relations.COMMUNICATION_VERBAL)
    communication_gestures = fields.RelationField(label='невербальное общение', relation=beings_relations.COMMUNICATION_GESTURES)
    communication_telepathic = fields.RelationField(label='телепатия', relation=beings_relations.COMMUNICATION_TELEPATHIC)

    intellect_level = fields.RelationField(label='уровень интеллекта', relation=beings_relations.INTELLECT_LEVEL)

    abilities = abilities_forms.AbilitiesField(label='', required=False)

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

    description = bbcode.BBField(label='Описание', required=False)

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
    def get_initials(cls, companion):
        initials = {'description': companion.description,
                    'max_health': companion.max_health,
                    'type': companion.type,
                    'dedication': companion.dedication,
                    'archetype': companion.archetype,
                    'mode': companion.mode,
                    'abilities': companion.abilities,
                    'name': companion.utg_name,
                    'communication_verbal': companion.communication_verbal,
                    'communication_gestures': companion.communication_gestures,
                    'communication_telepathic': companion.communication_telepathic,
                    'intellect_level': companion.intellect_level,
                    'structure': companion.structure,
                    'features': list(companion.features),
                    'movement': companion.movement,
                    'body': companion.body,
                    'size': companion.size}

        for i, weapon in enumerate(companion.weapons, start=1):
            initials['weapon_{}'.format(i)] = weapon.type
            initials['material_{}'.format(i)] = weapon.material
            initials['power_type_{}'.format(i)] = weapon.power_type

        return initials
